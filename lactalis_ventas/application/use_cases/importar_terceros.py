"""Caso de uso para importar terceros desde Excel."""
from typing import List
from dataclasses import dataclass
from lactalis_ventas.domain.entities.tercero import Tercero
from lactalis_ventas.domain.repositories.tercero_repository import TerceroRepository


@dataclass
class ResultadoImportacionTerceros:
    """Resultado de la importación de terceros."""

    total_leidos: int = 0
    terceros_nuevos: int = 0
    terceros_actualizados: int = 0
    terceros_ignorados: int = 0
    errores: List[str] = None

    def __post_init__(self):
        if self.errores is None:
            self.errores = []

    def obtener_resumen(self) -> str:
        """Obtiene un resumen de la importación."""
        return (
            f"Total leídos: {self.total_leidos}\n"
            f"Nuevos: {self.terceros_nuevos}\n"
            f"Actualizados: {self.terceros_actualizados}\n"
            f"Ignorados: {self.terceros_ignorados}\n"
            f"Errores: {len(self.errores)}"
        )


class ImportarTercerosUseCase:
    """Caso de uso para importar terceros desde Excel."""

    def __init__(self, tercero_repo: TerceroRepository):
        self.tercero_repo = tercero_repo

    def ejecutar(self, terceros: List[Tercero], actualizar_existentes: bool = True) -> ResultadoImportacionTerceros:
        """
        Importa terceros desde una lista.

        Args:
            terceros: Lista de terceros a importar
            actualizar_existentes: Si es True, actualiza terceros existentes. Si es False, los ignora.

        Returns:
            ResultadoImportacionTerceros con el resultado de la importación
        """
        resultado = ResultadoImportacionTerceros(total_leidos=len(terceros))

        for tercero in terceros:
            try:
                # Verificar si el tercero ya existe
                tercero_existente = self.tercero_repo.obtener_por_cod_padre(tercero.cod_padre)

                if tercero_existente:
                    if actualizar_existentes:
                        # Actualizar tercero existente
                        self.tercero_repo.actualizar(tercero)
                        resultado.terceros_actualizados += 1
                    else:
                        # Ignorar tercero existente
                        resultado.terceros_ignorados += 1
                else:
                    # Crear nuevo tercero
                    self.tercero_repo.guardar(tercero)
                    resultado.terceros_nuevos += 1

            except Exception as e:
                resultado.errores.append(f"Error con tercero {tercero.cod_padre}: {str(e)}")

        return resultado
