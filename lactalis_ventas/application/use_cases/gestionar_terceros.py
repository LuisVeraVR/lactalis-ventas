"""Casos de uso para gestionar terceros."""
from typing import List, Optional
from lactalis_ventas.domain.entities.tercero import Tercero
from lactalis_ventas.domain.repositories.tercero_repository import TerceroRepository


class ListarTercerosUseCase:
    """Caso de uso para listar terceros."""

    def __init__(self, tercero_repo: TerceroRepository):
        self.tercero_repo = tercero_repo

    def ejecutar(self, solo_activos: bool = False) -> List[Tercero]:
        """Lista todos los terceros, o solo los activos."""
        if solo_activos:
            return self.tercero_repo.obtener_activos()
        return self.tercero_repo.obtener_todos()


class BuscarTercerosUseCase:
    """Caso de uso para buscar terceros."""

    def __init__(self, tercero_repo: TerceroRepository):
        self.tercero_repo = tercero_repo

    def ejecutar(self, termino: str) -> List[Tercero]:
        """Busca terceros por término."""
        if not termino or not termino.strip():
            return self.tercero_repo.obtener_todos()
        return self.tercero_repo.buscar(termino.strip())


class CambiarEstadoTerceroUseCase:
    """Caso de uso para cambiar el estado de un tercero."""

    def __init__(self, tercero_repo: TerceroRepository):
        self.tercero_repo = tercero_repo

    def ejecutar(self, cod_padre: str, activar: bool) -> Optional[Tercero]:
        """Cambia el estado de un tercero (activar/desactivar)."""
        tercero = self.tercero_repo.obtener_por_cod_padre(cod_padre)
        if not tercero:
            return None

        if activar:
            tercero.activar()
        else:
            tercero.desactivar()

        self.tercero_repo.actualizar(tercero)
        return tercero


class ObtenerTerceroPorCodPadreUseCase:
    """Caso de uso para obtener un tercero por código padre."""

    def __init__(self, tercero_repo: TerceroRepository):
        self.tercero_repo = tercero_repo

    def ejecutar(self, cod_padre: str) -> Optional[Tercero]:
        """Obtiene un tercero por su código padre."""
        return self.tercero_repo.obtener_por_cod_padre(cod_padre)
