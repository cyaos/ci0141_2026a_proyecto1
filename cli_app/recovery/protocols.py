"""Implementación de los 4 protocolos de recuperación ante fallos."""
from abc import ABC, abstractmethod
from typing import Optional
import re
import sqlparse
from sqlparse.sql import Where
import wal as wal_module
from recovery.reporte import ReporteRecuperacion


# ─── Helpers de parseo SQL ────────────────────────────────────────────────────

def _extraer_verbo(sql: str) -> str:
    partes = sql.strip().split()
    return partes[0].lower() if partes else ''


def _extraer_tabla(sql: str, verbo: str) -> Optional[str]:
    """Extrae el nombre de tabla de una sentencia INSERT/UPDATE/DELETE mediante regex."""
    try:
        sql_limpio = sql.strip()
        if verbo == 'insert':
            m = re.match(r'INSERT\s+INTO\s+(\w+)', sql_limpio, re.IGNORECASE)
        elif verbo == 'update':
            m = re.match(r'UPDATE\s+(\w+)', sql_limpio, re.IGNORECASE)
        elif verbo == 'delete':
            m = re.match(r'DELETE\s+FROM\s+(\w+)', sql_limpio, re.IGNORECASE)
        else:
            return None
        return m.group(1) if m else None
    except Exception:
        return None


def _extraer_where(sql: str) -> Optional[str]:
    """Extrae el predicado WHERE de una sentencia SQL (sin la palabra WHERE)."""
    # eliminar RETURNING si existe antes de parsear
    low = sql.lower()
    if 'returning' in low:
        sql = sql[:low.find('returning')]
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return None
        stmt = parsed[0]
        for t in stmt.tokens:
            if isinstance(t, Where):
                # Where.value empieza con 'WHERE '
                return t.value[5:].strip().rstrip(';').strip()
    except Exception:
        pass
    return None


# ─── Helpers para SQL de UNDO ─────────────────────────────────────────────────

def _val_sql(val) -> str:
    """Convierte un valor Python a literal SQL seguro para comparaciones."""
    if val is None:
        return 'NULL'
    if isinstance(val, bool):
        return 'TRUE' if val else 'FALSE'
    if isinstance(val, (int, float)):
        return str(val)
    return "'" + str(val).replace("'", "''") + "'"


def _where_de_fila(fila: dict) -> str:
    partes = []
    for col, val in fila.items():
        partes.append(f"{col} IS NULL" if val is None else f"{col} = {_val_sql(val)}")
    return ' AND '.join(partes) if partes else 'TRUE'


def _set_de_fila(fila: dict) -> str:
    return ', '.join(f"{col} = {_val_sql(val)}" for col, val in fila.items())


def _insert_de_fila(tabla: str, fila: dict) -> str:
    cols = ', '.join(str(k) for k in fila.keys())
    vals = ', '.join(_val_sql(v) for v in fila.values())
    return f"INSERT INTO {tabla} ({cols}) VALUES ({vals})"


def _sqls_undo(op: str, tabla: str, before_rows: list, after_rows: list) -> list:
    """Genera las sentencias SQL necesarias para deshacer una operación DML."""
    op = op.upper()
    if op == 'INSERT':
        # deshacer un INSERT = DELETE de las filas que se insertaron
        return [f"DELETE FROM {tabla} WHERE {_where_de_fila(r)}" for r in (after_rows or [])]
    elif op == 'UPDATE':
        # deshacer un UPDATE = restaurar los valores anteriores
        sqls = []
        for b, a in zip(before_rows or [], after_rows or []):
            sqls.append(f"UPDATE {tabla} SET {_set_de_fila(b)} WHERE {_where_de_fila(a)}")
        return sqls
    elif op == 'DELETE':
        # deshacer un DELETE = re-insertar las filas eliminadas
        return [_insert_de_fila(tabla, r) for r in (before_rows or [])]
    return []


# ─── Helpers de ejecución en Postgres ─────────────────────────────────────────

async def _capturar_before_pg(adapter, tabla: str, where: Optional[str]) -> list:
    """Captura la imagen anterior de filas que van a ser modificadas/eliminadas."""
    if not tabla or not where:
        return []
    try:
        rows = await adapter.execute(f"SELECT * FROM {tabla} WHERE {where};")
        return [dict(r) for r in rows]
    except Exception:
        return []


async def _ejecutar_dml_pg(adapter, sql: str, verbo: str, tabla: Optional[str],
                            where: Optional[str]) -> tuple:
    """
    Ejecuta un DML en Postgres. Retorna (before, after).
    Para protocolos Undo: se llama antes del commit, aplica inmediatamente.
    """
    before = []
    after = []

    if verbo == 'insert':
        q = sql.rstrip().rstrip(';')
        if 'returning' not in sql.lower():
            q += ' RETURNING *'
        rows = await adapter.execute(q + ';')
        after = [dict(r) for r in rows] if rows else []

    elif verbo in ('update', 'delete'):
        # capturar imagen previa
        before = await _capturar_before_pg(adapter, tabla, where)
        q = sql.rstrip().rstrip(';')
        if 'returning' not in sql.lower():
            q += ' RETURNING *'
        rows = await adapter.execute(q + ';')
        returned = [dict(r) for r in rows] if rows else []
        if verbo == 'delete':
            # RETURNING * en DELETE devuelve las filas eliminadas (= before si no capturamos)
            if not before:
                before = returned
            after = []
        else:
            after = returned

    return before, after


async def _ejecutar_undo_pg(adapter, sqls_undo: list) -> list:
    """Ejecuta sentencias de UNDO contra Postgres. Retorna lista de resultados."""
    resultados = []
    for sql in sqls_undo:
        try:
            await adapter.execute_non_query(sql + ';')
            resultados.append({'sql': sql, 'ok': True})
        except Exception as e:
            resultados.append({'sql': sql, 'ok': False, 'error': str(e)})
    return resultados


async def _ejecutar_redo_pg(adapter, sql: str) -> dict:
    """Re-ejecuta una sentencia DML original para REDO."""
    try:
        await adapter.execute_non_query(sql if sql.endswith(';') else sql + ';')
        return {'sql': sql, 'ok': True}
    except Exception as e:
        return {'sql': sql, 'ok': False, 'error': str(e)}


# ─── Clase base abstracta ─────────────────────────────────────────────────────

class RecoveryProtocol(ABC):
    nombre: str

    def __init__(self, pg_adapter, mongo_adapter):
        self.pg = pg_adapter
        self.mongo = mongo_adapter
        # buffer de escrituras diferidas: {tid: [{'op', 'sql', 'engine', 'adapter', 'tabla'}]}
        self.buffer: dict = {}
        # adaptadores usados por TID (para on_commit/on_abort sin parámetro adapter)
        self._adaptadores: dict = {}

    def _guardar_adapter(self, tid: str, adapter):
        self._adaptadores[tid] = adapter

    def _adapter_de(self, tid: str):
        return self._adaptadores.get(tid) or self.pg

    def _limpiar_tid(self, tid: str):
        self.buffer.pop(tid, None)
        self._adaptadores.pop(tid, None)

    @abstractmethod
    async def on_write(self, tid: str, op: str, engine: str, sql: str, adapter) -> tuple:
        """
        Maneja una escritura durante operación normal.
        Retorna (before, after) para mostrar al usuario.
        """

    @abstractmethod
    async def on_commit(self, tid: str) -> None:
        """Se llama cuando el usuario ejecuta COMMIT (antes de que tx_mgr escriba COMMIT)."""

    @abstractmethod
    async def on_abort(self, tid: str) -> None:
        """Se llama cuando el usuario ejecuta ABORT (antes de que tx_mgr escriba ABORT)."""

    @abstractmethod
    async def recover(self, wal_entries: list, adapters: dict = None) -> ReporteRecuperacion:
        """
        Analiza el WAL tras un fallo y aplica la lógica de recuperación del protocolo.
        adapters: {'postgres': adapter_obj, 'mongo': adapter_obj}
        """


# ─── Protocolo 1: No-Undo / No-Redo ─────────────────────────────────────────

class NoUndoNoRedo(RecoveryProtocol):
    """
    Deferred Update con FORCE.
    Las escrituras se difieren hasta el COMMIT. No es necesario deshacer ni
    rehacer nada en la recuperación porque:
      - sin COMMIT: la BD nunca fue tocada.
      - con COMMIT: los cambios ya están garantizados en la BD.
    """
    nombre = 'no_undo_no_redo'

    async def on_write(self, tid: str, op: str, engine: str, sql: str, adapter) -> tuple:
        # No se escribe nada en la BD todavía: se bufferiza
        self._guardar_adapter(tid, adapter)
        if tid not in self.buffer:
            self.buffer[tid] = []
        self.buffer[tid].append({'op': op, 'sql': sql, 'engine': engine, 'adapter': adapter})
        return [], None  # before vacío, after diferido

    async def on_commit(self, tid: str) -> None:
        # Aplicar todas las operaciones bufferizadas de golpe
        operaciones = self.buffer.pop(tid, [])
        for item in operaciones:
            if item['engine'] != 'postgres':
                continue
            sql = item['sql']
            verbo = _extraer_verbo(sql)
            tabla = _extraer_tabla(sql, verbo)
            where = _extraer_where(sql) if verbo in ('update', 'delete') else None
            adapter = item['adapter']
            try:
                before, after = await _ejecutar_dml_pg(adapter, sql, verbo, tabla, where)
            except Exception:
                before, after = [], []
            # Registrar en WAL ahora que se aplicó
            await wal_module.append({
                'tid': tid,
                'op': item['op'],
                'engine': 'postgres',
                'query': sql,
                'before': before,
                'after': after,
                'table': tabla,
            })
        self._limpiar_tid(tid)

    async def on_abort(self, tid: str) -> None:
        # Descartar el buffer: la BD nunca fue modificada
        self._limpiar_tid(tid)

    async def recover(self, wal_entries: list, adapters: dict = None) -> ReporteRecuperacion:
        # Recuperación trivial: no hay nada que deshacer ni rehacer
        return ReporteRecuperacion(
            protocolo=self.nombre,
            estado_final='consistente',
        )


# ─── Protocolo 2: No-Undo / Redo ─────────────────────────────────────────────

class NoUndoRedo(RecoveryProtocol):
    """
    Deferred Update sin FORCE.
    Las escrituras se difieren hasta el COMMIT. Tras un fallo, las transacciones
    que ya llegaron a COMMIT se deben REHACER porque sus cambios pueden no haber
    alcanzado la BD. Las que no commitearon no dejan rastro en la BD.
    """
    nombre = 'no_undo_redo'

    async def on_write(self, tid: str, op: str, engine: str, sql: str, adapter) -> tuple:
        self._guardar_adapter(tid, adapter)
        if tid not in self.buffer:
            self.buffer[tid] = []
        self.buffer[tid].append({'op': op, 'sql': sql, 'engine': engine, 'adapter': adapter})
        return [], None

    async def on_commit(self, tid: str) -> None:
        operaciones = self.buffer.pop(tid, [])
        for item in operaciones:
            if item['engine'] != 'postgres':
                continue
            sql = item['sql']
            verbo = _extraer_verbo(sql)
            tabla = _extraer_tabla(sql, verbo)
            where = _extraer_where(sql) if verbo in ('update', 'delete') else None
            adapter = item['adapter']
            try:
                before, after = await _ejecutar_dml_pg(adapter, sql, verbo, tabla, where)
            except Exception:
                before, after = [], []
            await wal_module.append({
                'tid': tid,
                'op': item['op'],
                'engine': 'postgres',
                'query': sql,
                'before': before,
                'after': after,
                'table': tabla,
            })
        self._limpiar_tid(tid)

    async def on_abort(self, tid: str) -> None:
        self._limpiar_tid(tid)

    async def recover(self, wal_entries: list, adapters: dict = None) -> ReporteRecuperacion:
        """
        Para TXs con COMMIT en el WAL: REDO (re-aplicar sus operaciones).
        Para TXs sin COMMIT: nada (la BD nunca fue modificada).
        """
        pg = (adapters or {}).get('postgres') or self.pg
        tids_commit = _tids_con_commit(wal_entries)
        tids_sin_commit = _tids_sin_commit(wal_entries)

        tids_redo = []
        ops_redo = []

        for tid in tids_commit:
            ops = _ops_dml_de_tid(wal_entries, tid, engine='postgres')
            if not ops:
                continue
            tids_redo.append(tid)
            for entrada in ops:
                sql = entrada.get('query', '')
                if not sql or not pg:
                    ops_redo.append({'tid': tid, 'sql': sql, 'ok': False, 'razon': 'sin adaptador'})
                    continue
                res = await _ejecutar_redo_pg(pg, sql)
                res['tid'] = tid
                ops_redo.append(res)

        estado = 'consistente' if not any(not r.get('ok') for r in ops_redo) else 'incompleto'
        return ReporteRecuperacion(
            protocolo=self.nombre,
            tids_con_redo=tids_redo,
            operaciones_redo=ops_redo,
            estado_final=estado,
        )


# ─── Protocolo 3: Undo / No-Redo ─────────────────────────────────────────────

class UndoNoRedo(RecoveryProtocol):
    """
    Immediate Update con FORCE en commit.
    Cada escritura se aplica inmediatamente a la BD. Al hacer COMMIT se marca en
    el WAL. Tras un fallo, las TXs sin COMMIT se deshacen usando los 'before' del WAL.
    """
    nombre = 'undo_no_redo'

    async def on_write(self, tid: str, op: str, engine: str, sql: str, adapter) -> tuple:
        self._guardar_adapter(tid, adapter)
        if engine != 'postgres':
            return [], None
        verbo = _extraer_verbo(sql)
        tabla = _extraer_tabla(sql, verbo)
        where = _extraer_where(sql) if verbo in ('update', 'delete') else None
        before, after = await _ejecutar_dml_pg(adapter, sql, verbo, tabla, where)
        # Escribir en WAL inmediatamente (escritura anticipada)
        await wal_module.append({
            'tid': tid,
            'op': op,
            'engine': 'postgres',
            'query': sql,
            'before': before,
            'after': after,
            'table': tabla,
        })
        return before, after

    async def on_commit(self, tid: str) -> None:
        # Las operaciones ya están en la BD y en el WAL; solo se marca el commit
        self._limpiar_tid(tid)

    async def on_abort(self, tid: str) -> None:
        # Deshacer en orden inverso usando las imágenes 'before' del WAL
        adapter = self._adapter_de(tid)
        if adapter:
            entradas = wal_module.query(tid=tid)
            ops = [e for e in entradas if e.get('op') in ('INSERT', 'UPDATE', 'DELETE')]
            for entrada in reversed(ops):
                tabla = entrada.get('table') or ''
                if not tabla:
                    continue
                sqls = _sqls_undo(
                    entrada.get('op', ''),
                    tabla,
                    entrada.get('before', []),
                    entrada.get('after', []),
                )
                await _ejecutar_undo_pg(adapter, sqls)
        self._limpiar_tid(tid)

    async def recover(self, wal_entries: list, adapters: dict = None) -> ReporteRecuperacion:
        """
        Para TXs sin COMMIT: UNDO (revertir los cambios parciales en BD).
        Para TXs con COMMIT: nada (ya están confirmados).
        """
        pg = (adapters or {}).get('postgres') or self.pg
        tids_sin_commit = _tids_sin_commit(wal_entries)

        tids_undo = []
        ops_undo = []

        for tid in tids_sin_commit:
            ops = _ops_dml_de_tid(wal_entries, tid, engine='postgres')
            if not ops:
                continue
            tids_undo.append(tid)
            # UNDO en orden inverso
            for entrada in reversed(ops):
                tabla = entrada.get('table') or ''
                if not tabla or not pg:
                    ops_undo.append({'tid': tid, 'op': entrada.get('op'), 'ok': False, 'razon': 'sin tabla o adaptador'})
                    continue
                sqls = _sqls_undo(
                    entrada.get('op', ''),
                    tabla,
                    entrada.get('before', []),
                    entrada.get('after', []),
                )
                resultados = await _ejecutar_undo_pg(pg, sqls)
                for r in resultados:
                    r['tid'] = tid
                    r['op_original'] = entrada.get('op')
                ops_undo.extend(resultados)

        estado = 'consistente' if not any(not r.get('ok') for r in ops_undo) else 'incompleto'
        return ReporteRecuperacion(
            protocolo=self.nombre,
            tids_con_undo=tids_undo,
            operaciones_undo=ops_undo,
            estado_final=estado,
        )


# ─── Protocolo 4: Undo / Redo ────────────────────────────────────────────────

class UndoRedo(RecoveryProtocol):
    """
    Steal/No-Force — el protocolo más general (base de ARIES).
    Las escrituras se aplican inmediatamente a la BD. Tras un fallo:
      - TXs sin COMMIT: UNDO usando 'before' del WAL.
      - TXs con COMMIT:  REDO usando 'after'/'query' del WAL.
    """
    nombre = 'undo_redo'

    async def on_write(self, tid: str, op: str, engine: str, sql: str, adapter) -> tuple:
        self._guardar_adapter(tid, adapter)
        if engine != 'postgres':
            return [], None
        verbo = _extraer_verbo(sql)
        tabla = _extraer_tabla(sql, verbo)
        where = _extraer_where(sql) if verbo in ('update', 'delete') else None
        before, after = await _ejecutar_dml_pg(adapter, sql, verbo, tabla, where)
        await wal_module.append({
            'tid': tid,
            'op': op,
            'engine': 'postgres',
            'query': sql,
            'before': before,
            'after': after,
            'table': tabla,
        })
        return before, after

    async def on_commit(self, tid: str) -> None:
        self._limpiar_tid(tid)

    async def on_abort(self, tid: str) -> None:
        adapter = self._adapter_de(tid)
        if adapter:
            entradas = wal_module.query(tid=tid)
            ops = [e for e in entradas if e.get('op') in ('INSERT', 'UPDATE', 'DELETE')]
            for entrada in reversed(ops):
                tabla = entrada.get('table') or ''
                if not tabla:
                    continue
                sqls = _sqls_undo(
                    entrada.get('op', ''),
                    tabla,
                    entrada.get('before', []),
                    entrada.get('after', []),
                )
                await _ejecutar_undo_pg(adapter, sqls)
        self._limpiar_tid(tid)

    async def recover(self, wal_entries: list, adapters: dict = None) -> ReporteRecuperacion:
        """
        TXs sin COMMIT → UNDO.
        TXs con COMMIT → REDO.
        """
        pg = (adapters or {}).get('postgres') or self.pg
        tids_sin_commit = _tids_sin_commit(wal_entries)
        tids_commit = _tids_con_commit(wal_entries)

        tids_undo = []
        ops_undo = []
        tids_redo = []
        ops_redo = []

        # UNDO: transacciones incompletas
        for tid in tids_sin_commit:
            ops = _ops_dml_de_tid(wal_entries, tid, engine='postgres')
            if not ops:
                continue
            tids_undo.append(tid)
            for entrada in reversed(ops):
                tabla = entrada.get('table') or ''
                if not tabla or not pg:
                    ops_undo.append({'tid': tid, 'op': entrada.get('op'), 'ok': False, 'razon': 'sin tabla o adaptador'})
                    continue
                sqls = _sqls_undo(
                    entrada.get('op', ''),
                    tabla,
                    entrada.get('before', []),
                    entrada.get('after', []),
                )
                resultados = await _ejecutar_undo_pg(pg, sqls)
                for r in resultados:
                    r['tid'] = tid
                    r['op_original'] = entrada.get('op')
                ops_undo.extend(resultados)

        # REDO: transacciones confirmadas (re-aplicar por si el flush no llegó a BD)
        for tid in tids_commit:
            ops = _ops_dml_de_tid(wal_entries, tid, engine='postgres')
            if not ops:
                continue
            tids_redo.append(tid)
            for entrada in ops:
                sql = entrada.get('query', '')
                if not sql or not pg:
                    ops_redo.append({'tid': tid, 'sql': sql, 'ok': False, 'razon': 'sin adaptador'})
                    continue
                res = await _ejecutar_redo_pg(pg, sql)
                res['tid'] = tid
                ops_redo.append(res)

        todos_ok = not any(not r.get('ok') for r in ops_undo + ops_redo)
        return ReporteRecuperacion(
            protocolo=self.nombre,
            tids_con_undo=tids_undo,
            operaciones_undo=ops_undo,
            tids_con_redo=tids_redo,
            operaciones_redo=ops_redo,
            estado_final='consistente' if todos_ok else 'incompleto',
        )


# ─── Utilidades para analizar el WAL ─────────────────────────────────────────

def _tids_con_commit(wal_entries: list) -> list:
    """Devuelve TIDs que tienen registro COMMIT en el WAL."""
    return [e['tid'] for e in wal_entries if e.get('op') == 'COMMIT']


def _tids_sin_commit(wal_entries: list) -> list:
    """
    Devuelve TIDs que tienen BEGIN pero NO COMMIT ni ABORT
    (es decir, transacciones interrumpidas por un fallo).
    """
    con_begin = {e['tid'] for e in wal_entries if e.get('op') == 'BEGIN'}
    con_fin = {e['tid'] for e in wal_entries if e.get('op') in ('COMMIT', 'ABORT')}
    return list(con_begin - con_fin)


def _ops_dml_de_tid(wal_entries: list, tid: str, engine: str = 'postgres') -> list:
    """Retorna las operaciones DML de una transacción específica en orden cronológico."""
    return [
        e for e in wal_entries
        if e.get('tid') == tid
        and e.get('op') in ('INSERT', 'UPDATE', 'DELETE')
        and e.get('engine') == engine
    ]
