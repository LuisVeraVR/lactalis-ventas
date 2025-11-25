"""Value Objects para resultados de procesamiento."""
from dataclasses import dataclass, field
from typing import List
from lactalis_ventas.domain.entities.factura import FacturaLinea


@dataclass
class ResultadoProcesamiento:
    """Resultado del procesamiento de facturas."""

    total_lineas: int = 0
    lineas_procesadas: int = 0
    lineas_rechazadas: int = 0
    lineas_registradas: List[FacturaLinea] = field(default_factory=list)
    lineas_rechazadas_detalle: List[FacturaLinea] = field(default_factory=list)
    errores: List[str] = field(default_factory=list)

    def agregar_linea_registrada(self, linea: FacturaLinea) -> None:
        """Agrega una línea registrada al resultado."""
        self.lineas_registradas.append(linea)
        self.lineas_procesadas += 1

    def agregar_linea_rechazada(self, linea: FacturaLinea) -> None:
        """Agrega una línea rechazada al resultado."""
        self.lineas_rechazadas_detalle.append(linea)
        self.lineas_rechazadas += 1

    def agregar_error(self, error: str) -> None:
        """Agrega un error al resultado."""
        self.errores.append(error)

    def obtener_resumen(self) -> str:
        """Obtiene un resumen del procesamiento."""
        return (
            f"Total líneas: {self.total_lineas}\n"
            f"Líneas registradas: {self.lineas_procesadas}\n"
            f"Líneas rechazadas: {self.lineas_rechazadas}\n"
            f"Errores: {len(self.errores)}"
        )


@dataclass
class EstadisticasFacturas:
    """Estadísticas de facturas procesadas."""

    total_facturas: int = 0
    total_valor_neto: float = 0.0
    productos_unicos: int = 0
    terceros_unicos: int = 0
    fecha_inicio: str = ""
    fecha_fin: str = ""
