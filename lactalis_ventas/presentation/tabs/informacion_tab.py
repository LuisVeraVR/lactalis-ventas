"""Pestaña de información y estadísticas."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGroupBox, QPushButton
)
from PyQt6.QtCore import Qt
from lactalis_ventas.application.use_cases.obtener_estadisticas import ObtenerEstadisticasUseCase


class InformacionTab(QWidget):
    """Pestaña de información y estadísticas."""

    def __init__(self, obtener_estadisticas_uc: ObtenerEstadisticasUseCase):
        super().__init__()
        self.obtener_estadisticas_uc = obtener_estadisticas_uc

        self._configurar_ui()
        self.refrescar()

    def _configurar_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("Información del Sistema")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(titulo)

        # Grupo de reglas de negocio
        grupo_reglas = QGroupBox("Reglas de Negocio")
        grupo_reglas.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        layout_reglas = QVBoxLayout()

        reglas_text = """
<h3>Reglas de Procesamiento de Facturas:</h3>

<p><b>1. Validación de Número de Factura:</b></p>
<ul>
    <li>Solo se procesan facturas cuyo número empiece con "Factura"</li>
    <li>Ejemplo válido: "Factura001", "Factura-2024-001"</li>
    <li>Ejemplo inválido: "FAC001", "Invoice001"</li>
</ul>

<p><b>2. Validación de Valor Neto:</b></p>
<ul>
    <li>El valor neto debe ser estrictamente mayor que 0</li>
    <li>Se rechazan valores negativos y valores igual a 0</li>
    <li>Ejemplo válido: 1000.00, 0.01</li>
    <li>Ejemplo inválido: 0, -100.00</li>
</ul>

<p><b>3. Productos a Depurar (no registrar):</b></p>
<ul>
    <li>Crema de leche</li>
    <li>Leche en polvo</li>
    <li>Leche líquida</li>
</ul>
<p><i>Cualquier producto cuya descripción contenga estos términos será rechazado automáticamente.</i></p>

<p><b>4. Validación de Estado:</b></p>
<ul>
    <li>Los productos deben estar activos (se_registra = True)</li>
    <li>Los terceros deben estar activos (se_registra = True)</li>
    <li>Puede activar/desactivar productos y terceros desde las pestañas correspondientes</li>
</ul>

<p><b>5. Creación Automática:</b></p>
<ul>
    <li>Si un producto no existe en la base de datos, se crea automáticamente</li>
    <li>Si un tercero no existe en la base de datos, se crea automáticamente</li>
    <li>Los nuevos registros se crean con estado activo por defecto</li>
</ul>
        """

        text_reglas = QTextEdit()
        text_reglas.setHtml(reglas_text)
        text_reglas.setReadOnly(True)
        text_reglas.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
                padding: 10px;
            }
        """)
        layout_reglas.addWidget(text_reglas)

        grupo_reglas.setLayout(layout_reglas)
        layout.addWidget(grupo_reglas, 1)

        # Grupo de estadísticas
        grupo_stats = QGroupBox("Estadísticas de Procesamiento")
        grupo_stats.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        layout_stats = QVBoxLayout()

        # Botón refrescar
        btn_refrescar = QPushButton("Refrescar estadísticas")
        btn_refrescar.clicked.connect(self.refrescar)
        btn_refrescar.setStyleSheet("""
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
        layout_stats.addWidget(btn_refrescar)

        # Labels de estadísticas
        self.label_stats = QLabel()
        self.label_stats.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 20px;
                font-size: 13px;
            }
        """)
        self.label_stats.setWordWrap(True)
        layout_stats.addWidget(self.label_stats)

        grupo_stats.setLayout(layout_stats)
        layout.addWidget(grupo_stats)

    def refrescar(self):
        """Refresca las estadísticas."""
        try:
            stats = self.obtener_estadisticas_uc.ejecutar()

            if stats.total_facturas == 0:
                texto_stats = """
                <h3>No hay facturas procesadas</h3>
                <p>Procese facturas desde la pestaña "Procesar Excel" para ver estadísticas.</p>
                """
            else:
                texto_stats = f"""
                <h3>Resumen de Facturas Procesadas:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 10px; font-weight: bold;">Total de líneas procesadas:</td>
                        <td style="padding: 10px; text-align: right;">{stats.total_facturas:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Valor neto total:</td>
                        <td style="padding: 10px; text-align: right; color: #27ae60; font-weight: bold;">
                            ${stats.total_valor_neto:,.2f}
                        </td>
                    </tr>
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 10px; font-weight: bold;">Productos únicos:</td>
                        <td style="padding: 10px; text-align: right;">{stats.productos_unicos}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Terceros únicos:</td>
                        <td style="padding: 10px; text-align: right;">{stats.terceros_unicos}</td>
                    </tr>
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 10px; font-weight: bold;">Fecha inicial:</td>
                        <td style="padding: 10px; text-align: right;">{stats.fecha_inicio}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Fecha final:</td>
                        <td style="padding: 10px; text-align: right;">{stats.fecha_fin}</td>
                    </tr>
                </table>
                """

            self.label_stats.setText(texto_stats)

        except Exception as e:
            self.label_stats.setText(f"<p style='color: red;'>Error al obtener estadísticas: {str(e)}</p>")
