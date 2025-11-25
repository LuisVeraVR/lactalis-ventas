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
                cod_padre TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                nit TEXT NOT NULL,
                se_registra INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Tabla facturas (líneas procesadas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facturas_procesadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT NOT NULL,
                fecha TEXT NOT NULL,
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
