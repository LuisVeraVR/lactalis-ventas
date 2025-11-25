"""Entidad Producto del dominio."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    """Representa un producto en el sistema."""

    codigo: str
    descripcion: str
    grupo: str
    se_registra: bool = True

    def __post_init__(self):
        """Validaciones de negocio."""
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código del producto no puede estar vacío")
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("La descripción del producto no puede estar vacía")
        if not self.grupo or not self.grupo.strip():
            raise ValueError("El grupo del producto no puede estar vacío")

    def activar(self) -> None:
        """Activa el producto para que se registre."""
        self.se_registra = True

    def desactivar(self) -> None:
        """Desactiva el producto para que no se registre."""
        self.se_registra = False

    def debe_registrarse(self) -> bool:
        """Verifica si el producto debe registrarse."""
        return self.se_registra
