"""Simple REPL fallback for the DB client."""
import asyncio
import json
import connections as connections
import wal as wal
import tx_manager as tx_manager
from adapters.postgres_adapter import PostgresAdapter
from adapters.mongo_adapter import MongoAdapter
from urllib.parse import urlparse
import sqlparse
from sqlparse.sql import Where, Identifier, IdentifierList
from sqlparse.tokens import Keyword, DML, Name


def _parse_wal_filters(args):
    filters = {"tid": None, "since": None, "until": None}
    for arg in args:
        if "=" not in arg:
            continue
        key, value = arg.split("=", 1)
        key = key.lower().strip()
        value = value.strip()
        if key in filters and value:
            filters[key] = value
    return filters


async def repl_loop():
    print("DBClient REPL. Type 'help' for commands.")
    tx_mgr = tx_manager.TxManager()
    current_tid = None
    adapter_cache = {}
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("Exiting REPL.")
            return
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]
        if cmd in ("quit", "exit"):
            return
        if cmd == "help":
            print("Commands: connections, addconn, rmconn, use, active, begin, commit, abort, sql, wal, quit")
            print("WAL filters: wal tid=<TID> since=<ISO> until=<ISO>")
            continue
        if cmd == "connections":
            for c in connections.list_connections():
                print(c)
            continue
        if cmd == "addconn":
            if len(args) < 3:
                print("usage: addconn NAME ENGINE URI")
                continue
            name, engine, uri = args[0], args[1], args[2]
            connections.add_connection(name, engine, uri)
            print("added")
            continue
        if cmd == "rmconn":
            if len(args) < 1:
                print("usage: rmconn NAME")
                continue
            ok = connections.remove_connection(args[0])
            print("removed" if ok else "not found")
            continue
        if cmd == "begin":
            tid = await tx_mgr.begin()
            current_tid = tid
            print("began", tid)
            continue
        if cmd == "commit":
            if not current_tid:
                print("no active transaction")
                continue
            await tx_mgr.commit(current_tid)
            print("committed", current_tid)
            current_tid = None
            continue
        if cmd == "abort":
            if not current_tid:
                print("no active transaction")
                continue
            await tx_mgr.abort(current_tid)
            print("aborted", current_tid)
            current_tid = None
            continue
        if cmd == "sql":
            # preserve original SQL (may contain spaces)
            sql = line[len("sql") :].strip()
            if not sql:
                print("usage: sql <SQL or mongo command>")
                continue
            active = connections.get_active_connection()
            if not active:
                print("no active connection")
                continue
            engine = active.get("engine")
            uri = active.get("uri")
            try:
                if engine and engine.startswith("postgres"):
                    pg = adapter_cache.get(("postgres", uri))
                    if pg is None:
                        pg = PostgresAdapter(uri)
                        adapter_cache[("postgres", uri)] = pg
                    verb = sql.strip().split()[0].lower()
                    if verb in ("select", "with"):
                        rows = await pg.execute(sql)
                        for r in rows:
                            print(dict(r))
                    elif verb in ("insert", "update", "delete"):
                        # capture before/after images and write-ahead log
                        before = None
                        after = None
                        # INSERT: no before, use RETURNING * to get after
                        if verb == "insert":
                            try:
                                q = sql
                                if "returning" not in sql.lower():
                                    q = sql.rstrip().rstrip(";") + " RETURNING *;"
                                rows = await pg.execute(q)
                                after = [dict(r) for r in rows]
                                before = []
                            except Exception as e:
                                print("execution error:", e)
                                continue
                        else:
                            # try to extract table and WHERE clause for before image.
                            # Use a permissive parsing strategy:
                            # - strip RETURNING for parsing
                            # - split on WHERE (case-insensitive) to get table part and predicate
                            tbl = None
                            where = None
                            # remove trailing RETURNING clause if present (case-insensitive)
                            low_sql = sql.lower()
                            if "returning" in low_sql:
                                idx = low_sql.find("returning")
                                sql_no_return = sql[:idx]
                            else:
                                sql_no_return = sql
                            # Use sqlparse to extract table and WHERE clause robustly
                            tbl = None
                            where = None
                            try:
                                parsed = sqlparse.parse(sql_no_return)
                                if parsed:
                                    stmt = parsed[0]
                                    # extract WHERE token if present
                                    where_token = None
                                    for t in stmt.tokens:
                                        if isinstance(t, Where):
                                            where_token = t
                                            break
                                    if where_token:
                                        # where_token.value includes leading 'WHERE'
                                        where = where_token.value[len("WHERE"):].strip().rstrip(";").strip()
                                    # extract table for UPDATE and DELETE
                                    if verb == "update":
                                        # find Identifier after UPDATE
                                        seen_update = False
                                        for t in stmt.tokens:
                                            if t.ttype is DML and t.value.upper() == "UPDATE":
                                                seen_update = True
                                                continue
                                            if seen_update:
                                                if isinstance(t, Identifier):
                                                    tbl = t.get_name()
                                                    break
                                                # IdentifierList or plain Name token
                                                if isinstance(t, IdentifierList):
                                                    # take first identifier
                                                    for idn in t.get_identifiers():
                                                        tbl = idn.get_name()
                                                        break
                                                    if tbl:
                                                        break
                                                if t.ttype is Name:
                                                    tbl = t.value
                                                    break
                                    elif verb == "delete":
                                        # find Identifier after FROM
                                        seen_from = False
                                        for t in stmt.tokens:
                                            if t.ttype is Keyword and t.value.upper() == "FROM":
                                                seen_from = True
                                                continue
                                            if seen_from:
                                                if isinstance(t, Identifier):
                                                    tbl = t.get_name()
                                                    break
                                                if isinstance(t, IdentifierList):
                                                    for idn in t.get_identifiers():
                                                        tbl = idn.get_name()
                                                        break
                                                    if tbl:
                                                        break
                                                if t.ttype is Name:
                                                    tbl = t.value
                                                    break
                            except Exception as e:
                                print("sqlparse error:", e)

                            # ensure a DB transaction is started for this logical TID so we can safely SELECT ... FOR UPDATE
                            if current_tid:
                                existing = tx_mgr.get_adapter_tx(current_tid, "postgres")
                                if not existing:
                                    try:
                                        txobj = await pg.begin_transaction()
                                        await tx_mgr.attach_adapter_tx(current_tid, "postgres", pg, txobj)
                                    except Exception:
                                        pass

                            if tbl and where:
                                try:
                                    # use FOR UPDATE when inside a transaction to lock rows
                                    if current_tid:
                                        sel = f"SELECT * FROM {tbl} WHERE {where} FOR UPDATE;"
                                    else:
                                        sel = f"SELECT * FROM {tbl} WHERE {where};"
                                    brow = await pg.execute(sel)
                                    before = [dict(r) for r in brow]
                                except Exception:
                                    before = []
                            else:
                                # couldn't parse table/where; record empty before image
                                before = []
                            # Execute the operation and capture after images via RETURNING *
                            try:
                                q = sql
                                if "returning" not in sql.lower():
                                    q = sql.rstrip().rstrip(";") + " RETURNING *;"
                                rows = await pg.execute(q)
                                after = [dict(r) for r in rows]
                                # For DELETE, RETURNING returns the deleted rows (i.e. the before image).
                                # Normalize images: before should contain pre-existing rows, after should be empty.
                                if verb == "delete":
                                    if not before:
                                        # if we didn't capture before via SELECT, use RETURNING rows as before
                                        before = after
                                    after = []
                            except Exception as e:
                                print("execution error:", e)
                                continue

                        # write WAL entry
                        entry = {
                            "tid": current_tid,
                            "op": verb.upper(),
                            "engine": "postgres",
                            "query": sql,
                            "before": before,
                            "after": after,
                        }
                        try:
                            await wal.append(entry)
                        except Exception:
                            # fallback to tx_mgr logging if wal.append fails
                            await tx_mgr.log_op(current_tid or "NO_TID", verb.upper(), engine, before, after, sql)
                        # print a concise result
                        print(f"{verb.upper()} affected, before_count={len(before) if before is not None else 'unknown'}, after_count={len(after) if after is not None else 'unknown'}")
                    else:
                        # other statements
                        try:
                            res = await pg.execute_non_query(sql)
                            print(res)
                        except Exception as e:
                            print("execution error:", e)
                        if current_tid:
                            await tx_mgr.log_op(current_tid, "WRITE", engine, None, None, sql)
                elif engine and engine.startswith("mongo"):
                    # mongo command forms:
                    # 1) sql <op> <db> <coll> [json]
                    # 2) sql <op> <coll> [json]  (uses db from URI if present)
                    parts = sql.split(None, 3)
                    op = parts[0].lower()
                    # determine default DB from URI path if available
                    parsed = urlparse(uri)
                    default_db = None
                    if parsed.path and parsed.path not in ("/", ""):
                        default_db = parsed.path.lstrip("/")

                    db = None
                    coll = None
                    payload = {}

                    if len(parts) >= 3:
                        # Two possible shapes when there are 3 tokens:
                        # - op db coll
                        # - op coll payload   (short form using default DB from URI, payload is JSON)
                        third = parts[2].lstrip()
                        if third.startswith("{") or third.startswith("["):
                            # short form with JSON payload: op coll payload
                            if not default_db:
                                print("mongo usage: sql <op> <db> <coll> [json] (or include DB in URI)")
                                continue
                            db = default_db
                            coll = parts[1]
                            try:
                                payload = json.loads(parts[2])
                            except Exception as e:
                                print("invalid json payload:", e)
                                continue
                        else:
                            # assume op db coll [json]
                            db = parts[1]
                            coll = parts[2]
                            if len(parts) == 4:
                                try:
                                    payload = json.loads(parts[3])
                                except Exception as e:
                                    print("invalid json payload:", e)
                                    continue
                    elif len(parts) == 2:
                        # short form without payload: op coll (uses DB from URI)
                        if not default_db:
                            print("mongo usage: sql <op> <db> <coll> [json] (or include DB in URI)")
                            continue
                        db = default_db
                        coll = parts[1]
                    else:
                        print("mongo usage: sql <op> <db> <coll> [json]")
                        continue

                    mg = adapter_cache.get(("mongo", uri))
                    if mg is None:
                        mg = MongoAdapter(uri)
                        adapter_cache[("mongo", uri)] = mg
                    client = await mg.connect()
                    if op == "find":
                        rows = await client[db][coll].find(payload).to_list(length=100)
                        for r in rows:
                            print(r)
                    elif op == "insert":
                        docs = payload if isinstance(payload, list) else [payload]
                        res = await client[db][coll].insert_many(docs)
                        print("inserted_ids:", res.inserted_ids)
                        if current_tid:
                            await tx_mgr.log_op(current_tid, "WRITE", engine, None, None, f"insert {db}.{coll}")
                    elif op == "update":
                        # payload should be {"filter":..., "update":...}
                        flt = payload.get("filter", {})
                        upd = payload.get("update", {})
                        res = await client[db][coll].update_many(flt, upd)
                        print("matched:", res.matched_count, "modified:", res.modified_count)
                        if current_tid:
                            await tx_mgr.log_op(current_tid, "WRITE", engine, None, None, f"update {db}.{coll}")
                    elif op == "delete":
                        flt = payload
                        res = await client[db][coll].delete_many(flt)
                        print("deleted:", res.deleted_count)
                        if current_tid:
                            await tx_mgr.log_op(current_tid, "WRITE", engine, None, None, f"delete {db}.{coll}")
                    else:
                        print("unsupported mongo op:", op)
                else:
                    print("unsupported engine:", engine)
            except Exception as e:
                print("execution error:", e)
            continue
        if cmd == "use":
            if len(args) < 1:
                print("usage: use NAME")
                continue
            ok = connections.set_active(args[0])
            print("active set" if ok else "not found")
            continue
        if cmd == "active":
            cur = connections.get_active_connection()
            if cur:
                print("Active:", cur)
            else:
                print("No active connection")
            continue
        if cmd == "wal":
            filters = _parse_wal_filters(args)
            rows = wal.query(
                tid=filters["tid"],
                since=filters["since"],
                until=filters["until"],
            )
            for r in rows[-20:]:
                print(r)
            continue
        print("unknown command")
