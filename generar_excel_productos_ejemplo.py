"""Script para generar un archivo Excel de ejemplo de productos."""
import pandas as pd


def generar_excel_productos():
    """Genera un archivo Excel de ejemplo con productos."""

    # Datos de ejemplo
    datos = [
        {
            "codigo": "P001",
            "descripcion": "Yogurt Natural 1L",
            "grupo": "Yogurt",
            "activo": True
        },
        {
            "codigo": "P002",
            "descripcion": "Queso Campesino 500g",
            "grupo": "Quesos",
            "activo": True
        },
        {
            "codigo": "P003",
            "descripcion": "Mantequilla 250g",
            "grupo": "Derivados",
            "activo": True
        },
        {
            "codigo": "P004",
            "descripcion": "Yogurt Griego 150g",
            "grupo": "Yogurt",
            "activo": True
        },
        {
            "codigo": "P005",
            "descripcion": "Queso Mozzarella 1kg",
            "grupo": "Quesos",
            "activo": True
        },
        {
            "codigo": "P006",
            "descripcion": "Leche Entera 1L",
            "grupo": "Leches",
            "activo": True
        },
        {
            "codigo": "P007",
            "descripcion": "Queso Parmesano 200g",
            "grupo": "Quesos",
            "activo": True
        },
        {
            "codigo": "P008",
            "descripcion": "Yogurt Batido Fresa 1L",
            "grupo": "Yogurt",
            "activo": True
        },
        {
            "codigo": "P009",
            "descripcion": "Leche Deslactosada 1L",
            "grupo": "Leches",
            "activo": True
        },
        {
            "codigo": "P010",
            "descripcion": "Queso Doble Crema 500g",
            "grupo": "Quesos",
            "activo": True
        },
        {
            "codigo": "P011",
            "descripcion": "Kumis Natural 1L",
            "grupo": "Derivados",
            "activo": False  # Este producto está desactivado
        },
        {
            "codigo": "P012",
            "descripcion": "Arequipe 250g",
            "grupo": "Derivados",
            "activo": True
        },
    ]

    # Crear DataFrame
    df = pd.DataFrame(datos)

    # Guardar a Excel
    archivo = "productos_ejemplo.xlsx"
    df.to_excel(archivo, index=False, sheet_name="Productos")

    print(f"Archivo generado exitosamente: {archivo}")
    print(f"\nEstadísticas del archivo:")
    print(f"- Total de productos: {len(datos)}")
    print(f"- Productos activos: {sum(1 for p in datos if p['activo'])}")
    print(f"- Productos inactivos: {sum(1 for p in datos if not p['activo'])}")
    print(f"\nGrupos:")
    grupos = {}
    for producto in datos:
        grupo = producto['grupo']
        grupos[grupo] = grupos.get(grupo, 0) + 1
    for grupo, cantidad in grupos.items():
        print(f"  - {grupo}: {cantidad}")
    print(f"\nPuede usar este archivo para importar productos a la aplicación.")


if __name__ == "__main__":
    generar_excel_productos()
