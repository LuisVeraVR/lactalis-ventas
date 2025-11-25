"""Procesador de archivos Excel."""
import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from lactalis_ventas.domain.entities.factura import FacturaLinea


class ExcelProcessor:
    """Procesador de archivos Excel de facturas."""

    # Columnas esperadas en el Excel
    COLUMNAS_ESPERADAS = {
        "numero_factura": ["numero_factura", "factura", "nro_factura", "número factura"],
        "fecha": ["fecha", "fecha_factura"],
        "cod_padre": ["cod_padre", "código padre", "codigo_padre"],
        "nombre_tercero": ["nombre_tercero", "tercero", "cliente", "nombre cliente"],
        "nit": ["nit", "identificación", "identificacion"],
        "codigo_producto": ["codigo_producto", "código producto", "cod_producto"],
        "descripcion_producto": ["descripcion_producto", "descripción producto", "producto", "descripcion"],
        "grupo_producto": ["grupo_producto", "grupo", "categoría", "categoria"],
        "cantidad": ["cantidad", "qty", "unidades"],
        "valor_neto": ["valor_neto", "valor neto", "total", "valor"]
    }

    def procesar_archivo(self, ruta_archivo: str) -> List[FacturaLinea]:
        """
        Procesa un archivo Excel y retorna una lista de FacturaLinea.

        Args:
            ruta_archivo: Ruta al archivo Excel

        Returns:
            Lista de FacturaLinea extraídas del Excel

        Raises:
            Exception: Si hay errores al procesar el archivo
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(ruta_archivo)

            # Normalizar nombres de columnas
            df.columns = [col.strip().lower() for col in df.columns]

            # Mapear columnas
            columnas_mapeadas = self._mapear_columnas(df.columns)

            # Validar que existan las columnas requeridas
            columnas_faltantes = [
                col for col in self.COLUMNAS_ESPERADAS.keys()
                if col not in columnas_mapeadas
            ]

            if columnas_faltantes:
                raise ValueError(
                    f"Columnas faltantes en el Excel: {', '.join(columnas_faltantes)}"
                )

            # Procesar cada fila
            lineas = []
            for idx, row in df.iterrows():
                try:
                    linea = self._procesar_fila(row, columnas_mapeadas, idx)
                    if linea:
                        lineas.append(linea)
                except Exception as e:
                    print(f"Advertencia: Error en fila {idx + 2}: {str(e)}")
                    continue

            return lineas

        except Exception as e:
            raise Exception(f"Error al procesar archivo Excel: {str(e)}")

    def _mapear_columnas(self, columnas_df: List[str]) -> dict:
        """Mapea las columnas del DataFrame a las columnas esperadas."""
        mapeo = {}
        columnas_df_lower = [col.lower().strip() for col in columnas_df]

        for col_esperada, variantes in self.COLUMNAS_ESPERADAS.items():
            for variante in variantes:
                if variante.lower() in columnas_df_lower:
                    idx = columnas_df_lower.index(variante.lower())
                    mapeo[col_esperada] = columnas_df[idx]
                    break

        return mapeo

    def _procesar_fila(
        self,
        row,
        columnas_mapeadas: dict,
        idx: int
    ) -> Optional[FacturaLinea]:
        """Procesa una fila del DataFrame y retorna una FacturaLinea."""
        try:
            # Extraer datos de la fila
            numero_factura = str(row[columnas_mapeadas["numero_factura"]]).strip()

            # Procesar fecha
            fecha_raw = row[columnas_mapeadas["fecha"]]
            if pd.isna(fecha_raw):
                fecha = datetime.now()
            elif isinstance(fecha_raw, pd.Timestamp):
                fecha = fecha_raw.to_pydatetime()
            elif isinstance(fecha_raw, datetime):
                fecha = fecha_raw
            else:
                fecha = pd.to_datetime(fecha_raw).to_pydatetime()

            cod_padre = str(row[columnas_mapeadas["cod_padre"]]).strip()
            nombre_tercero = str(row[columnas_mapeadas["nombre_tercero"]]).strip()
            nit = str(row[columnas_mapeadas["nit"]]).strip()
            codigo_producto = str(row[columnas_mapeadas["codigo_producto"]]).strip()
            descripcion_producto = str(row[columnas_mapeadas["descripcion_producto"]]).strip()
            grupo_producto = str(row[columnas_mapeadas["grupo_producto"]]).strip()

            # Procesar cantidad
            cantidad_raw = row[columnas_mapeadas["cantidad"]]
            cantidad = Decimal(str(cantidad_raw)) if not pd.isna(cantidad_raw) else Decimal("0")

            # Procesar valor neto
            valor_neto_raw = row[columnas_mapeadas["valor_neto"]]
            valor_neto = Decimal(str(valor_neto_raw)) if not pd.isna(valor_neto_raw) else Decimal("0")

            # Validar que los datos básicos no estén vacíos
            if not numero_factura or numero_factura == "nan":
                return None
            if not cod_padre or cod_padre == "nan":
                return None
            if not codigo_producto or codigo_producto == "nan":
                return None

            # Crear la línea de factura
            linea = FacturaLinea(
                numero_factura=numero_factura,
                fecha=fecha,
                cod_padre=cod_padre,
                nombre_tercero=nombre_tercero,
                nit=nit,
                codigo_producto=codigo_producto,
                descripcion_producto=descripcion_producto,
                grupo_producto=grupo_producto,
                cantidad=cantidad,
                valor_neto=valor_neto
            )

            return linea

        except Exception as e:
            raise Exception(f"Error procesando fila {idx + 2}: {str(e)}")
