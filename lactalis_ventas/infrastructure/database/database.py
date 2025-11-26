"""Gestor de base de datos SQLite."""
import sqlite3
from typing import Optional
from pathlib import Path


class Database:
    """Gestor de base de datos SQLite."""

    def __init__(self, db_path: str = "lactalis.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def conectar(self) -> sqlite3.Connection:
        """Conecta a la base de datos."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def cerrar(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def inicializar_esquema(self) -> None:
        """Inicializa el esquema de la base de datos."""
        conn = self.conectar()
        cursor = conn.cursor()

        # Tabla productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                descripcion TEXT NOT NULL,
                grupo TEXT NOT NULL,
                se_registra INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Tabla terceros
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS terceros (
                identificador_unico TEXT PRIMARY KEY,
                cod_padre TEXT NOT NULL,
                nombre TEXT NOT NULL,
                nit TEXT NOT NULL,
                se_registra INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Migrar datos existentes si es necesario
        # Verificar si la tabla existe y tiene el formato antiguo
        cursor.execute("""
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='terceros'
        """)
        table_info = cursor.fetchone()
        if table_info and 'identificador_unico' not in table_info[0]:
            # La tabla existe pero no tiene identificador_unico, migrar
            cursor.execute("""
                CREATE TABLE terceros_new (
                    identificador_unico TEXT PRIMARY KEY,
                    cod_padre TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    nit TEXT NOT NULL,
                    se_registra INTEGER NOT NULL DEFAULT 1
                )
            """)
            cursor.execute("""
                INSERT INTO terceros_new (identificador_unico, cod_padre, nombre, nit, se_registra)
                SELECT cod_padre as identificador_unico, cod_padre, nombre, nit, se_registra
                FROM terceros
            """)
            cursor.execute("DROP TABLE terceros")
            cursor.execute("ALTER TABLE terceros_new RENAME TO terceros")
            print("Tabla terceros migrada exitosamente con campo identificador_unico")

        # Tabla facturas (líneas procesadas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facturas_procesadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT NOT NULL,
                fecha TEXT NOT NULL,
                anulada TEXT,
                cod_padre TEXT NOT NULL,
                nombre_tercero TEXT NOT NULL,
                nit TEXT NOT NULL,
                codigo_producto TEXT NOT NULL,
                descripcion_producto TEXT NOT NULL,
                grupo_producto TEXT NOT NULL,
                cantidad REAL NOT NULL,
                valor_neto REAL NOT NULL,
                fue_registrada INTEGER NOT NULL DEFAULT 1,
                motivo_rechazo TEXT,
                fecha_procesamiento TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrar tabla facturas si es necesario
        cursor.execute("""
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='facturas_procesadas'
        """)
        table_info = cursor.fetchone()
        if table_info and 'anulada' not in table_info[0]:
            # La tabla existe pero no tiene anulada, migrar
            cursor.execute("""
                CREATE TABLE facturas_procesadas_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    anulada TEXT,
                    cod_padre TEXT NOT NULL,
                    nombre_tercero TEXT NOT NULL,
                    nit TEXT NOT NULL,
                    codigo_producto TEXT NOT NULL,
                    descripcion_producto TEXT NOT NULL,
                    grupo_producto TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    valor_neto REAL NOT NULL,
                    fue_registrada INTEGER NOT NULL DEFAULT 1,
                    motivo_rechazo TEXT,
                    fecha_procesamiento TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                INSERT INTO facturas_procesadas_new
                (id, numero_factura, fecha, anulada, cod_padre, nombre_tercero, nit,
                 codigo_producto, descripcion_producto, grupo_producto, cantidad,
                 valor_neto, fue_registrada, motivo_rechazo, fecha_procesamiento)
                SELECT id, numero_factura, fecha, '' as anulada, cod_padre, nombre_tercero, nit,
                 codigo_producto, descripcion_producto, grupo_producto, cantidad,
                 valor_neto, fue_registrada, motivo_rechazo, fecha_procesamiento
                FROM facturas_procesadas
            """)
            cursor.execute("DROP TABLE facturas_procesadas")
            cursor.execute("ALTER TABLE facturas_procesadas_new RENAME TO facturas_procesadas")
            print("Tabla facturas_procesadas migrada exitosamente con campo anulada")

        # Índices para mejorar rendimiento
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_productos_descripcion
            ON productos(descripcion)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_terceros_nombre
            ON terceros(nombre)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facturas_numero
            ON facturas_procesadas(numero_factura)
        """)

        conn.commit()

    def ejecutar_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Ejecuta una query SQL."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor

    def ejecutar_many(self, query: str, params_list: list) -> None:
        """Ejecuta una query SQL múltiples veces."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()

    def commit(self) -> None:
        """Confirma los cambios en la base de datos."""
        if self.connection:
            self.connection.commit()

    def __enter__(self):
        """Soporte para context manager."""
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        self.cerrar()
