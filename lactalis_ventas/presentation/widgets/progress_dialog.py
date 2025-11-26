"""Diálogo de progreso con tiempo estimado."""
import time
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """Diálogo de progreso con tiempo estimado."""

    def __init__(self, parent=None, title="Procesando", message="Por favor espere..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        # Variables de control
        self.start_time = None
        self.total_items = 0
        self.current_item = 0
        self.estimated_time_per_item = 0.1  # Segundos por item (se ajusta dinámicamente)

        # Configurar UI
        self._setup_ui(message)

        # Timer para actualizar el progreso
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(100)  # Actualizar cada 100ms

    def _setup_ui(self, message):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Mensaje principal
        self.label_message = QLabel(message)
        self.label_message.setWordWrap(True)
        font = QFont()
        font.setPointSize(11)
        self.label_message.setFont(font)
        layout.addWidget(self.label_message)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Etiqueta de progreso
        self.label_progress = QLabel("Iniciando...")
        self.label_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_progress.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(self.label_progress)

        # Etiqueta de tiempo
        self.label_time = QLabel("")
        self.label_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_time.setStyleSheet("color: #34495e; font-size: 10px; font-weight: bold;")
        layout.addWidget(self.label_time)

    def set_total(self, total: int):
        """Establece el total de items a procesar."""
        self.total_items = total
        self.current_item = 0
        self.start_time = time.time()
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)

    def set_value(self, value: int):
        """Establece el valor actual del progreso."""
        self.current_item = value
        self.progress_bar.setValue(value)

        # Calcular tiempo estimado por item
        if self.start_time and value > 0:
            elapsed = time.time() - self.start_time
            self.estimated_time_per_item = elapsed / value

        self._update_display()

    def increment(self):
        """Incrementa el progreso en 1."""
        self.set_value(self.current_item + 1)

    def set_message(self, message: str):
        """Actualiza el mensaje."""
        self.label_message.setText(message)

    def _update_display(self):
        """Actualiza la visualización del progreso."""
        if self.total_items == 0:
            return

        # Calcular porcentaje
        percentage = (self.current_item / self.total_items) * 100

        # Actualizar etiqueta de progreso
        self.label_progress.setText(f"{self.current_item} de {self.total_items} ({percentage:.1f}%)")

        # Calcular y mostrar tiempo
        if self.start_time:
            elapsed = time.time() - self.start_time

            if self.current_item > 0:
                # Tiempo restante estimado
                remaining_items = self.total_items - self.current_item
                estimated_remaining = remaining_items * self.estimated_time_per_item

                elapsed_str = self._format_time(elapsed)
                remaining_str = self._format_time(estimated_remaining)

                self.label_time.setText(
                    f"⏱️ Transcurrido: {elapsed_str} | ⏳ Restante: {remaining_str}"
                )
            else:
                elapsed_str = self._format_time(elapsed)
                self.label_time.setText(f"⏱️ Transcurrido: {elapsed_str}")

    def _format_time(self, seconds: float) -> str:
        """Formatea el tiempo en un formato legible."""
        if seconds < 1:
            return "< 1s"
        elif seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def set_completed(self):
        """Marca el progreso como completado."""
        self.progress_bar.setValue(self.total_items)
        if self.start_time:
            elapsed = time.time() - self.start_time
            elapsed_str = self._format_time(elapsed)
            self.label_time.setText(f"✅ Completado en: {elapsed_str}")
        self.label_progress.setText(f"Completado: {self.total_items} items")
        self.update_timer.stop()

    def closeEvent(self, event):
        """Maneja el cierre del diálogo."""
        self.update_timer.stop()
        super().closeEvent(event)
