"""Caso de uso para importar productos desde Excel."""
from typing import List
from dataclasses import dataclass
from lactalis_ventas.domain.entities.producto import Producto
from lactalis_ventas.domain.repositories.producto_repository import ProductoRepository


@dataclass
class ResultadoImportacionProductos:
    """Resultado de la importación de productos."""

    total_leidos: int = 0
    productos_nuevos: int = 0
    productos_actualizados: int = 0
    productos_ignorados: int = 0
    errores: List[str] = None

    def __post_init__(self):
        if self.errores is None:
            self.errores = []

    def obtener_resumen(self) -> str:
        """Obtiene un resumen de la importación."""
        return (
            f"Total leídos: {self.total_leidos}\n"
            f"Nuevos: {self.productos_nuevos}\n"
            f"Actualizados: {self.productos_actualizados}\n"
            f"Ignorados: {self.productos_ignorados}\n"
            f"Errores: {len(self.errores)}"
        )


class ImportarProductosUseCase:
    """Caso de uso para importar productos desde Excel."""

    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def ejecutar(self, productos: List[Producto], actualizar_existentes: bool = True) -> ResultadoImportacionProductos:
        """
        Importa productos desde una lista.

        Args:
            productos: Lista de productos a importar
            actualizar_existentes: Si es True, actualiza productos existentes. Si es False, los ignora.

        Returns:
            ResultadoImportacionProductos con el resultado de la importación
        """
        resultado = ResultadoImportacionProductos(total_leidos=len(productos))

        for producto in productos:
            try:
                # Verificar si el producto ya existe
                producto_existente = self.producto_repo.obtener_por_codigo(producto.codigo)

                if producto_existente:
                    if actualizar_existentes:
                        # Actualizar producto existente
                        self.producto_repo.actualizar(producto)
                        resultado.productos_actualizados += 1
                    else:
                        # Ignorar producto existente
                        resultado.productos_ignorados += 1
                else:
                    # Crear nuevo producto
                    self.producto_repo.guardar(producto)
                    resultado.productos_nuevos += 1

            except Exception as e:
                resultado.errores.append(f"Error con producto {producto.codigo}: {str(e)}")

        return resultado
