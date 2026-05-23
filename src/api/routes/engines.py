from fastapi import APIRouter
from api.deps import get_manager
from api.schemas import EngineStatus

router = APIRouter(prefix="/api/engines", tags=["engines"])

ENGINE_META = {
    "postgres": {
        "name": "PostgreSQL",
        "host": "localhost",
        "port": 5432
    },
    "mongo": {
        "name": "MongoDB",
        "host": "localhost",
        "port": 27017
    }
}

@router.get("/status", response_model=list[EngineStatus])
def get_engine_status():
    manager = get_manager()
    engine_statuses = []
    
    for engine_key, meta_info in ENGINE_META.items():
        connection = manager.conexiones.get(engine_key)
        is_active = False
        
        if connection:
            is_active = connection.probar_conexion()
            
        engine_statuses.append(
            EngineStatus(
                key=engine_key,
                name=meta_info["name"],
                host=meta_info["host"],
                port=meta_info["port"],
                active=is_active
            )
        )
        
    return engine_statuses
