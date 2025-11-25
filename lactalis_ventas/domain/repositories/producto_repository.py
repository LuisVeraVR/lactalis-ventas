"""Interfaz del repositorio de productos."""
from abc import ABC, abstractmethod
from typing import List, Optional
from lactalis_ventas.domain.entities.producto import Producto


class ProductoRepository(ABC):
    """Interfaz del repositorio de productos."""

    @abstractmethod
    def obtener_todos(self) -> List[Producto]:
        """Obtiene todos los productos."""
        pass

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código."""
        pass

    @abstractmethod
    def guardar(self, producto: Producto) -> None:
        """Guarda un producto."""
        pass

    @abstractmethod
    def actualizar(self, producto: Producto) -> None:
        """Actualiza un producto."""
        pass

    @abstractmethod
    def buscar(self, termino: str) -> List[Producto]:
        """Busca productos por término."""
        pass

    @abstractmethod
    def obtener_por_grupo(self, grupo: str) -> List[Producto]:
        """Obtiene productos por grupo."""
        pass
