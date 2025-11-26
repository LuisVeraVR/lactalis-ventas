"""Procesador de archivos Excel para terceros."""
import pandas as pd
from typing import List
from lactalis_ventas.domain.entities.tercero import Tercero


class TerceroExcelProcessor:
    """Procesador de archivos Excel de terceros."""

    # Columnas esperadas en el Excel
    COLUMNAS_ESPERADAS = {
        "id": ["v", "id", "#", "número", "numero"],  # Columna V como ID (opcional)
        "cod_padre": ["nombre código padre", "nombre codigo padre", "cod_padre", "código padre", "codigo_padre", "codigo", "código", "code"],
        "nombre": ["nombre", "razon_social", "razón social", "cliente", "tercero", "name"],
        "nit": ["nit", "identificación", "identificacion", "documento", "ruc"],
        "se_registra": ["se_registra", "se registra", "activo", "estado", "active"]
    }

    def procesar_archivo(self, ruta_archivo: str) -> List[Tercero]:
        """
        Procesa un archivo Excel y retorna una lista de Tercero.

        Args:
            ruta_archivo: Ruta al archivo Excel

        Returns:
            Lista de Tercero extraídos del Excel

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
            if "cod_padre" not in columnas_mapeadas:
                raise ValueError("El Excel debe contener una columna de 'Nombre Código Padre' o 'codigo'")
            if "nit" not in columnas_mapeadas:
                raise ValueError("El Excel debe contener una columna de 'NIT'")

            # Si no hay columna nombre, usar cod_padre como nombre
            if "nombre" not in columnas_mapeadas:
                columnas_mapeadas["nombre"] = columnas_mapeadas["cod_padre"]

            # Si no hay columna se_registra, usar True por defecto
            if "se_registra" not in columnas_mapeadas:
                df["_activo_default"] = True
                columnas_mapeadas["se_registra"] = "_activo_default"

            # Procesar cada fila
            terceros = []
            errores = []

            for idx, row in df.iterrows():
                try:
                    tercero = self._procesar_fila(row, columnas_mapeadas, idx)
                    if tercero:
                        terceros.append(tercero)
                except Exception as e:
                    errores.append(f"Fila {idx + 2}: {str(e)}")
                    continue

            if errores:
                print(f"Advertencias durante la importación:")
                for error in errores[:10]:  # Mostrar máximo 10 errores
                    print(f"  - {error}")
                if len(errores) > 10:
                    print(f"  ... y {len(errores) - 10} errores más")

            return terceros

        except Exception as e:
            raise Exception(f"Error al procesar archivo Excel de terceros: {str(e)}")

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

    def _procesar_fila(self, row, columnas_mapeadas: dict, idx: int) -> Tercero:
        """Procesa una fila del DataFrame y retorna un Tercero."""
        # Extraer datos de la fila
        cod_padre = str(row[columnas_mapeadas["cod_padre"]]).strip()
        nombre = str(row[columnas_mapeadas["nombre"]]).strip()
        nit = str(row[columnas_mapeadas["nit"]]).strip()

        # Procesar se_registra
        se_registra_raw = row[columnas_mapeadas["se_registra"]]
        if isinstance(se_registra_raw, bool):
            se_registra = se_registra_raw
        elif isinstance(se_registra_raw, (int, float)):
            se_registra = bool(int(se_registra_raw))
        elif isinstance(se_registra_raw, str):
            se_registra_lower = se_registra_raw.lower().strip()
            # Reconocer "NIT" como True y "NO NIT" como False
            if "no nit" in se_registra_lower or "no_nit" in se_registra_lower:
                se_registra = False
            elif "nit" in se_registra_lower:
                se_registra = True
            else:
                # Otros valores comunes
                se_registra = se_registra_lower in ["true", "1", "si", "sí", "yes", "activo"]
        else:
            se_registra = True

        # Validar que los datos básicos no estén vacíos
        if not cod_padre or cod_padre == "nan":
            raise ValueError("Código padre vacío")
        if not nombre or nombre == "nan":
            raise ValueError("Nombre vacío")
        if not nit or nit == "nan":
            raise ValueError("NIT vacío")

        # Crear el tercero
        tercero = Tercero(
            cod_padre=cod_padre,
            nombre=nombre,
            nit=nit,
            se_registra=se_registra
        )

        return tercero
