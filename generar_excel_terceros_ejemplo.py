"""Script para generar un archivo Excel de ejemplo de terceros."""
import pandas as pd


def generar_excel_terceros():
    """Genera un archivo Excel de ejemplo con terceros."""

    # Datos de ejemplo - Formato: V (ID Único), Nombre Código Padre, Nombre, NIT, Se Registra
    datos = [
        {
            "V": "T001",
            "Nombre Código Padre": "COD001",
            "Nombre": "Distribuidora La Esperanza",
            "NIT": "900123456-1",
            "Se Registra": "NIT"
        },
        {
            "V": "T002",
            "Nombre Código Padre": "COD002",
            "Nombre": "Comercial El Progreso",
            "NIT": "800234567-2",
            "Se Registra": "NIT"
        },
        {
            "V": "T003",
            "Nombre Código Padre": "COD003",
            "Nombre": "Supermercado Los Andes",
            "NIT": "700345678-3",
            "Se Registra": "NIT"
        },
        {
            "V": "T004",
            "Nombre Código Padre": "COD004",
            "Nombre": "Almacén Don José",
            "NIT": "600456789-4",
            "Se Registra": "NIT"
        },
        {
            "V": "T005",
            "Nombre Código Padre": "COD005",
            "Nombre": "Tienda La Fortuna",
            "NIT": "890123456-5",
            "Se Registra": "NIT"
        },
        {
            "V": "T006",
            "Nombre Código Padre": "COD006",
            "Nombre": "Mercado Central",
            "NIT": "890234567-6",
            "Se Registra": "NIT"
        },
        {
            "V": "T007",
            "Nombre Código Padre": "COD007",
            "Nombre": "Distribuciones El Sol",
            "NIT": "890345678-7",
            "Se Registra": "NIT"
        },
        {
            "V": "T008",
            "Nombre Código Padre": "COD008",
            "Nombre": "Comercial La Luna",
            "NIT": "890456789-8",
            "Se Registra": "NIT"
        },
        {
            "V": "T009",
            "Nombre Código Padre": "COD009",
            "Nombre": "Almacén Las Estrellas",
            "NIT": "890567890-9",
            "Se Registra": "NIT"
        },
        {
            "V": "T010",
            "Nombre Código Padre": "COD010",
            "Nombre": "Supermercado El Valle",
            "NIT": "890678901-0",
            "Se Registra": "NIT"
        },
        {
            "V": "T011",
            "Nombre Código Padre": "COD011",
            "Nombre": "Tienda La Montaña",
            "NIT": "800789012-1",
            "Se Registra": "NO NIT"  # Este tercero está desactivado
        },
        {
            "V": "T012",
            "Nombre Código Padre": "COD012",
            "Nombre": "Distribuidora El Río",
            "NIT": "890890123-2",
            "Se Registra": "NIT"
        },
        {
            "V": "T013",
            "Nombre Código Padre": "COD013",
            "Nombre": "Comercial La Pradera",
            "NIT": "890901234-3",
            "Se Registra": "NIT"
        },
        {
            "V": "T014",
            "Nombre Código Padre": "COD014",
            "Nombre": "Almacén El Bosque",
            "NIT": "890012345-4",
            "Se Registra": "NIT"
        },
        {
            "V": "T015",
            "Nombre Código Padre": "COD015",
            "Nombre": "Supermercado La Costa",
            "NIT": "800123456-5",
            "Se Registra": "NIT"
        },
    ]

    # Crear DataFrame
    df = pd.DataFrame(datos)

    # Guardar a Excel
    archivo = "terceros_ejemplo.xlsx"
    df.to_excel(archivo, index=False, sheet_name="Terceros")

    print(f"Archivo generado exitosamente: {archivo}")
    print(f"\nEstadísticas del archivo:")
    print(f"- Total de terceros: {len(datos)}")
    print(f"- Terceros activos: {sum(1 for t in datos if t['Se Registra'] == 'NIT')}")
    print(f"- Terceros inactivos: {sum(1 for t in datos if t['Se Registra'] == 'NO NIT')}")
    print(f"\nFormato de columnas:")
    print(f"- V: Identificador único del tercero")
    print(f"- Nombre Código Padre: Código padre del tercero")
    print(f"- Nombre: Nombre completo del tercero")
    print(f"- NIT: Número de identificación tributaria")
    print(f"- Se Registra: Estado ('NIT' para activo, 'NO NIT' para inactivo)")
    print(f"\nPuede usar este archivo para importar terceros a la aplicación.")
    print(f"\nIMPORTANTE: La columna 'V' es el identificador único que se usará")
    print(f"para comparar con 'Cód.Padre' en las facturas de Lactalis.")


if __name__ == "__main__":
    generar_excel_terceros()
