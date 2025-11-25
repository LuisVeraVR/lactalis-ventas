"""Ventana principal de la aplicación."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from lactalis_ventas.infrastructure.database.database import Database
from lactalis_ventas.infrastructure.database.producto_repository_impl import ProductoRepositoryImpl
from lactalis_ventas.infrastructure.database.tercero_repository_impl import TerceroRepositoryImpl
from lactalis_ventas.infrastructure.database.factura_repository_impl import FacturaRepositoryImpl
from lactalis_ventas.infrastructure.excel.excel_processor import ExcelProcessor
from lactalis_ventas.application.use_cases.procesar_facturas import ProcesarFacturasUseCase
from lactalis_ventas.application.use_cases.gestionar_productos import (
    ListarProductosUseCase, BuscarProductosUseCase, CambiarEstadoProductoUseCase
)
from lactalis_ventas.application.use_cases.gestionar_terceros import (
    ListarTercerosUseCase, BuscarTercerosUseCase, CambiarEstadoTerceroUseCase
)
from lactalis_ventas.application.use_cases.obtener_estadisticas import ObtenerEstadisticasUseCase
from lactalis_ventas.presentation.tabs.procesar_excel_tab import ProcesarExcelTab
from lactalis_ventas.presentation.tabs.productos_tab import ProductosTab
from lactalis_ventas.presentation.tabs.terceros_tab import TercerosTab
from lactalis_ventas.presentation.tabs.informacion_tab import InformacionTab


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lactalis - Procesador de Facturas")
        self.setMinimumSize(1200, 800)

        # Inicializar base de datos
        self.database = Database("lactalis.db")
        self.database.conectar()
        self.database.inicializar_esquema()

        # Inicializar repositorios
        self.producto_repo = ProductoRepositoryImpl(self.database)
        self.tercero_repo = TerceroRepositoryImpl(self.database)
        self.factura_repo = FacturaRepositoryImpl(self.database)

        # Inicializar procesador de Excel
        self.excel_processor = ExcelProcessor()

        # Inicializar casos de uso
        self._inicializar_casos_uso()

        # Configurar UI
        self._configurar_ui()

    def _inicializar_casos_uso(self):
        """Inicializa los casos de uso."""
        # Casos de uso de facturas
        self.procesar_facturas_uc = ProcesarFacturasUseCase(
            self.producto_repo,
            self.tercero_repo,
            self.factura_repo
        )

        # Casos de uso de productos
        self.listar_productos_uc = ListarProductosUseCase(self.producto_repo)
        self.buscar_productos_uc = BuscarProductosUseCase(self.producto_repo)
        self.cambiar_estado_producto_uc = CambiarEstadoProductoUseCase(self.producto_repo)

        # Casos de uso de terceros
        self.listar_terceros_uc = ListarTercerosUseCase(self.tercero_repo)
        self.buscar_terceros_uc = BuscarTercerosUseCase(self.tercero_repo)
        self.cambiar_estado_tercero_uc = CambiarEstadoTerceroUseCase(self.tercero_repo)

        # Casos de uso de estadísticas
        self.obtener_estadisticas_uc = ObtenerEstadisticasUseCase(self.factura_repo)

    def _configurar_ui(self):
        """Configura la interfaz de usuario."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Procesar Excel
        self.procesar_tab = ProcesarExcelTab(
            self.excel_processor,
            self.procesar_facturas_uc
        )
        self.tabs.addTab(self.procesar_tab, "📄 Procesar Excel")

        # Tab 2: Productos
        self.productos_tab = ProductosTab(
            self.listar_productos_uc,
            self.buscar_productos_uc,
            self.cambiar_estado_producto_uc
        )
        self.tabs.addTab(self.productos_tab, "📦 Productos")

        # Tab 3: Terceros
        self.terceros_tab = TercerosTab(
            self.listar_terceros_uc,
            self.buscar_terceros_uc,
            self.cambiar_estado_tercero_uc
        )
        self.tabs.addTab(self.terceros_tab, "👥 Terceros")

        # Tab 4: Información
        self.informacion_tab = InformacionTab(self.obtener_estadisticas_uc)
        self.tabs.addTab(self.informacion_tab, "ℹ️ Información")

        # Conectar señales
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        """Manejador de cambio de tab."""
        # Refrescar datos cuando cambiamos de tab
        if index == 1:  # Tab Productos
            self.productos_tab.refrescar()
        elif index == 2:  # Tab Terceros
            self.terceros_tab.refrescar()
        elif index == 3:  # Tab Información
            self.informacion_tab.refrescar()

    def closeEvent(self, event):
        """Manejador de cierre de la ventana."""
        respuesta = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro que desea salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            # Cerrar base de datos
            self.database.cerrar()
            event.accept()
        else:
            event.ignore()
