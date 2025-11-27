"""Pestana para procesar archivos Excel."""
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QProgressBar, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from lactalis_ventas.infrastructure.excel.excel_processor import ExcelProcessor
from lactalis_ventas.application.use_cases.procesar_facturas import ProcesarFacturasUseCase
from lactalis_ventas.presentation.widgets.progress_dialog import ProgressDialog


class ProcessThread(QThread):
    """Thread para procesar facturas en segundo plano."""

    finished = pyqtSignal(object)  # Emite el resultado del procesamiento
    error = pyqtSignal(str)  # Emite errores
    progress = pyqtSignal(int, int, str)  # Emite progreso (actual, total, mensaje)

    def __init__(self, excel_processor, archivo, db_path="lactalis.db"):
        super().__init__()
        self.excel_processor = excel_processor
        self.archivo = archivo
        self.db_path = db_path

    def run(self):
        """Ejecuta el procesamiento."""
        database = None
        try:
            # Crear conexion a la base de datos en este thread
            from lactalis_ventas.infrastructure.database.database import Database
            from lactalis_ventas.infrastructure.database.producto_repository_impl import ProductoRepositoryImpl
            from lactalis_ventas.infrastructure.database.tercero_repository_impl import TerceroRepositoryImpl
            from lactalis_ventas.infrastructure.database.factura_repository_impl import FacturaRepositoryImpl
            from lactalis_ventas.application.use_cases.procesar_facturas import ProcesarFacturasUseCase

            self.progress.emit(0, 0, "Inicializando base de datos...")
            database = Database(self.db_path)
            database.conectar()

            # Crear repositorios con la conexion de este thread
            producto_repo = ProductoRepositoryImpl(database)
            tercero_repo = TerceroRepositoryImpl(database)
            factura_repo = FacturaRepositoryImpl(database)

            # Crear caso de uso con los repositorios de este thread
            procesar_uc = ProcesarFacturasUseCase(
                producto_repo,
                tercero_repo,
                factura_repo
            )

            # Leer archivo Excel
            self.progress.emit(0, 0, "Leyendo archivo Excel...")
            lineas = self.excel_processor.procesar_archivo(self.archivo)

            # Emitir total de lineas
            total = len(lineas)
            self.progress.emit(0, total, f"Procesando {total} lineas de facturas...")

            # Procesar facturas con actualizacion de progreso
            resultado = procesar_uc.ejecutar(lineas)

            # Emitir progreso completo
            self.progress.emit(total, total, "Procesamiento completado")

            self.finished.emit(resultado)
        except Exception as e:
            import traceback
            error_msg = f"Error procesando linea: {str(e)}\n{traceback.format_exc()}"
            self.error.emit(error_msg)
        finally:
            # Cerrar la conexion de base de datos de este thread
            if database:
                database.cerrar()


class ProcesarExcelTab(QWidget):
    """Pestana para procesar archivos Excel."""

    def __init__(self, excel_processor: ExcelProcessor, procesar_uc: ProcesarFacturasUseCase):
        super().__init__()
        self.excel_processor = excel_processor
        self.procesar_uc = procesar_uc
        self.archivo_seleccionado = None
        self.process_thread = None
        self.ultimo_resultado = None

        self._configurar_ui()

    def _configurar_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titulo
        titulo = QLabel("Procesar Facturas desde Excel")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(titulo)

        # Grupo de seleccion de archivo
        grupo_archivo = QGroupBox("1. Seleccionar archivo Excel")
        grupo_archivo.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_archivo = QHBoxLayout()

        self.label_archivo = QLabel("No se ha seleccionado ningun archivo")
        self.label_archivo.setStyleSheet("color: #7f8c8d;")
        layout_archivo.addWidget(self.label_archivo, 1)

        self.btn_seleccionar = QPushButton("Seleccionar archivo")
        self.btn_seleccionar.clicked.connect(self._seleccionar_archivo)
        self.btn_seleccionar.setStyleSheet("""
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
        layout_archivo.addWidget(self.btn_seleccionar)

        grupo_archivo.setLayout(layout_archivo)
        layout.addWidget(grupo_archivo)

        # Grupo de procesamiento
        grupo_procesar = QGroupBox("2. Procesar archivo")
        grupo_procesar.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_procesar = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.btn_procesar = QPushButton("Procesar facturas")
        self.btn_procesar.clicked.connect(self._procesar_facturas)
        self.btn_procesar.setEnabled(False)
        self.btn_procesar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover:enabled {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        btn_layout.addWidget(self.btn_procesar)

        self.btn_exportar = QPushButton("Exportar registrables")
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.clicked.connect(self._exportar_registrables)
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover:enabled {
                background-color: #7d3c98;
            }
            QPushButton:disabled {
                background-color: #b9b9b9;
            }
        """)
        btn_layout.addWidget(self.btn_exportar)
        btn_layout.addStretch()

        layout_procesar.addLayout(btn_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout_procesar.addWidget(self.progress_bar)

        grupo_procesar.setLayout(layout_procesar)
        layout.addWidget(grupo_procesar)

        # Grupo de resultados
        grupo_resultados = QGroupBox("3. Resultados")
        grupo_resultados.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_resultados = QVBoxLayout()

        # Resumen
        self.label_resumen = QLabel("")
        self.label_resumen.setStyleSheet("font-size: 12px; padding: 10px; background-color: #ecf0f1; border-radius: 4px;")
        layout_resultados.addWidget(self.label_resumen)

        # Splitter para dividir registradas y rechazadas
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Tabla de lineas registradas
        grupo_registradas = QWidget()
        layout_reg = QVBoxLayout(grupo_registradas)
        layout_reg.setContentsMargins(0, 0, 0, 0)

        label_reg = QLabel("Lineas registradas:")
        label_reg.setStyleSheet("font-weight: bold; color: #27ae60;")
        layout_reg.addWidget(label_reg)

        self.tabla_registradas = QTableWidget()
        self.tabla_registradas.setColumnCount(7)
        self.tabla_registradas.setHorizontalHeaderLabels([
            "Factura", "Fecha", "Tercero", "Producto", "Descripcion", "Cantidad", "Valor Neto"
        ])
        self.tabla_registradas.horizontalHeader().setStretchLastSection(True)
        layout_reg.addWidget(self.tabla_registradas)

        splitter.addWidget(grupo_registradas)

        # Tabla de lineas rechazadas
        grupo_rechazadas = QWidget()
        layout_rech = QVBoxLayout(grupo_rechazadas)
        layout_rech.setContentsMargins(0, 0, 0, 0)

        label_rech = QLabel("Lineas rechazadas:")
        label_rech.setStyleSheet("font-weight: bold; color: #e74c3c;")
        layout_rech.addWidget(label_rech)

        self.tabla_rechazadas = QTableWidget()
        self.tabla_rechazadas.setColumnCount(7)
        self.tabla_rechazadas.setHorizontalHeaderLabels([
            "Factura", "Tercero", "Producto", "Descripcion", "Valor Neto", "Motivo", ""
        ])
        self.tabla_rechazadas.horizontalHeader().setStretchLastSection(True)
        layout_rech.addWidget(self.tabla_rechazadas)

        splitter.addWidget(grupo_rechazadas)

        layout_resultados.addWidget(splitter)

        grupo_resultados.setLayout(layout_resultados)
        layout.addWidget(grupo_resultados, 1)

    def _seleccionar_archivo(self):
        """Abre el dialogo para seleccionar un archivo Excel."""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos Excel (*.xlsx *.xls)"
        )

        if archivo:
            self.archivo_seleccionado = archivo
            self.label_archivo.setText(f"Archivo: {archivo}")
            self.label_archivo.setStyleSheet("color: #27ae60;")
            self.btn_procesar.setEnabled(True)

    def _procesar_facturas(self):
        """Procesa las facturas del archivo Excel."""
        if not self.archivo_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un archivo Excel")
            return

        # Deshabilitar botones
        self.btn_procesar.setEnabled(False)
        self.btn_seleccionar.setEnabled(False)

        # Ocultar barra de progreso anterior
        self.progress_bar.setVisible(False)

        # Limpiar resultados anteriores
        self.label_resumen.setText("Procesando...")
        self.tabla_registradas.setRowCount(0)
        self.tabla_rechazadas.setRowCount(0)
        self.ultimo_resultado = None
        self.btn_exportar.setEnabled(False)

        # Crear dialogo de progreso
        self.progress_dialog = ProgressDialog(
            self,
            "Procesando facturas",
            "Iniciando procesamiento..."
        )
        self.progress_dialog.show()

        # Crear y ejecutar thread (sin pasar procesar_uc ya que se crea dentro del thread)
        self.process_thread = ProcessThread(
            self.excel_processor,
            self.archivo_seleccionado,
            "lactalis.db"  # Ruta de la base de datos
        )
        self.process_thread.finished.connect(self._on_proceso_completado)
        self.process_thread.error.connect(self._on_proceso_error)
        self.process_thread.progress.connect(self._on_progreso_actualizado)
        self.process_thread.start()

    def _on_progreso_actualizado(self, actual: int, total: int, mensaje: str):
        """Actualiza el progreso del procesamiento."""
        if total > 0:
            if self.progress_dialog.total_items == 0:
                self.progress_dialog.set_total(total)
            self.progress_dialog.set_value(actual)
            self.progress_dialog.set_message(mensaje)

    def _on_proceso_completado(self, resultado):
        """Manejador de proceso completado."""
        # Marcar progreso como completado y cerrar dialogo
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.set_completed()
            self.progress_dialog.close()

        # Habilitar botones
        self.btn_procesar.setEnabled(True)
        self.btn_seleccionar.setEnabled(True)

        # Mostrar resumen
        self.label_resumen.setText(resultado.obtener_resumen())
        self.ultimo_resultado = resultado
        self.btn_exportar.setEnabled(len(resultado.lineas_registradas) > 0)

        # Llenar tabla de registradas
        self.tabla_registradas.setRowCount(len(resultado.lineas_registradas))
        for i, linea in enumerate(resultado.lineas_registradas):
            self.tabla_registradas.setItem(i, 0, QTableWidgetItem(linea.numero_factura))
            self.tabla_registradas.setItem(i, 1, QTableWidgetItem(linea.fecha.strftime("%Y-%m-%d")))
            self.tabla_registradas.setItem(i, 2, QTableWidgetItem(linea.nombre_tercero))
            self.tabla_registradas.setItem(i, 3, QTableWidgetItem(linea.codigo_producto))
            self.tabla_registradas.setItem(i, 4, QTableWidgetItem(linea.descripcion_producto))
            self.tabla_registradas.setItem(i, 5, QTableWidgetItem(str(linea.cantidad)))
            self.tabla_registradas.setItem(i, 6, QTableWidgetItem(f"${linea.valor_neto:,.2f}"))

        # Llenar tabla de rechazadas
        self.tabla_rechazadas.setRowCount(len(resultado.lineas_rechazadas_detalle))
        for i, linea in enumerate(resultado.lineas_rechazadas_detalle):
            self.tabla_rechazadas.setItem(i, 0, QTableWidgetItem(linea.numero_factura))
            self.tabla_rechazadas.setItem(i, 1, QTableWidgetItem(linea.nombre_tercero))
            self.tabla_rechazadas.setItem(i, 2, QTableWidgetItem(linea.codigo_producto))
            self.tabla_rechazadas.setItem(i, 3, QTableWidgetItem(linea.descripcion_producto))
            self.tabla_rechazadas.setItem(i, 4, QTableWidgetItem(f"${linea.valor_neto:,.2f}"))
            self.tabla_rechazadas.setItem(i, 5, QTableWidgetItem(linea.motivo_rechazo or ""))

        # Mostrar mensaje de exito
        QMessageBox.information(
            self,
            "Procesamiento completado",
            f"Se procesaron {resultado.lineas_procesadas} lineas correctamente.\n"
            f"Se rechazaron {resultado.lineas_rechazadas} lineas."
        )

    def _on_proceso_error(self, error):
        """Manejador de errores en el proceso."""
        # Cerrar dialogo de progreso
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        # Habilitar botones
        self.btn_procesar.setEnabled(True)
        self.btn_seleccionar.setEnabled(True)

        # Mostrar error
        QMessageBox.critical(
            self,
            "Error al procesar",
            f"Ocurrio un error al procesar el archivo:\n\n{error}"
        )

    def _exportar_registrables(self):
        """Exporta a Excel las lineas ya depuradas que se registran."""
        if not self.ultimo_resultado or not self.ultimo_resultado.lineas_registradas:
            QMessageBox.information(
                self,
                "Sin datos",
                "No hay lineas registrables para exportar. Procese un archivo primero."
            )
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar lineas registrables",
            "lineas_registrables.xlsx",
            "Archivos Excel (*.xlsx)"
        )
        if not ruta:
            return
        if not ruta.lower().endswith(".xlsx"):
            ruta = f"{ruta}.xlsx"

        try:
            data = []
            for linea in self.ultimo_resultado.lineas_registradas:
                data.append({
                    "numero_factura": linea.numero_factura,
                    "fecha": linea.fecha,
                    "cod_padre": linea.cod_padre,
                    "nombre_tercero": linea.nombre_tercero,
                    "nit": linea.nit,
                    "codigo_producto": linea.codigo_producto,
                    "descripcion_producto": linea.descripcion_producto,
                    "grupo_producto": linea.grupo_producto,
                    "cantidad": float(linea.cantidad),
                    "valor_neto": float(linea.valor_neto),
                })

            pd.DataFrame(data).to_excel(ruta, index=False)
            QMessageBox.information(
                self,
                "Exportacion completada",
                f"Se exportaron {len(data)} lineas depuradas a:\n{ruta}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al exportar",
                f"No se pudo crear el Excel:\n\n{str(e)}"
            )
