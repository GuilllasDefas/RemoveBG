from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt6.QtGui import QFont

class DicaFlutuante(QLabel):
    """ Cria uma dica flutuante (tooltip) customizada para um widget PyQt6 
        com atraso para mostrar e personalização avançada.
    """
    def __init__(self, widget, texto, atraso_ms=500, pai=None):
        super().__init__(pai or widget.window())
        self.widget_alvo = widget
        self.setText(texto)
        self.atraso_ms = atraso_ms
        
        # Configuração visual
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setWordWrap(True)
        self.setMaximumWidth(250)
        self.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                color: #000000;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #AAAAAA;
            }
        """)
        
        # Timer para controlar exibição
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.mostrar_dica)
        self.hide()
        
        # Instalar filtro de evento no widget alvo
        self.widget_alvo.installEventFilter(self)
    
    def eventFilter(self, objeto, evento):
        """Filtro de eventos para monitorar o widget alvo"""
        if objeto is self.widget_alvo:
            tipo_evento = evento.type()
            
            if tipo_evento == QEvent.Type.Enter:
                # Mouse entrou no widget - iniciar timer
                posicao_global = objeto.mapToGlobal(QPoint(0, objeto.height() + 5))
                self.posicao = posicao_global
                self.timer.start(self.atraso_ms)
                
            elif tipo_evento in (QEvent.Type.Leave, QEvent.Type.MouseButtonPress):
                # Mouse saiu ou clicou - esconder dica e cancelar timer
                self.timer.stop()
                self.hide()
                
        return super().eventFilter(objeto, evento)
    
    def mostrar_dica(self):
        """Exibe a dica na posição calculada"""
        if not self.widget_alvo.underMouse():
            return
            
        # Ajustar posição caso necessário
        self.adjustSize()
        
        # Mover para posição calculada
        self.move(self.posicao)
        self.show()
