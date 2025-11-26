"""Script para generar un archivo Excel de ejemplo de terceros."""
import pandas as pd


def generar_excel_terceros():
    """Genera un archivo Excel de ejemplo con terceros."""

    # Datos de ejemplo - Formato: V, Nombre Código Padre, NIT, Se Registra
    datos = [
        {
            "V": 1,
            "Nombre Código Padre": "T001",
            "NIT": "900123456-1",
            "Se Registra": True
        },
        {
            "V": 2,
            "Nombre Código Padre": "T002",
            "NIT": "800234567-2",
            "Se Registra": True
        },
        {
            "V": 3,
            "Nombre Código Padre": "T003",
            "NIT": "700345678-3",
            "Se Registra": True
        },
        {
            "V": 4,
            "Nombre Código Padre": "T004",
            "NIT": "600456789-4",
            "Se Registra": True
        },
        {
            "V": 5,
            "Nombre Código Padre": "T005",
            "NIT": "890123456-5",
            "Se Registra": True
        },
        {
            "V": 6,
            "Nombre Código Padre": "T006",
            "NIT": "890234567-6",
            "Se Registra": True
        },
        {
            "V": 7,
            "Nombre Código Padre": "T007",
            "NIT": "890345678-7",
            "Se Registra": True
        },
        {
            "V": 8,
            "Nombre Código Padre": "T008",
            "NIT": "890456789-8",
            "Se Registra": True
        },
        {
            "V": 9,
            "Nombre Código Padre": "T009",
            "NIT": "890567890-9",
            "Se Registra": True
        },
        {
            "V": 10,
            "Nombre Código Padre": "T010",
            "NIT": "890678901-0",
            "Se Registra": True
        },
        {
            "V": 11,
            "Nombre Código Padre": "T011",
            "NIT": "800789012-1",
            "Se Registra": False  # Este tercero está desactivado
        },
        {
            "V": 12,
            "Nombre Código Padre": "T012",
            "NIT": "890890123-2",
            "Se Registra": True
        },
        {
            "V": 13,
            "Nombre Código Padre": "T013",
            "NIT": "890901234-3",
            "Se Registra": True
        },
        {
            "V": 14,
            "Nombre Código Padre": "T014",
            "NIT": "890012345-4",
            "Se Registra": True
        },
        {
            "V": 15,
            "Nombre Código Padre": "T015",
            "NIT": "800123456-5",
            "Se Registra": True
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
    print(f"- Terceros activos: {sum(1 for t in datos if t['Se Registra'])}")
    print(f"- Terceros inactivos: {sum(1 for t in datos if not t['Se Registra'])}")
    print(f"\nFormato de columnas:")
    print(f"- V: Identificador numérico")
    print(f"- Nombre Código Padre: Código del tercero")
    print(f"- NIT: Número de identificación tributaria")
    print(f"- Se Registra: Estado (True/False)")
    print(f"\nPuede usar este archivo para importar terceros a la aplicación.")


if __name__ == "__main__":
    generar_excel_terceros()
