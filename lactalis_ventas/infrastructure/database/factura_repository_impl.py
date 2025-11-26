"""Implementación del repositorio de facturas con SQLite."""
from typing import List
from datetime import datetime
from decimal import Decimal
from lactalis_ventas.domain.entities.factura import FacturaLinea
from lactalis_ventas.domain.repositories.factura_repository import FacturaRepository
from lactalis_ventas.domain.value_objects.resultado_procesamiento import EstadisticasFacturas
from lactalis_ventas.infrastructure.database.database import Database


class FacturaRepositoryImpl(FacturaRepository):
    """Implementación del repositorio de facturas con SQLite."""

    def __init__(self, database: Database):
        self.db = database

    def guardar_lineas(self, lineas: List[FacturaLinea]) -> None:
        """Guarda múltiples líneas de factura."""
        if not lineas:
            return

        datos = [
            (
                linea.numero_factura,
                linea.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                linea.anulada,
                linea.clase_factura,
                linea.cod_padre,
                linea.nombre_tercero,
                linea.nit,
                linea.codigo_producto,
                linea.descripcion_producto,
                linea.grupo_producto,
                float(linea.cantidad),
                float(linea.valor_neto),
                1 if linea.fue_registrada else 0,
                linea.motivo_rechazo
            )
            for linea in lineas
        ]

        self.db.ejecutar_many(
            """
            INSERT INTO facturas_procesadas
            (numero_factura, fecha, anulada, clase_factura, cod_padre, nombre_tercero, nit,
             codigo_producto, descripcion_producto, grupo_producto,
             cantidad, valor_neto, fue_registrada, motivo_rechazo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            datos
        )

    def obtener_todas_lineas(self) -> List[FacturaLinea]:
        """Obtiene todas las líneas de factura."""
        cursor = self.db.ejecutar_query(
            "SELECT * FROM facturas_procesadas ORDER BY fecha DESC"
        )
        rows = cursor.fetchall()
        return [self._row_to_linea(row) for row in rows]

    def obtener_estadisticas(self) -> EstadisticasFacturas:
        """Obtiene estadísticas de las facturas procesadas."""
        cursor = self.db.ejecutar_query(
            """
            SELECT
                COUNT(*) as total_facturas,
                SUM(valor_neto) as total_valor_neto,
                COUNT(DISTINCT codigo_producto) as productos_unicos,
                COUNT(DISTINCT cod_padre) as terceros_unicos,
                MIN(fecha) as fecha_inicio,
                MAX(fecha) as fecha_fin
            FROM facturas_procesadas
            WHERE fue_registrada = 1
            """
        )
        row = cursor.fetchone()

        if not row or row["total_facturas"] == 0:
            return EstadisticasFacturas()

        return EstadisticasFacturas(
            total_facturas=row["total_facturas"] or 0,
            total_valor_neto=float(row["total_valor_neto"] or 0.0),
            productos_unicos=row["productos_unicos"] or 0,
            terceros_unicos=row["terceros_unicos"] or 0,
            fecha_inicio=row["fecha_inicio"] or "",
            fecha_fin=row["fecha_fin"] or ""
        )

    def limpiar_todas(self) -> None:
        """Elimina todas las líneas de factura."""
        self.db.ejecutar_query("DELETE FROM facturas_procesadas")
        self.db.commit()

    def _row_to_linea(self, row) -> FacturaLinea:
        """Convierte una fila de la BD a un objeto FacturaLinea."""
        return FacturaLinea(
            numero_factura=row["numero_factura"],
            fecha=datetime.strptime(row["fecha"], "%Y-%m-%d %H:%M:%S"),
            anulada=row["anulada"] if "anulada" in row.keys() else "",
            clase_factura=row["clase_factura"] if "clase_factura" in row.keys() else "",
            cod_padre=row["cod_padre"],
            nombre_tercero=row["nombre_tercero"],
            nit=row["nit"],
            codigo_producto=row["codigo_producto"],
            descripcion_producto=row["descripcion_producto"],
            grupo_producto=row["grupo_producto"],
            cantidad=Decimal(str(row["cantidad"])),
            valor_neto=Decimal(str(row["valor_neto"])),
            fue_registrada=bool(row["fue_registrada"]),
            motivo_rechazo=row["motivo_rechazo"]
        )
