# Lactalis - Procesador de Facturas

Aplicación de escritorio Python con PyQt6 para procesar facturas Excel de Lactalis, desarrollada con Clean Architecture.

## Características

- **Procesamiento de facturas**: Carga y procesa archivos Excel aplicando reglas de negocio
- **Gestión de productos**: Visualiza, busca y activa/desactiva productos
- **Gestión de terceros**: Visualiza, busca y activa/desactiva terceros (clientes/proveedores)
- **Estadísticas**: Muestra información y estadísticas de las facturas procesadas
- **Base de datos SQLite**: Almacenamiento persistente de productos, terceros y facturas
- **Interfaz moderna**: UI intuitiva con PyQt6 y 4 pestañas funcionales

## Reglas de Negocio

### 1. Validación de Número de Factura
- Solo se procesan facturas cuyo número empiece con "Factura"
- Ejemplos válidos: `Factura001`, `Factura-2024-001`
- Ejemplos inválidos: `FAC001`, `Invoice001`

### 2. Validación de Valor Neto
- El valor neto debe ser estrictamente mayor que 0
- Se rechazan valores negativos y valores igual a 0

### 3. Productos a Depurar (no registrar)
- Crema de leche
- Leche en polvo
- Leche líquida

Cualquier producto cuya descripción contenga estos términos será rechazado automáticamente.

### 4. Validación de Estado
- Los productos deben estar activos (`se_registra = True`)
- Los terceros deben estar activos (`se_registra = True`)
- Puede activar/desactivar desde las pestañas correspondientes

### 5. Creación Automática
- Si un producto no existe en la BD, se crea automáticamente
- Si un tercero no existe en la BD, se crea automáticamente
- Los nuevos registros se crean con estado activo por defecto

## Arquitectura

El proyecto sigue Clean Architecture con las siguientes capas:

```
lactalis_ventas/
├── domain/                     # Capa de Dominio
│   ├── entities/              # Entidades del negocio
│   │   ├── producto.py
│   │   ├── tercero.py
│   │   └── factura.py
│   ├── value_objects/         # Objetos de valor
│   │   └── resultado_procesamiento.py
│   └── repositories/          # Interfaces de repositorios
│       ├── producto_repository.py
│       ├── tercero_repository.py
│       └── factura_repository.py
│
├── application/               # Capa de Aplicación
│   └── use_cases/            # Casos de uso
│       ├── procesar_facturas.py
│       ├── gestionar_productos.py
│       ├── gestionar_terceros.py
│       └── obtener_estadisticas.py
│
├── infrastructure/           # Capa de Infraestructura
│   ├── database/            # Implementaciones con SQLite
│   │   ├── database.py
│   │   ├── producto_repository_impl.py
│   │   ├── tercero_repository_impl.py
│   │   └── factura_repository_impl.py
│   └── excel/              # Procesamiento de Excel
│       └── excel_processor.py
│
└── presentation/            # Capa de Presentación
    ├── main_window.py      # Ventana principal
    └── tabs/               # Pestañas de la UI
        ├── procesar_excel_tab.py
        ├── productos_tab.py
        ├── terceros_tab.py
        └── informacion_tab.py
```

## Requisitos

- Python 3.9 o superior
- PyQt6
- pandas
- openpyxl

## Instalación

1. Clonar el repositorio o descargar el código:
```bash
cd lactalis-ventas
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Ejecutar los tests

```bash
python test_sistema.py
```

O con pytest:
```bash
pytest test_sistema.py -v
```

## Formato del Archivo Excel

El archivo Excel debe contener las siguientes columnas (en cualquier orden):

- **numero_factura** / factura / nro_factura: Número de la factura
- **fecha** / fecha_factura: Fecha de la factura
- **cod_padre** / código padre: Código del tercero
- **nombre_tercero** / tercero / cliente: Nombre del tercero
- **nit** / identificación: NIT del tercero
- **codigo_producto** / código producto: Código del producto
- **descripcion_producto** / descripción producto / producto: Descripción del producto
- **grupo_producto** / grupo / categoría: Grupo del producto
- **cantidad** / qty / unidades: Cantidad
- **valor_neto** / valor neto / total / valor: Valor neto de la línea

El procesador reconoce automáticamente las columnas por sus variantes.

### Formato del Archivo Excel de Productos

Para importar productos, el archivo Excel debe contener las siguientes columnas (en cualquier orden):

- **codigo** / código / codigo_producto: Código del producto (requerido)
- **descripcion** / descripción / nombre / producto: Descripción del producto (requerido)
- **grupo** / categoria / categoría / tipo: Grupo del producto (opcional, por defecto: "General")
- **activo** / se_registra / estado: Estado del producto (opcional, por defecto: True)

Ejemplo: Ejecute `python generar_excel_productos_ejemplo.py` para generar un archivo de ejemplo.

### Formato del Archivo Excel de Terceros

Para importar terceros, el archivo Excel debe contener las siguientes columnas (en cualquier orden):

- **cod_padre** / código padre / codigo: Código del tercero (requerido)
- **nombre** / razon_social / cliente: Nombre del tercero (requerido)
- **nit** / identificación / documento: NIT del tercero (requerido)
- **activo** / se_registra / estado: Estado del tercero (opcional, por defecto: True)

Ejemplo: Ejecute `python generar_excel_terceros_ejemplo.py` para generar un archivo de ejemplo.

## Base de Datos

La aplicación crea automáticamente una base de datos SQLite (`lactalis.db`) con las siguientes tablas:

### Tabla `productos`
- `codigo` (TEXT, PRIMARY KEY): Código del producto
- `descripcion` (TEXT): Descripción del producto
- `grupo` (TEXT): Grupo al que pertenece
- `se_registra` (INTEGER): Estado (1=activo, 0=inactivo)

### Tabla `terceros`
- `cod_padre` (TEXT, PRIMARY KEY): Código padre del tercero
- `nombre` (TEXT): Nombre del tercero
- `nit` (TEXT): NIT del tercero
- `se_registra` (INTEGER): Estado (1=activo, 0=inactivo)

### Tabla `facturas_procesadas`
- `id` (INTEGER, PRIMARY KEY): ID autoincremental
- `numero_factura` (TEXT): Número de factura
- `fecha` (TEXT): Fecha de la factura
- `cod_padre` (TEXT): Código del tercero
- `nombre_tercero` (TEXT): Nombre del tercero
- `nit` (TEXT): NIT del tercero
- `codigo_producto` (TEXT): Código del producto
- `descripcion_producto` (TEXT): Descripción del producto
- `grupo_producto` (TEXT): Grupo del producto
- `cantidad` (REAL): Cantidad
- `valor_neto` (REAL): Valor neto
- `fue_registrada` (INTEGER): Si fue registrada (1) o rechazada (0)
- `motivo_rechazo` (TEXT): Motivo de rechazo si aplica
- `fecha_procesamiento` (TEXT): Timestamp del procesamiento

## Interfaz de Usuario

### Pestaña 1: Procesar Excel
- Seleccionar archivo Excel
- Procesar facturas aplicando las reglas de negocio
- Ver resultados: líneas registradas y rechazadas con motivos

### Pestaña 2: Productos
- Listar todos los productos
- Buscar productos por código, descripción o grupo
- Activar/desactivar productos
- **Importar productos desde Excel**
- Ver estadísticas (total, activos, inactivos)

### Pestaña 3: Terceros
- Listar todos los terceros
- Buscar terceros por código, nombre o NIT
- Activar/desactivar terceros
- **Importar terceros desde Excel**
- Ver estadísticas (total, activos, inactivos)

### Pestaña 4: Información
- Ver reglas de negocio completas
- Ver estadísticas de facturas procesadas:
  - Total de líneas procesadas
  - Valor neto total
  - Productos únicos
  - Terceros únicos
  - Rango de fechas

## Desarrollo

### Ejecutar tests con cobertura

```bash
pytest test_sistema.py --cov=lactalis_ventas --cov-report=html
```

### Estructura de tests

Los tests cubren:
- **TestEntidades**: Validaciones de entidades del dominio
- **TestRepositorios**: Operaciones CRUD en la base de datos
- **TestCasosDeUso**: Lógica de negocio y reglas de procesamiento

## Licencia

Este proyecto es privado y confidencial para uso exclusivo de Lactalis.

## Autor

Desarrollado con Clean Architecture, MVVM y las mejores prácticas de Python.

## Notas Técnicas

- **Patrón Repository**: Abstracción de la capa de datos
- **Dataclasses**: Para entidades simples y legibles
- **Type Hints**: Para mejor mantenibilidad
- **Procesamiento en thread**: Para no bloquear la UI
- **Validaciones en el dominio**: Reglas de negocio centralizadas
- **Separación de responsabilidades**: Cada capa tiene un propósito claro
