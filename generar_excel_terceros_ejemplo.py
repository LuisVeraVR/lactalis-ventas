"""Script para generar un archivo Excel de ejemplo de terceros."""
import pandas as pd


def generar_excel_terceros():
    """Genera un archivo Excel de ejemplo con terceros."""

    # Datos de ejemplo
    datos = [
        {
            "cod_padre": "T001",
            "nombre": "Supermercado La Canasta",
            "nit": "900123456-1",
            "activo": True
        },
        {
            "cod_padre": "T002",
            "nombre": "Tienda El Ahorro",
            "nit": "800234567-2",
            "activo": True
        },
        {
            "cod_padre": "T003",
            "nombre": "Distribuidora Los Andes",
            "nit": "700345678-3",
            "activo": True
        },
        {
            "cod_padre": "T004",
            "nombre": "Café Gourmet del Centro",
            "nit": "600456789-4",
            "activo": True
        },
        {
            "cod_padre": "T005",
            "nombre": "Supermercado El Éxito",
            "nit": "890123456-5",
            "activo": True
        },
        {
            "cod_padre": "T006",
            "nombre": "Carrefour Colombia",
            "nit": "890234567-6",
            "activo": True
        },
        {
            "cod_padre": "T007",
            "nombre": "Tiendas Ara",
            "nit": "890345678-7",
            "activo": True
        },
        {
            "cod_padre": "T008",
            "nombre": "Olímpica S.A.",
            "nit": "890456789-8",
            "activo": True
        },
        {
            "cod_padre": "T009",
            "nombre": "D1 Tiendas",
            "nit": "890567890-9",
            "activo": True
        },
        {
            "cod_padre": "T010",
            "nombre": "Justo & Bueno",
            "nit": "890678901-0",
            "activo": True
        },
        {
            "cod_padre": "T011",
            "nombre": "Distribuidora del Valle (Inactivo)",
            "nit": "800789012-1",
            "activo": False  # Este tercero está desactivado
        },
        {
            "cod_padre": "T012",
            "nombre": "Makro S.A.",
            "nit": "890890123-2",
            "activo": True
        },
        {
            "cod_padre": "T013",
            "nombre": "PriceSmart Colombia",
            "nit": "890901234-3",
            "activo": True
        },
        {
            "cod_padre": "T014",
            "nombre": "Tiendas Jumbo",
            "nit": "890012345-4",
            "activo": True
        },
        {
            "cod_padre": "T015",
            "nombre": "Metro Cali",
            "nit": "800123456-5",
            "activo": True
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
    print(f"- Terceros activos: {sum(1 for t in datos if t['activo'])}")
    print(f"- Terceros inactivos: {sum(1 for t in datos if not t['activo'])}")
    print(f"\nPuede usar este archivo para importar terceros a la aplicación.")


if __name__ == "__main__":
    generar_excel_terceros()
