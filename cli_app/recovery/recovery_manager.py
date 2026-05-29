"""Coordinador que mantiene el protocolo de recuperación activo."""
from recovery.protocols import NoUndoNoRedo, NoUndoRedo, UndoNoRedo, UndoRedo


NOMBRES_VALIDOS = ('no_undo_no_redo', 'no_undo_redo', 'undo_no_redo', 'undo_redo')


class RecoveryManager:
    def __init__(self, pg_adapter=None, mongo_adapter=None):
        self.protocolos = {
            'no_undo_no_redo': NoUndoNoRedo(pg_adapter, mongo_adapter),
            'no_undo_redo':    NoUndoRedo(pg_adapter, mongo_adapter),
            'undo_no_redo':    UndoNoRedo(pg_adapter, mongo_adapter),
            'undo_redo':       UndoRedo(pg_adapter, mongo_adapter),
        }
        # El protocolo más completo como predeterminado
        self.activo = self.protocolos['undo_redo']

    def seleccionar(self, nombre: str) -> bool:
        """Cambia el protocolo activo. Retorna True si el nombre es válido."""
        if nombre not in self.protocolos:
            return False
        self.activo = self.protocolos[nombre]
        return True

    def protocolo_activo(self) -> str:
        return self.activo.nombre
