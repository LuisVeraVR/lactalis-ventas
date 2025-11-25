"""Punto de entrada de la aplicación Lactalis - Procesador de Facturas."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from lactalis_ventas.presentation.main_window import MainWindow


def main():
    """Función principal."""
    # Crear aplicación
    app = QApplication(sys.argv)

    # Configurar estilo
    app.setStyle("Fusion")

    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()

    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
