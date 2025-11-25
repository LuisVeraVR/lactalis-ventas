"""Script para generar un archivo Excel de ejemplo para probar el sistema."""
import pandas as pd
from datetime import datetime, timedelta


def generar_excel_ejemplo():
    """Genera un archivo Excel de ejemplo con datos de prueba."""

    # Datos de ejemplo
    datos = [
        # Líneas válidas
        {
            "numero_factura": "Factura001",
            "fecha": datetime.now() - timedelta(days=5),
            "cod_padre": "T001",
            "nombre_tercero": "Supermercado La Canasta",
            "nit": "900123456-1",
            "codigo_producto": "P001",
            "descripcion_producto": "Yogurt Natural 1L",
            "grupo_producto": "Yogurt",
            "cantidad": 50,
            "valor_neto": 125000.00
        },
        {
            "numero_factura": "Factura002",
            "fecha": datetime.now() - timedelta(days=4),
            "cod_padre": "T002",
            "nombre_tercero": "Tienda El Ahorro",
            "nit": "800234567-2",
            "codigo_producto": "P002",
            "descripcion_producto": "Queso Campesino 500g",
            "grupo_producto": "Quesos",
            "cantidad": 30,
            "valor_neto": 90000.00
        },
        {
            "numero_factura": "Factura003",
            "fecha": datetime.now() - timedelta(days=3),
            "cod_padre": "T001",
            "nombre_tercero": "Supermercado La Canasta",
            "nit": "900123456-1",
            "codigo_producto": "P003",
            "descripcion_producto": "Mantequilla 250g",
            "grupo_producto": "Derivados",
            "cantidad": 20,
            "valor_neto": 48000.00
        },
        {
            "numero_factura": "Factura004",
            "fecha": datetime.now() - timedelta(days=2),
            "cod_padre": "T003",
            "nombre_tercero": "Distribuidora Los Andes",
            "nit": "700345678-3",
            "codigo_producto": "P004",
            "descripcion_producto": "Yogurt Griego 150g",
            "grupo_producto": "Yogurt",
            "cantidad": 100,
            "valor_neto": 180000.00
        },

        # Línea con valor neto = 0 (será rechazada)
        {
            "numero_factura": "Factura005",
            "fecha": datetime.now() - timedelta(days=1),
            "cod_padre": "T002",
            "nombre_tercero": "Tienda El Ahorro",
            "nit": "800234567-2",
            "codigo_producto": "P005",
            "descripcion_producto": "Producto Promocional",
            "grupo_producto": "Promociones",
            "cantidad": 10,
            "valor_neto": 0.00  # Será rechazada
        },

        # Línea sin prefijo "Factura" (será rechazada)
        {
            "numero_factura": "FAC006",  # Será rechazada
            "fecha": datetime.now(),
            "cod_padre": "T003",
            "nombre_tercero": "Distribuidora Los Andes",
            "nit": "700345678-3",
            "codigo_producto": "P006",
            "descripcion_producto": "Queso Mozzarella 1kg",
            "grupo_producto": "Quesos",
            "cantidad": 15,
            "valor_neto": 75000.00
        },

        # Línea con producto a depurar (será rechazada)
        {
            "numero_factura": "Factura007",
            "fecha": datetime.now(),
            "cod_padre": "T001",
            "nombre_tercero": "Supermercado La Canasta",
            "nit": "900123456-1",
            "codigo_producto": "P007",
            "descripcion_producto": "Crema de Leche 200ml",  # Será rechazada (producto a depurar)
            "grupo_producto": "Cremas",
            "cantidad": 25,
            "valor_neto": 50000.00
        },
        {
            "numero_factura": "Factura008",
            "fecha": datetime.now(),
            "cod_padre": "T002",
            "nombre_tercero": "Tienda El Ahorro",
            "nit": "800234567-2",
            "codigo_producto": "P008",
            "descripcion_producto": "Leche en Polvo 1kg",  # Será rechazada (producto a depurar)
            "grupo_producto": "Leches",
            "cantidad": 40,
            "valor_neto": 120000.00
        },

        # Más líneas válidas
        {
            "numero_factura": "Factura009",
            "fecha": datetime.now(),
            "cod_padre": "T004",
            "nombre_tercero": "Café Gourmet del Centro",
            "nit": "600456789-4",
            "codigo_producto": "P009",
            "descripcion_producto": "Queso Parmesano 200g",
            "grupo_producto": "Quesos",
            "cantidad": 12,
            "valor_neto": 72000.00
        },
        {
            "numero_factura": "Factura010",
            "fecha": datetime.now(),
            "cod_padre": "T004",
            "nombre_tercero": "Café Gourmet del Centro",
            "nit": "600456789-4",
            "codigo_producto": "P010",
            "descripcion_producto": "Yogurt Batido Fresa 1L",
            "grupo_producto": "Yogurt",
            "cantidad": 60,
            "valor_neto": 144000.00
        },
    ]

    # Crear DataFrame
    df = pd.DataFrame(datos)

    # Guardar a Excel
    archivo = "facturas_ejemplo.xlsx"
    df.to_excel(archivo, index=False, sheet_name="Facturas")

    print(f"Archivo generado exitosamente: {archivo}")
    print(f"\nEstadísticas del archivo:")
    print(f"- Total de líneas: {len(datos)}")
    print(f"- Líneas válidas esperadas: 6")
    print(f"- Líneas rechazadas esperadas: 4")
    print(f"  * 1 por valor neto = 0")
    print(f"  * 1 por no empezar con 'Factura'")
    print(f"  * 2 por productos a depurar (crema de leche, leche en polvo)")
    print(f"\nPuede usar este archivo para probar la aplicación.")


if __name__ == "__main__":
    generar_excel_ejemplo()
