"""Pestaña para gestionar productos."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt
from lactalis_ventas.application.use_cases.gestionar_productos import (
    ListarProductosUseCase, BuscarProductosUseCase, CambiarEstadoProductoUseCase
)


class ProductosTab(QWidget):
    """Pestaña para gestionar productos."""

    def __init__(
        self,
        listar_uc: ListarProductosUseCase,
        buscar_uc: BuscarProductosUseCase,
        cambiar_estado_uc: CambiarEstadoProductoUseCase
    ):
        super().__init__()
        self.listar_uc = listar_uc
        self.buscar_uc = buscar_uc
        self.cambiar_estado_uc = cambiar_estado_uc

        self._configurar_ui()
        self.refrescar()

    def _configurar_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("Gestión de Productos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(titulo)

        # Grupo de búsqueda
        grupo_busqueda = QGroupBox("Buscar productos")
        grupo_busqueda.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_busqueda = QHBoxLayout()

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por código, descripción o grupo...")
        self.txt_buscar.returnPressed.connect(self._buscar)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout_busqueda.addWidget(self.txt_buscar, 1)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self._buscar)
        btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout_busqueda.addWidget(btn_buscar)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self._limpiar_busqueda)
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        layout_busqueda.addWidget(btn_limpiar)

        grupo_busqueda.setLayout(layout_busqueda)
        layout.addWidget(grupo_busqueda)

        # Estadísticas
        self.label_stats = QLabel("")
        self.label_stats.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.label_stats)

        # Tabla de productos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Código", "Descripción", "Grupo", "Estado", "Acciones"
        ])

        # Configurar tabla
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.tabla, 1)

    def refrescar(self):
        """Refresca la lista de productos."""
        productos = self.listar_uc.ejecutar()
        self._actualizar_tabla(productos)

    def _buscar(self):
        """Busca productos."""
        termino = self.txt_buscar.text().strip()
        productos = self.buscar_uc.ejecutar(termino)
        self._actualizar_tabla(productos)

    def _limpiar_busqueda(self):
        """Limpia la búsqueda y muestra todos los productos."""
        self.txt_buscar.clear()
        self.refrescar()

    def _actualizar_tabla(self, productos):
        """Actualiza la tabla con los productos."""
        self.tabla.setRowCount(len(productos))

        activos = sum(1 for p in productos if p.se_registra)
        inactivos = len(productos) - activos
        self.label_stats.setText(
            f"Total: {len(productos)} productos | "
            f"Activos: {activos} | Inactivos: {inactivos}"
        )

        for i, producto in enumerate(productos):
            # Código
            item_codigo = QTableWidgetItem(producto.codigo)
            self.tabla.setItem(i, 0, item_codigo)

            # Descripción
            item_desc = QTableWidgetItem(producto.descripcion)
            self.tabla.setItem(i, 1, item_desc)

            # Grupo
            item_grupo = QTableWidgetItem(producto.grupo)
            self.tabla.setItem(i, 2, item_grupo)

            # Estado
            estado_text = "✓ Activo" if producto.se_registra else "✗ Inactivo"
            item_estado = QTableWidgetItem(estado_text)
            if producto.se_registra:
                item_estado.setForeground(Qt.GlobalColor.darkGreen)
            else:
                item_estado.setForeground(Qt.GlobalColor.red)
            self.tabla.setItem(i, 3, item_estado)

            # Acciones
            widget_acciones = QWidget()
            layout_acciones = QHBoxLayout(widget_acciones)
            layout_acciones.setContentsMargins(5, 2, 5, 2)

            if producto.se_registra:
                btn_accion = QPushButton("Desactivar")
                btn_accion.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                btn_accion.clicked.connect(
                    lambda checked, cod=producto.codigo: self._desactivar_producto(cod)
                )
            else:
                btn_accion = QPushButton("Activar")
                btn_accion.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
                btn_accion.clicked.connect(
                    lambda checked, cod=producto.codigo: self._activar_producto(cod)
                )

            layout_acciones.addWidget(btn_accion)
            layout_acciones.addStretch()

            self.tabla.setCellWidget(i, 4, widget_acciones)

    def _activar_producto(self, codigo: str):
        """Activa un producto."""
        try:
            self.cambiar_estado_uc.ejecutar(codigo, activar=True)
            self.refrescar()
            QMessageBox.information(
                self,
                "Producto activado",
                f"El producto {codigo} ha sido activado correctamente."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al activar el producto:\n\n{str(e)}"
            )

    def _desactivar_producto(self, codigo: str):
        """Desactiva un producto."""
        respuesta = QMessageBox.question(
            self,
            "Confirmar desactivación",
            f"¿Está seguro que desea desactivar el producto {codigo}?\n\n"
            "Las líneas de factura con este producto serán rechazadas en futuros procesamientos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.cambiar_estado_uc.ejecutar(codigo, activar=False)
                self.refrescar()
                QMessageBox.information(
                    self,
                    "Producto desactivado",
                    f"El producto {codigo} ha sido desactivado correctamente."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al desactivar el producto:\n\n{str(e)}"
                )
