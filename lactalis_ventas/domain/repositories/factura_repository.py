"""Interfaz del repositorio de facturas."""
from abc import ABC, abstractmethod
from typing import List
from lactalis_ventas.domain.entities.factura import FacturaLinea
from lactalis_ventas.domain.value_objects.resultado_procesamiento import EstadisticasFacturas


class FacturaRepository(ABC):
    """Interfaz del repositorio de facturas."""

    @abstractmethod
    def guardar_lineas(self, lineas: List[FacturaLinea]) -> None:
        """Guarda múltiples líneas de factura."""
        pass

    @abstractmethod
    def obtener_todas_lineas(self) -> List[FacturaLinea]:
        """Obtiene todas las líneas de factura."""
        pass

    @abstractmethod
    def obtener_estadisticas(self) -> EstadisticasFacturas:
        """Obtiene estadísticas de las facturas procesadas."""
        pass

    @abstractmethod
    def limpiar_todas(self) -> None:
        """Elimina todas las líneas de factura."""
        pass
