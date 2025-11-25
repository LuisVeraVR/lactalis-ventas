"""Interfaz del repositorio de terceros."""
from abc import ABC, abstractmethod
from typing import List, Optional
from lactalis_ventas.domain.entities.tercero import Tercero


class TerceroRepository(ABC):
    """Interfaz del repositorio de terceros."""

    @abstractmethod
    def obtener_todos(self) -> List[Tercero]:
        """Obtiene todos los terceros."""
        pass

    @abstractmethod
    def obtener_por_cod_padre(self, cod_padre: str) -> Optional[Tercero]:
        """Obtiene un tercero por su código padre."""
        pass

    @abstractmethod
    def guardar(self, tercero: Tercero) -> None:
        """Guarda un tercero."""
        pass

    @abstractmethod
    def actualizar(self, tercero: Tercero) -> None:
        """Actualiza un tercero."""
        pass

    @abstractmethod
    def buscar(self, termino: str) -> List[Tercero]:
        """Busca terceros por término."""
        pass
