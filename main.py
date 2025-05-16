import sys

from PyQt6.QtWidgets import QApplication

from app.gui.app_principal import AplicativoRemoveFundo
from app.utils.estilos import configurar_paleta


def main():
    # Inicialização da aplicação Qt
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo visual consistente

    # Aplicar paleta de cores global
    app.setPalette(configurar_paleta(app))

    # Inicializa a janela principal
    janela_principal = AplicativoRemoveFundo()
    janela_principal.show()

    # Executa o loop de eventos
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
