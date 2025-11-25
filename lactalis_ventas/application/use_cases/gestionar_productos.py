"""Casos de uso para gestionar productos."""
from typing import List, Optional
from lactalis_ventas.domain.entities.producto import Producto
from lactalis_ventas.domain.repositories.producto_repository import ProductoRepository


class ListarProductosUseCase:
    """Caso de uso para listar productos."""

    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def ejecutar(self) -> List[Producto]:
        """Lista todos los productos."""
        return self.producto_repo.obtener_todos()


class BuscarProductosUseCase:
    """Caso de uso para buscar productos."""

    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def ejecutar(self, termino: str) -> List[Producto]:
        """Busca productos por término."""
        if not termino or not termino.strip():
            return self.producto_repo.obtener_todos()
        return self.producto_repo.buscar(termino.strip())


class CambiarEstadoProductoUseCase:
    """Caso de uso para cambiar el estado de un producto."""

    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def ejecutar(self, codigo: str, activar: bool) -> Optional[Producto]:
        """Cambia el estado de un producto (activar/desactivar)."""
        producto = self.producto_repo.obtener_por_codigo(codigo)
        if not producto:
            return None

        if activar:
            producto.activar()
        else:
            producto.desactivar()

        self.producto_repo.actualizar(producto)
        return producto


class ObtenerProductoPorCodigoUseCase:
    """Caso de uso para obtener un producto por código."""

    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def ejecutar(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código."""
        return self.producto_repo.obtener_por_codigo(codigo)
