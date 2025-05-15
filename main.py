from PyQt6.QtWidgets import QApplication
import sys
from app.gui.app_principal import AplicativoRemoveFundo

def main():
    # Inicialização da aplicação Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Estilo visual consistente
    
    # Inicializa a janela principal
    janela_principal = AplicativoRemoveFundo()
    janela_principal.show()
    
    # Executa o loop de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()