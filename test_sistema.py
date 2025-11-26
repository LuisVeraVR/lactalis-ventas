"""Tests del sistema Lactalis - Procesador de Facturas."""
import unittest
import tempfile
import os
from datetime import datetime
from decimal import Decimal
from lactalis_ventas.domain.entities.producto import Producto
from lactalis_ventas.domain.entities.tercero import Tercero
from lactalis_ventas.domain.entities.factura import FacturaLinea
from lactalis_ventas.infrastructure.database.database import Database
from lactalis_ventas.infrastructure.database.producto_repository_impl import ProductoRepositoryImpl
from lactalis_ventas.infrastructure.database.tercero_repository_impl import TerceroRepositoryImpl
from lactalis_ventas.infrastructure.database.factura_repository_impl import FacturaRepositoryImpl
from lactalis_ventas.application.use_cases.procesar_facturas import ProcesarFacturasUseCase
from lactalis_ventas.application.use_cases.gestionar_productos import (
    ListarProductosUseCase, BuscarProductosUseCase, CambiarEstadoProductoUseCase
)
from lactalis_ventas.application.use_cases.gestionar_terceros import (
    ListarTercerosUseCase, BuscarTercerosUseCase, CambiarEstadoTerceroUseCase
)


class TestEntidades(unittest.TestCase):
    """Tests de las entidades del dominio."""

    def test_crear_producto_valido(self):
        """Test: Crear producto válido."""
        producto = Producto(
            codigo="P001",
            descripcion="Yogurt Natural",
            grupo="Lácteos",
            se_registra=True
        )
        self.assertEqual(producto.codigo, "P001")
        self.assertEqual(producto.descripcion, "Yogurt Natural")
        self.assertTrue(producto.debe_registrarse())

    def test_producto_validaciones(self):
        """Test: Validaciones de producto."""
        with self.assertRaises(ValueError):
            Producto(codigo="", descripcion="Test", grupo="Test")

        with self.assertRaises(ValueError):
            Producto(codigo="P001", descripcion="", grupo="Test")

    def test_activar_desactivar_producto(self):
        """Test: Activar y desactivar producto."""
        producto = Producto("P001", "Test", "Grupo")
        self.assertTrue(producto.se_registra)

        producto.desactivar()
        self.assertFalse(producto.se_registra)

        producto.activar()
        self.assertTrue(producto.se_registra)

    def test_crear_tercero_valido(self):
        """Test: Crear tercero válido."""
        tercero = Tercero(
            identificador_unico="T001",
            cod_padre="COD001",
            nombre="Cliente Prueba",
            nit="123456789",
            se_registra=True
        )
        self.assertEqual(tercero.identificador_unico, "T001")
        self.assertEqual(tercero.cod_padre, "COD001")
        self.assertEqual(tercero.nombre, "Cliente Prueba")
        self.assertTrue(tercero.debe_registrarse())

    def test_crear_factura_linea_valida(self):
        """Test: Crear línea de factura válida."""
        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo Test",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )
        self.assertTrue(linea.es_valida())
        self.assertEqual(linea.numero_factura, "Factura001")

    def test_validacion_factura_numero(self):
        """Test: Validación de clase de factura."""
        linea = FacturaLinea(
            numero_factura="FAC001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Nota Crédito",  # No empieza con "Factura"
            cod_padre="T001",
            nombre_tercero="Cliente",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo Test",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )
        self.assertFalse(linea.es_valida())

    def test_validacion_valor_neto(self):
        """Test: Validación de valor neto."""
        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo Test",
            cantidad=Decimal("10"),
            valor_neto=Decimal("0")  # Valor neto = 0
        )
        self.assertFalse(linea.es_valida())


class TestRepositorios(unittest.TestCase):
    """Tests de los repositorios."""

    def setUp(self):
        """Configuración antes de cada test."""
        # Crear base de datos temporal
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.database = Database(self.db_path)
        self.database.conectar()
        self.database.inicializar_esquema()

        # Inicializar repositorios
        self.producto_repo = ProductoRepositoryImpl(self.database)
        self.tercero_repo = TerceroRepositoryImpl(self.database)
        self.factura_repo = FacturaRepositoryImpl(self.database)

    def tearDown(self):
        """Limpieza después de cada test."""
        self.database.cerrar()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_guardar_y_obtener_producto(self):
        """Test: Guardar y obtener producto."""
        producto = Producto("P001", "Yogurt", "Lácteos")
        self.producto_repo.guardar(producto)

        producto_obtenido = self.producto_repo.obtener_por_codigo("P001")
        self.assertIsNotNone(producto_obtenido)
        self.assertEqual(producto_obtenido.codigo, "P001")
        self.assertEqual(producto_obtenido.descripcion, "Yogurt")

    def test_listar_productos(self):
        """Test: Listar productos."""
        producto1 = Producto("P001", "Yogurt", "Lácteos")
        producto2 = Producto("P002", "Queso", "Lácteos")

        self.producto_repo.guardar(producto1)
        self.producto_repo.guardar(producto2)

        productos = self.producto_repo.obtener_todos()
        self.assertEqual(len(productos), 2)

    def test_buscar_productos(self):
        """Test: Buscar productos."""
        producto1 = Producto("P001", "Yogurt Natural", "Lácteos")
        producto2 = Producto("P002", "Queso Fresco", "Lácteos")

        self.producto_repo.guardar(producto1)
        self.producto_repo.guardar(producto2)

        resultados = self.producto_repo.buscar("Yogurt")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].codigo, "P001")

    def test_actualizar_producto(self):
        """Test: Actualizar producto."""
        producto = Producto("P001", "Yogurt", "Lácteos")
        self.producto_repo.guardar(producto)

        producto.desactivar()
        self.producto_repo.actualizar(producto)

        producto_actualizado = self.producto_repo.obtener_por_codigo("P001")
        self.assertFalse(producto_actualizado.se_registra)

    def test_guardar_y_obtener_tercero(self):
        """Test: Guardar y obtener tercero."""
        tercero = Tercero("T001", "COD001", "Cliente Test", "123456789")
        self.tercero_repo.guardar(tercero)

        tercero_obtenido = self.tercero_repo.obtener_por_identificador("T001")
        self.assertIsNotNone(tercero_obtenido)
        self.assertEqual(tercero_obtenido.identificador_unico, "T001")
        self.assertEqual(tercero_obtenido.cod_padre, "COD001")

    def test_guardar_lineas_factura(self):
        """Test: Guardar líneas de factura."""
        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto",
            grupo_producto="Grupo",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00"),
            fue_registrada=True
        )

        self.factura_repo.guardar_lineas([linea])

        lineas = self.factura_repo.obtener_todas_lineas()
        self.assertEqual(len(lineas), 1)
        self.assertEqual(lineas[0].numero_factura, "Factura001")


class TestCasosDeUso(unittest.TestCase):
    """Tests de los casos de uso."""

    def setUp(self):
        """Configuración antes de cada test."""
        # Crear base de datos temporal
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.database = Database(self.db_path)
        self.database.conectar()
        self.database.inicializar_esquema()

        # Inicializar repositorios
        self.producto_repo = ProductoRepositoryImpl(self.database)
        self.tercero_repo = TerceroRepositoryImpl(self.database)
        self.factura_repo = FacturaRepositoryImpl(self.database)

        # Inicializar casos de uso
        self.procesar_facturas_uc = ProcesarFacturasUseCase(
            self.producto_repo,
            self.tercero_repo,
            self.factura_repo
        )

    def tearDown(self):
        """Limpieza después de cada test."""
        self.database.cerrar()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_procesar_factura_valida(self):
        """Test: Procesar factura válida."""
        # Crear producto y tercero primero
        producto = Producto("P001", "Yogurt Natural", "Lácteos")
        self.producto_repo.guardar(producto)

        tercero = Tercero("T001", "COD001", "Cliente Test", "123456789")
        self.tercero_repo.guardar(tercero)

        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Yogurt Natural",
            grupo_producto="Lácteos",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        self.assertEqual(resultado.total_lineas, 1)
        self.assertEqual(resultado.lineas_procesadas, 1)
        self.assertEqual(resultado.lineas_rechazadas, 0)

    def test_rechazar_factura_sin_prefijo(self):
        """Test: Rechazar factura sin prefijo 'Factura'."""
        linea = FacturaLinea(
            numero_factura="FAC001",  # No empieza con "Factura"
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        self.assertEqual(resultado.lineas_procesadas, 0)
        self.assertEqual(resultado.lineas_rechazadas, 1)

    def test_rechazar_valor_neto_cero(self):
        """Test: Rechazar factura con valor neto cero."""
        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo",
            cantidad=Decimal("10"),
            valor_neto=Decimal("0")  # Valor neto = 0
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        self.assertEqual(resultado.lineas_procesadas, 0)
        self.assertEqual(resultado.lineas_rechazadas, 1)

    def test_rechazar_producto_depurar(self):
        """Test: Rechazar productos que no existen en BD."""
        # Crear tercero pero NO crear el producto
        tercero = Tercero("T001", "COD001", "Cliente Test", "123456789")
        self.tercero_repo.guardar(tercero)

        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",  # Producto que no existe en BD
            descripcion_producto="Producto Test",
            grupo_producto="Lácteos",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        self.assertEqual(resultado.lineas_procesadas, 0)
        self.assertEqual(resultado.lineas_rechazadas, 1)

    def test_rechazar_producto_desactivado(self):
        """Test: Rechazar producto desactivado."""
        # Crear tercero activo
        tercero = Tercero("T001", "COD001", "Cliente Test", "123456789")
        self.tercero_repo.guardar(tercero)

        # Crear y desactivar producto
        producto = Producto("P001", "Producto Test", "Grupo")
        producto.desactivar()
        self.producto_repo.guardar(producto)

        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        self.assertEqual(resultado.lineas_procesadas, 0)
        self.assertEqual(resultado.lineas_rechazadas, 1)

    def test_rechazar_tercero_desactivado(self):
        """Test: Rechazar tercero desactivado."""
        # Crear producto activo
        producto = Producto("P001", "Producto Test", "Grupo")
        self.producto_repo.guardar(producto)

        # Crear y desactivar tercero
        tercero = Tercero("T001", "COD001", "Cliente Test", "123456789")
        tercero.desactivar()
        self.tercero_repo.guardar(tercero)

        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T001",
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        self.assertEqual(resultado.lineas_procesadas, 0)
        self.assertEqual(resultado.lineas_rechazadas, 1)

    def test_crear_producto_automaticamente(self):
        """Test: Rechazar cuando tercero no existe en BD."""
        # Crear producto pero NO crear el tercero
        producto = Producto("P001", "Producto Test", "Grupo")
        self.producto_repo.guardar(producto)

        linea = FacturaLinea(
            numero_factura="Factura001",
            fecha=datetime.now(),
            anulada="",
            clase_factura="Factura",
            cod_padre="T999",  # Tercero que no existe en BD
            nombre_tercero="Cliente Test",
            nit="123456789",
            codigo_producto="P001",
            descripcion_producto="Producto Test",
            grupo_producto="Grupo",
            cantidad=Decimal("10"),
            valor_neto=Decimal("1000.00")
        )

        resultado = self.procesar_facturas_uc.ejecutar([linea])

        # Verificar que se rechazó
        self.assertEqual(resultado.lineas_procesadas, 0)
        self.assertEqual(resultado.lineas_rechazadas, 1)


def suite():
    """Crea la suite de tests."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntidades))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRepositorios))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCasosDeUso))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
