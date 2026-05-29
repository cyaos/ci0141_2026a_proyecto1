"""Dataclass para reportar el resultado de una operación de recuperación."""
from dataclasses import dataclass, field


@dataclass
class ReporteRecuperacion:
    protocolo: str
    tids_con_undo: list = field(default_factory=list)
    tids_con_redo: list = field(default_factory=list)
    operaciones_undo: list = field(default_factory=list)   # detalles de cada reversión
    operaciones_redo: list = field(default_factory=list)   # detalles de cada re-aplicación
    estado_final: str = 'consistente'                      # 'consistente' | 'incompleto'

    def __str__(self):
        lineas = [
            f"Protocolo  : {self.protocolo}",
            f"Estado     : {self.estado_final}",
            f"TIDs UNDO  : {self.tids_con_undo or '(ninguno)'}",
            f"TIDs REDO  : {self.tids_con_redo or '(ninguno)'}",
        ]
        if self.operaciones_undo:
            lineas.append("Operaciones UNDO:")
            for op in self.operaciones_undo:
                lineas.append(f"  {op}")
        if self.operaciones_redo:
            lineas.append("Operaciones REDO:")
            for op in self.operaciones_redo:
                lineas.append(f"  {op}")
        return "\n".join(lineas)
