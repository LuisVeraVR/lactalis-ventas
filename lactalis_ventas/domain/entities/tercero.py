"""Entidad Tercero del dominio."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Tercero:
    """Representa un tercero (cliente/proveedor) en el sistema."""

    identificador_unico: str
    cod_padre: str
    nombre: str
    nit: str
    se_registra: bool = True

    def __post_init__(self):
        """Validaciones de negocio."""
        if not self.identificador_unico or not self.identificador_unico.strip():
            raise ValueError("El identificador único del tercero no puede estar vacío")
        if not self.cod_padre or not self.cod_padre.strip():
            raise ValueError("El código padre del tercero no puede estar vacío")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del tercero no puede estar vacío")
        if not self.nit or not self.nit.strip():
            raise ValueError("El NIT del tercero no puede estar vacío")

    def activar(self) -> None:
        """Activa el tercero para que se registre."""
        self.se_registra = True

    def desactivar(self) -> None:
        """Desactiva el tercero para que no se registre."""
        self.se_registra = False

    def debe_registrarse(self) -> bool:
        """Verifica si el tercero debe registrarse."""
        return self.se_registra
