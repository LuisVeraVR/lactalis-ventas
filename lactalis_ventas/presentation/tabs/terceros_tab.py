"""Pestana para gestionar terceros."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTableView, QMessageBox, QHeaderView, QGroupBox,
    QFileDialog, QApplication, QAbstractItemView
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor
from lactalis_ventas.application.use_cases.gestionar_terceros import (
    ListarTercerosUseCase, BuscarTercerosUseCase, CambiarEstadoTerceroUseCase
)
from lactalis_ventas.application.use_cases.importar_terceros import ImportarTercerosUseCase
from lactalis_ventas.infrastructure.excel.tercero_excel_processor import TerceroExcelProcessor
from lactalis_ventas.presentation.widgets.progress_dialog import ProgressDialog


class TerceroTableModel(QAbstractTableModel):
    """Modelo liviano para mostrar terceros sin crear miles de widgets."""

    HEADERS = ["Codigo Padre", "Nombre", "NIT", "Estado", "Accion"]

    def __init__(self, terceros):
        super().__init__()
        self._terceros = terceros

    def rowCount(self, parent=QModelIndex()):  # type: ignore[override]
        return len(self._terceros)

    def columnCount(self, parent=QModelIndex()):  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not (0 <= index.row() < len(self._terceros)):
            return None

        tercero = self._terceros[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return tercero.cod_padre
            if col == 1:
                return tercero.nombre
            if col == 2:
                return tercero.nit
            if col == 3:
                return "Activo" if tercero.se_registra else "Inactivo"
            if col == 4:
                return "Desactivar" if tercero.se_registra else "Activar"

        if role == Qt.ItemDataRole.ForegroundRole and col == 3:
            return QColor("darkgreen") if tercero.se_registra else QColor("red")

        if role == Qt.ItemDataRole.TextAlignmentRole and col in (0, 2, 3, 4):
            return Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_terceros(self, terceros):
        """Reemplaza los datos de manera eficiente."""
        self.beginResetModel()
        self._terceros = terceros
        self.endResetModel()

    def tercero_en_fila(self, row: int):
        if 0 <= row < len(self._terceros):
            return self._terceros[row]
        return None


class TercerosTab(QWidget):
    """Pestana para gestionar terceros."""

    def __init__(
        self,
        listar_uc: ListarTercerosUseCase,
        buscar_uc: BuscarTercerosUseCase,
        cambiar_estado_uc: CambiarEstadoTerceroUseCase,
        importar_uc: ImportarTercerosUseCase,
        excel_processor: TerceroExcelProcessor
    ):
        super().__init__()
        self.listar_uc = listar_uc
        self.buscar_uc = buscar_uc
        self.cambiar_estado_uc = cambiar_estado_uc
        self.importar_uc = importar_uc
        self.excel_processor = excel_processor

        self._configurar_ui()
        self.refrescar()

    def _configurar_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titulo
        titulo = QLabel("Gestion de Terceros")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(titulo)

        # Grupo de busqueda
        grupo_busqueda = QGroupBox("Buscar terceros")
        grupo_busqueda.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_busqueda = QHBoxLayout()

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por codigo, nombre o NIT...")
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

        btn_importar = QPushButton("Importar Excel")
        btn_importar.clicked.connect(self._importar_excel)
        btn_importar.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        layout_busqueda.addWidget(btn_importar)

        grupo_busqueda.setLayout(layout_busqueda)
        layout.addWidget(grupo_busqueda)

        # Estadisticas
        self.label_stats = QLabel("")
        self.label_stats.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.label_stats)

        # Tabla de terceros
        self.modelo = TerceroTableModel([])
        self.tabla = QTableView()
        self.tabla.setModel(self.modelo)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setStyleSheet("""
            QTableView {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.tabla.clicked.connect(self._on_tabla_click)

        layout.addWidget(self.tabla, 1)

    def refrescar(self):
        """Refresca la lista de terceros."""
        terceros = self.listar_uc.ejecutar()
        self._actualizar_tabla(terceros)

    def _buscar(self):
        """Busca terceros."""
        termino = self.txt_buscar.text().strip()
        terceros = self.buscar_uc.ejecutar(termino)
        self._actualizar_tabla(terceros)

    def _limpiar_busqueda(self):
        """Limpia la busqueda y muestra todos los terceros."""
        self.txt_buscar.clear()
        self.refrescar()

    def _actualizar_tabla(self, terceros):
        """Actualiza la tabla con los terceros."""
        self.modelo.set_terceros(terceros)

        activos = sum(1 for t in terceros if t.se_registra)
        inactivos = len(terceros) - activos
        self.label_stats.setText(
            f"Total: {len(terceros)} terceros | "
            f"Activos: {activos} | Inactivos: {inactivos}"
        )

    def _on_tabla_click(self, index: QModelIndex):
        """Maneja clicks en la tabla (columna de accion)."""
        if not index.isValid() or index.column() != 4:
            return

        tercero = self.modelo.tercero_en_fila(index.row())
        if not tercero:
            return

        if tercero.se_registra:
            self._desactivar_tercero(tercero.cod_padre)
        else:
            self._activar_tercero(tercero.cod_padre)

    def _activar_tercero(self, cod_padre: str):
        """Activa un tercero."""
        try:
            self.cambiar_estado_uc.ejecutar(cod_padre, activar=True)
            self.refrescar()
            QMessageBox.information(
                self,
                "Tercero activado",
                f"El tercero {cod_padre} ha sido activado correctamente."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al activar el tercero:\n\n{str(e)}"
            )

    def _desactivar_tercero(self, cod_padre: str):
        """Desactiva un tercero."""
        respuesta = QMessageBox.question(
            self,
            "Confirmar desactivacion",
            f"Esta seguro que desea desactivar el tercero {cod_padre}?\n\n"
            "Las lineas de factura con este tercero seran rechazadas en futuros procesamientos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.cambiar_estado_uc.ejecutar(cod_padre, activar=False)
                self.refrescar()
                QMessageBox.information(
                    self,
                    "Tercero desactivado",
                    f"El tercero {cod_padre} ha sido desactivado correctamente."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al desactivar el tercero:\n\n{str(e)}"
                )

    def _importar_excel(self):
        """Importa terceros desde un archivo Excel."""
        # Seleccionar archivo
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel de terceros",
            "",
            "Archivos Excel (*.xlsx *.xls)"
        )

        if not archivo:
            return

        # Preguntar si actualizar existentes
        respuesta = QMessageBox.question(
            self,
            "Modo de importacion",
            "Desea actualizar los terceros existentes?\n\n"
            "SI: Los terceros existentes seran actualizados\n"
            "NO: Los terceros existentes seran ignorados",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        actualizar_existentes = respuesta == QMessageBox.StandardButton.Yes

        # Crear dialogo de progreso
        progress = ProgressDialog(
            self,
            "Importando terceros",
            "Leyendo archivo Excel..."
        )
        progress.show()
        QApplication.processEvents()

        try:
            # Procesar archivo Excel
            terceros = self.excel_processor.procesar_archivo(archivo)

            if not terceros:
                progress.close()
                QMessageBox.warning(
                    self,
                    "Sin datos",
                    "No se encontraron terceros validos en el archivo Excel."
                )
                return

            # Configurar progreso
            progress.set_total(len(terceros))
            progress.set_message("Importando terceros a la base de datos...")
            QApplication.processEvents()

            # Importar terceros con optimizacion para grandes volumenes
            from lactalis_ventas.application.use_cases.importar_terceros import ResultadoImportacionTerceros
            resultado = ResultadoImportacionTerceros(total_leidos=len(terceros))

            # Calcular intervalo de actualizacion (cada 100 registros o 1% del total)
            update_interval = max(100, len(terceros) // 100) if len(terceros) > 1000 else 10

            # Procesar en lotes para mejor rendimiento
            batch_size = 500
            for batch_start in range(0, len(terceros), batch_size):
                batch_end = min(batch_start + batch_size, len(terceros))
                batch = terceros[batch_start:batch_end]

                for i, tercero in enumerate(batch):
                    try:
                        # Verificar si el tercero ya existe
                        tercero_existente = self.importar_uc.tercero_repo.obtener_por_cod_padre(tercero.cod_padre)

                        if tercero_existente:
                            if actualizar_existentes:
                                self.importar_uc.tercero_repo.actualizar(tercero)
                                resultado.terceros_actualizados += 1
                            else:
                                resultado.terceros_ignorados += 1
                        else:
                            self.importar_uc.tercero_repo.guardar(tercero)
                            resultado.terceros_nuevos += 1

                        # Actualizar progreso solo en intervalos
                        actual_index = batch_start + i + 1
                        if actual_index % update_interval == 0 or actual_index == len(terceros):
                            progress.set_value(actual_index)
                            QApplication.processEvents()

                    except Exception as e:
                        resultado.errores.append(f"Error con tercero {tercero.cod_padre}: {str(e)}")

            # Marcar como completado
            progress.set_completed()
            QApplication.processEvents()

            # Cerrar dialogo de progreso
            progress.close()

            # Refrescar tabla
            self.refrescar()

            # Mostrar resultado
            mensaje = (
                f"Importacion completada:\n\n"
                f"Total leidos: {resultado.total_leidos}\n"
                f"Nuevos: {resultado.terceros_nuevos}\n"
                f"Actualizados: {resultado.terceros_actualizados}\n"
                f"Ignorados: {resultado.terceros_ignorados}\n"
                f"Errores: {len(resultado.errores)}"
            )

            if resultado.errores:
                mensaje += "\n\nPrimeros errores:\n"
                for error in resultado.errores[:5]:
                    mensaje += f"- {error}\n"

            QMessageBox.information(
                self,
                "Importacion completada",
                mensaje
            )

        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Error al importar",
                f"Ocurrio un error al importar el archivo:\n\n{str(e)}"
            )
