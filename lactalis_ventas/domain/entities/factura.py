"""Entidad Factura del dominio."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class FacturaLinea:
    """Representa una línea de factura procesada."""

    numero_factura: str
    fecha: datetime
    cod_padre: str
    nombre_tercero: str
    nit: str
    codigo_producto: str
    descripcion_producto: str
    grupo_producto: str
    cantidad: Decimal
    valor_neto: Decimal
    fue_registrada: bool = False
    motivo_rechazo: Optional[str] = None

    def __post_init__(self):
        """Validaciones de negocio."""
        if not self.numero_factura or not self.numero_factura.strip():
            raise ValueError("El número de factura no puede estar vacío")
        if not isinstance(self.fecha, datetime):
            raise ValueError("La fecha debe ser un objeto datetime")
        if self.valor_neto < 0:
            raise ValueError("El valor neto no puede ser negativo")

    def es_valida(self) -> bool:
        """Verifica si la línea de factura es válida según las reglas de negocio."""
        # Regla 1: El número de factura debe empezar con "Factura"
        if not self.numero_factura.startswith("Factura"):
            return False

        # Regla 2: El valor neto debe ser mayor que 0
        if self.valor_neto <= 0:
            return False

        return True

    def marcar_como_registrada(self) -> None:
        """Marca la línea como registrada."""
        self.fue_registrada = True
        self.motivo_rechazo = None

    def marcar_como_rechazada(self, motivo: str) -> None:
        """Marca la línea como rechazada con un motivo."""
        self.fue_registrada = False
        self.motivo_rechazo = motivo
