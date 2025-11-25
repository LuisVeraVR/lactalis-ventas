"""Implementación del repositorio de productos con SQLite."""
from typing import List, Optional
from lactalis_ventas.domain.entities.producto import Producto
from lactalis_ventas.domain.repositories.producto_repository import ProductoRepository
from lactalis_ventas.infrastructure.database.database import Database


class ProductoRepositoryImpl(ProductoRepository):
    """Implementación del repositorio de productos con SQLite."""

    def __init__(self, database: Database):
        self.db = database

    def obtener_todos(self) -> List[Producto]:
        """Obtiene todos los productos."""
        cursor = self.db.ejecutar_query("SELECT * FROM productos ORDER BY descripcion")
        rows = cursor.fetchall()
        return [self._row_to_producto(row) for row in rows]

    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código."""
        cursor = self.db.ejecutar_query(
            "SELECT * FROM productos WHERE codigo = ?",
            (codigo,)
        )
        row = cursor.fetchone()
        return self._row_to_producto(row) if row else None

    def guardar(self, producto: Producto) -> None:
        """Guarda un producto."""
        self.db.ejecutar_query(
            """
            INSERT OR REPLACE INTO productos (codigo, descripcion, grupo, se_registra)
            VALUES (?, ?, ?, ?)
            """,
            (
                producto.codigo,
                producto.descripcion,
                producto.grupo,
                1 if producto.se_registra else 0
            )
        )
        self.db.commit()

    def actualizar(self, producto: Producto) -> None:
        """Actualiza un producto."""
        self.db.ejecutar_query(
            """
            UPDATE productos
            SET descripcion = ?, grupo = ?, se_registra = ?
            WHERE codigo = ?
            """,
            (
                producto.descripcion,
                producto.grupo,
                1 if producto.se_registra else 0,
                producto.codigo
            )
        )
        self.db.commit()

    def buscar(self, termino: str) -> List[Producto]:
        """Busca productos por término."""
        cursor = self.db.ejecutar_query(
            """
            SELECT * FROM productos
            WHERE codigo LIKE ? OR descripcion LIKE ? OR grupo LIKE ?
            ORDER BY descripcion
            """,
            (f"%{termino}%", f"%{termino}%", f"%{termino}%")
        )
        rows = cursor.fetchall()
        return [self._row_to_producto(row) for row in rows]

    def obtener_por_grupo(self, grupo: str) -> List[Producto]:
        """Obtiene productos por grupo."""
        cursor = self.db.ejecutar_query(
            "SELECT * FROM productos WHERE grupo = ? ORDER BY descripcion",
            (grupo,)
        )
        rows = cursor.fetchall()
        return [self._row_to_producto(row) for row in rows]

    def _row_to_producto(self, row) -> Producto:
        """Convierte una fila de la BD a un objeto Producto."""
        return Producto(
            codigo=row["codigo"],
            descripcion=row["descripcion"],
            grupo=row["grupo"],
            se_registra=bool(row["se_registra"])
        )
