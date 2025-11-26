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
        3. Factura no debe estar anulada (Anulada != 'X')
        4. Producto debe existir en BD (validar por codigo)
        5. Producto debe estar activo (se_registra=True)
        6. Tercero debe existir en BD (validar por identificador_unico = Cód.Padre)
        7. Tercero debe estar activo (se_registra=True)
        """
        resultado = ResultadoProcesamiento(total_lineas=len(lineas))

        for linea in lineas:
            try:
                # Reglas 1, 2 y 3: Se validan en el método es_valida() de FacturaLinea
                # (Factura empieza con "Factura", Valor neto > 0, No anulada)
                if not linea.es_valida():
                    motivo = "Factura inválida: "
                    if not linea.numero_factura.startswith("Factura"):
                        motivo += "no empieza con 'Factura'"
                    elif linea.valor_neto <= 0:
                        motivo += f"valor neto inválido ({linea.valor_neto})"
                    elif linea.anulada and str(linea.anulada).strip().upper() == "X":
                        motivo += "factura anulada"
                    else:
                        motivo += "no cumple reglas de negocio"

                    linea.marcar_como_rechazada(motivo)
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Regla 4 y 5: Verificar si el producto existe y está activo
                producto = self.producto_repo.obtener_por_codigo(linea.codigo_producto)
                if not producto:
                    linea.marcar_como_rechazada(
                        f"Producto no existe en BD: {linea.codigo_producto}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

                if not producto.debe_registrarse():
                    linea.marcar_como_rechazada(
                        f"Producto desactivado: {linea.codigo_producto}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

                # Regla 6 y 7: Verificar si el tercero existe y está activo
                # cod_padre en el Excel corresponde al identificador_unico del tercero en BD
                tercero = self.tercero_repo.obtener_por_identificador(linea.cod_padre)
                if not tercero:
                    linea.marcar_como_rechazada(
                        f"Tercero no existe en BD: {linea.cod_padre}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

                if not tercero.debe_registrarse():
                    linea.marcar_como_rechazada(
                        f"Tercero desactivado: {linea.cod_padre}"
                    )
                    resultado.agregar_linea_rechazada(linea)
                    continue

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
