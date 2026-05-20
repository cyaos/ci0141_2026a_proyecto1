from fastapi import HTTPException
from connections.connection_manager import ConnectionManager

_manager: ConnectionManager | None = None

def get_manager() -> ConnectionManager:
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
        _manager.conectar_todos()
    return _manager

def get_engine(engine_name: str):
    manager = get_manager()
    if engine_name not in manager.conexiones:
        raise HTTPException(status_code=404, detail="Motor de base de datos no reconocido.")
    
    connection = manager.conexiones[engine_name]
    if not connection.probar_conexion():
        raise HTTPException(status_code=503, detail=f"El motor {connection.nombre} no está disponible.")
    
    return connection

def shutdown() -> None:
    global _manager
    if _manager is not None:
        _manager.desconectar_todos()
        _manager = None
