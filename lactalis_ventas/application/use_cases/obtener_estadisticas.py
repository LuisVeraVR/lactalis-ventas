"""Caso de uso para obtener estadísticas."""
from lactalis_ventas.domain.repositories.factura_repository import FacturaRepository
from lactalis_ventas.domain.value_objects.resultado_procesamiento import EstadisticasFacturas


class ObtenerEstadisticasUseCase:
    """Caso de uso para obtener estadísticas de facturas."""

    def __init__(self, factura_repo: FacturaRepository):
        self.factura_repo = factura_repo

    def ejecutar(self) -> EstadisticasFacturas:
        """Obtiene estadísticas de las facturas procesadas."""
        return self.factura_repo.obtener_estadisticas()
