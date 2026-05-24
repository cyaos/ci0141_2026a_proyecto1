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
from recovery.recovery_manager import RecoveryManager, NOMBRES_VALIDOS
from recovery.failure_simulator import simular_fallo


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
    recovery_mgr = RecoveryManager()

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
            print("Recuperación: protocolo [nombre], simular_fallo, recuperar")
            print("  protocolos: no_undo_no_redo | no_undo_redo | undo_no_redo | undo_redo")
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
            # El protocolo aplica operaciones diferidas (No-Undo) antes del COMMIT
            await recovery_mgr.activo.on_commit(current_tid)
            await tx_mgr.commit(current_tid)
            print("committed", current_tid)
            current_tid = None
            continue
        if cmd == "abort":
            if not current_tid:
                print("no active transaction")
                continue
            # El protocolo aplica UNDO si corresponde (Undo protocols)
            await recovery_mgr.activo.on_abort(current_tid)
            await tx_mgr.abort(current_tid)
            print("aborted", current_tid)
            current_tid = None
            continue

        # ── Comandos de recuperación ──────────────────────────────────────────
        if cmd == "protocolo":
            if not args:
                print("Protocolo activo:", recovery_mgr.protocolo_activo())
                print("Disponibles:", ", ".join(NOMBRES_VALIDOS))
            else:
                nombre = args[0].lower()
                if recovery_mgr.seleccionar(nombre):
                    print("Protocolo cambiado a:", nombre)
                else:
                    print("Protocolo desconocido. Disponibles:", ", ".join(NOMBRES_VALIDOS))
            continue

        if cmd == "simular_fallo":
            if not current_tid:
                print("no hay transacción activa")
                continue
            await simular_fallo(current_tid, tx_mgr)
            print(f"Fallo simulado en transacción {current_tid}")
            print("La TX quedó interrumpida (sin COMMIT ni ABORT) en el WAL.")
            current_tid = None
            continue

        if cmd == "recuperar":
            entradas_wal = wal.query()
            active = connections.get_active_connection()
            adaptadores = {}
            if active:
                engine_activo = active.get("engine", "")
                uri_activo = active.get("uri", "")
                if engine_activo.startswith("postgres"):
                    pg = adapter_cache.get(("postgres", uri_activo))
                    if pg is None:
                        pg = PostgresAdapter(uri_activo)
                        adapter_cache[("postgres", uri_activo)] = pg
                    adaptadores["postgres"] = pg
                elif engine_activo.startswith("mongo"):
                    mg = adapter_cache.get(("mongo", uri_activo))
                    if mg is None:
                        mg = MongoAdapter(uri_activo)
                        adapter_cache[("mongo", uri_activo)] = mg
                    adaptadores["mongo"] = mg
            reporte = await recovery_mgr.activo.recover(entradas_wal, adaptadores)
            print(reporte)
            continue

        # ── Comando sql ───────────────────────────────────────────────────────
        if cmd == "sql":
            # preserve original SQL (may contain spaces)
            sql = line[len("sql"):].strip()
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
                        # Delegar al protocolo activo: él decide si ejecuta ahora o bufferiza
                        try:
                            before, after = await recovery_mgr.activo.on_write(
                                current_tid or "NO_TID", verb.upper(), "postgres", sql, pg
                            )
                        except Exception as e:
                            print("execution error:", e)
                            continue
                        if after is None:
                            print(f"{verb.upper()} bufferizado (protocolo: {recovery_mgr.protocolo_activo()}; se aplicará en COMMIT)")
                        else:
                            bc = len(before) if before is not None else "desconocido"
                            ac = len(after) if after is not None else "desconocido"
                            print(f"{verb.upper()} ejecutado, before_count={bc}, after_count={ac}")
                    else:
                        # other statements (CREATE, DROP, etc.)
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
            for r in rows:
                print(r)
            continue
        print("unknown command")
