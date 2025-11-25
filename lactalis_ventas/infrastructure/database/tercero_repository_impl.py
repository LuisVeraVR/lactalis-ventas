"""Implementación del repositorio de terceros con SQLite."""
from typing import List, Optional
from lactalis_ventas.domain.entities.tercero import Tercero
from lactalis_ventas.domain.repositories.tercero_repository import TerceroRepository
from lactalis_ventas.infrastructure.database.database import Database


class TerceroRepositoryImpl(TerceroRepository):
    """Implementación del repositorio de terceros con SQLite."""

    def __init__(self, database: Database):
        self.db = database

    def obtener_todos(self) -> List[Tercero]:
        """Obtiene todos los terceros."""
        cursor = self.db.ejecutar_query("SELECT * FROM terceros ORDER BY nombre")
        rows = cursor.fetchall()
        return [self._row_to_tercero(row) for row in rows]

    def obtener_por_cod_padre(self, cod_padre: str) -> Optional[Tercero]:
        """Obtiene un tercero por su código padre."""
        cursor = self.db.ejecutar_query(
            "SELECT * FROM terceros WHERE cod_padre = ?",
            (cod_padre,)
        )
        row = cursor.fetchone()
        return self._row_to_tercero(row) if row else None

    def guardar(self, tercero: Tercero) -> None:
        """Guarda un tercero."""
        self.db.ejecutar_query(
            """
            INSERT OR REPLACE INTO terceros (cod_padre, nombre, nit, se_registra)
            VALUES (?, ?, ?, ?)
            """,
            (
                tercero.cod_padre,
                tercero.nombre,
                tercero.nit,
                1 if tercero.se_registra else 0
            )
        )
        self.db.commit()

    def actualizar(self, tercero: Tercero) -> None:
        """Actualiza un tercero."""
        self.db.ejecutar_query(
            """
            UPDATE terceros
            SET nombre = ?, nit = ?, se_registra = ?
            WHERE cod_padre = ?
            """,
            (
                tercero.nombre,
                tercero.nit,
                1 if tercero.se_registra else 0,
                tercero.cod_padre
            )
        )
        self.db.commit()

    def buscar(self, termino: str) -> List[Tercero]:
        """Busca terceros por término."""
        cursor = self.db.ejecutar_query(
            """
            SELECT * FROM terceros
            WHERE cod_padre LIKE ? OR nombre LIKE ? OR nit LIKE ?
            ORDER BY nombre
            """,
            (f"%{termino}%", f"%{termino}%", f"%{termino}%")
        )
        rows = cursor.fetchall()
        return [self._row_to_tercero(row) for row in rows]

    def _row_to_tercero(self, row) -> Tercero:
        """Convierte una fila de la BD a un objeto Tercero."""
        return Tercero(
            cod_padre=row["cod_padre"],
            nombre=row["nombre"],
            nit=row["nit"],
            se_registra=bool(row["se_registra"])
        )
