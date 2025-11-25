"""Caso de uso para procesar facturas desde Excel."""
from typing import List
from lactalis_ventas.domain.entities.factura import FacturaLinea
from lactalis_ventas.domain.entities.producto import Producto
from lactalis_ventas.domain.entities.tercero import Tercero
from lactalis_ventas.domain.repositories.producto_repository import ProductoRepository
from lactalis_ventas.domain.repositories.tercero_repository import TerceroRepository
from lactalis_ventas.domain.repositories.factura_repository import FacturaRepository
from lactalis_ventas.domain.value_objects.resultado_procesamiento import ResultadoProcesamiento


class ProcesarFacturasUseCase:
    """Caso de uso para procesar facturas."""

    # Productos a depurar (no registrar)
    PRODUCTOS_DEPURAR = [
        "crema de leche",
        "leche en polvo",
        "leche líquida",
        "leche liquida"
    ]

    def __init__(
        self,
        producto_repo: ProductoRepository,
        tercero_repo: TerceroRepository,
        factura_repo: FacturaRepository
    ):
        self.producto_repo = producto_repo
        self.tercero_repo = tercero_repo
        self.factura_repo = factura_repo

    def ejecutar(self, lineas: List[FacturaLinea]) -> ResultadoProcesamiento:
        """
        Procesa las líneas de factura aplicando las reglas de negocio.

        Reglas:
        1. Solo facturas que empiecen con "Factura"
        2. Valor neto > 0
        3. Depurar: crema de leche, leche en polvo, leche líquida
        4. Producto debe estar activo (se_registra=True)
        5. Tercero debe estar activo (se_registra=True)
        """
        resultado = ResultadoProcesamiento(total_lineas=len(lineas))

        for linea in lineas:
            try:
                # Regla 1: Número de factura debe empezar con "Factura"
                if not linea.numero_factura.startswith("Factura"):
                    linea.marcar_como_rechazada("Factura no empieza con 'Factura'")
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Regla 2: Valor neto debe ser mayor que 0
                if linea.valor_neto <= 0:
                    linea.marcar_como_rechazada(f"Valor neto inválido: {linea.valor_neto}")
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Regla 3: Depurar productos específicos
                if self._es_producto_depurar(linea.descripcion_producto):
                    linea.marcar_como_rechazada(
                        f"Producto en lista de depuración: {linea.descripcion_producto}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Verificar si el producto debe registrarse
                producto = self.producto_repo.obtener_por_codigo(linea.codigo_producto)
                if producto and not producto.debe_registrarse():
                    linea.marcar_como_rechazada(
                        f"Producto desactivado: {linea.codigo_producto}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Si el producto no existe, crearlo
                if not producto:
                    producto = Producto(
                        codigo=linea.codigo_producto,
                        descripcion=linea.descripcion_producto,
                        grupo=linea.grupo_producto,
                        se_registra=True
                    )
                    self.producto_repo.guardar(producto)

                # Verificar si el tercero debe registrarse
                tercero = self.tercero_repo.obtener_por_cod_padre(linea.cod_padre)
                if tercero and not tercero.debe_registrarse():
                    linea.marcar_como_rechazada(
                        f"Tercero desactivado: {linea.cod_padre}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Si el tercero no existe, crearlo
                if not tercero:
                    tercero = Tercero(
                        cod_padre=linea.cod_padre,
                        nombre=linea.nombre_tercero,
                        nit=linea.nit,
                        se_registra=True
                    )
                    self.tercero_repo.guardar(tercero)

                # Si pasó todas las validaciones, marcar como registrada
                linea.marcar_como_registrada()
                resultado.agregar_linea_registrada(linea)

            except Exception as e:
                error_msg = f"Error procesando línea: {str(e)}"
                resultado.agregar_error(error_msg)
                linea.marcar_como_rechazada(error_msg)
                resultado.agregar_linea_rechazada(linea)

        # Guardar las líneas procesadas
        try:
            self.factura_repo.guardar_lineas(resultado.lineas_registradas)
        except Exception as e:
            resultado.agregar_error(f"Error guardando facturas: {str(e)}")

        return resultado

    def _es_producto_depurar(self, descripcion: str) -> bool:
        """Verifica si un producto debe ser depurado (no registrado)."""
        descripcion_lower = descripcion.lower().strip()
        return any(
            producto_depurar in descripcion_lower
            for producto_depurar in self.PRODUCTOS_DEPURAR
        )
