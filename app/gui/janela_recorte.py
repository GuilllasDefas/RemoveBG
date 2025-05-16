from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, 
                           QLabel, QPushButton, QWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PIL import Image, ImageQt

class JanelaRecorte(QDialog):
    def __init__(self, parent, imagem, callback_concluido):
        super().__init__(parent)
        self.setWindowTitle("Ferramenta de Recorte")
        self.resize(800, 600)
        self.setModal(True)
        
        self.imagem_original = imagem
        self.callback_concluido = callback_concluido
        self.inicio_x = None
        self.inicio_y = None
        self.fim_x = None
        self.fim_y = None
        self.zoom_atual = 1.0
        
        # Layout principal
        self.layout_principal = QVBoxLayout(self)
        
        # Widget de canvas para desenhar
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Widget personalizado para desenhar o retângulo
        self.area_desenho = AreaDesenhoRecorte(self)
        self.scroll_area.setWidget(self.area_desenho)
        
        self.layout_principal.addWidget(self.scroll_area)
        
        # Frame de controles de zoom
        self.frame_zoom = QWidget()
        self.layout_zoom = QHBoxLayout(self.frame_zoom)
        
        self.botao_zoom_mais = QPushButton("Zoom +")
        self.botao_zoom_mais.clicked.connect(lambda: self.zoom(1.2))
        self.layout_zoom.addWidget(self.botao_zoom_mais)
        
        self.botao_zoom_menos = QPushButton("Zoom -")
        self.botao_zoom_menos.clicked.connect(lambda: self.zoom(0.8))
        self.layout_zoom.addWidget(self.botao_zoom_menos)
        
        self.botao_zoom_reset = QPushButton("Reset")
        self.botao_zoom_reset.clicked.connect(lambda: self.zoom(1.0/self.zoom_atual))
        self.layout_zoom.addWidget(self.botao_zoom_reset)
        
        self.layout_principal.addWidget(self.frame_zoom)
        
        # Frame de botões de ação
        self.frame_botoes = QWidget()
        self.layout_botoes = QHBoxLayout(self.frame_botoes)
        
        self.botao_recortar = QPushButton("Recortar")
        self.botao_recortar.clicked.connect(self.confirmar_recorte)
        self.layout_botoes.addWidget(self.botao_recortar)
        
        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_cancelar.clicked.connect(self.reject)
        self.layout_botoes.addWidget(self.botao_cancelar)
        
        self.layout_principal.addWidget(self.frame_botoes)
        
        # Atualizar a imagem
        self.exibir_imagem()
        
    def exibir_imagem(self):
        """Exibe a imagem no widget de desenho com o zoom atual"""
        largura = int(self.imagem_original.width * self.zoom_atual)
        altura = int(self.imagem_original.height * self.zoom_atual)
        
        imagem_redimensionada = self.imagem_original.resize(
            (largura, altura), Image.Resampling.NEAREST
        )
        
        # Converter de PIL para QPixmap
        q_imagem = ImageQt.ImageQt(imagem_redimensionada)
        self.pixmap = QPixmap.fromImage(q_imagem)
        
        # Atualizar o widget de desenho
        self.area_desenho.setPixmap(self.pixmap)
        self.area_desenho.setFixedSize(largura, altura)
        self.area_desenho.update()
    
    def zoom(self, fator):
        """Aplica zoom na imagem"""
        novo_zoom = self.zoom_atual * fator
        
        # Limita o zoom entre 0.1x e 10x
        if 0.1 <= novo_zoom <= 10.0:
            self.zoom_atual = novo_zoom
            self.exibir_imagem()
            # Resetar o retângulo de seleção
            self.area_desenho.inicio = None
            self.area_desenho.fim = None
    
    def confirmar_recorte(self):
        """Confirma o recorte e chama o callback com a imagem recortada"""
        if not self.area_desenho.inicio or not self.area_desenho.fim:
            self.reject()
            return
            
        # Obter coordenadas do retângulo
        x1 = min(self.area_desenho.inicio.x(), self.area_desenho.fim.x())
        y1 = min(self.area_desenho.inicio.y(), self.area_desenho.fim.y())
        x2 = max(self.area_desenho.inicio.x(), self.area_desenho.fim.x())
        y2 = max(self.area_desenho.inicio.y(), self.area_desenho.fim.y())
            
        # Verificar se a área selecionada é válida
        if x2 - x1 <= 0 or y2 - y1 <= 0:
            self.reject()
            return
            
        # Converter coordenadas de acordo com o zoom
        x1_real = int(x1 / self.zoom_atual)
        y1_real = int(y1 / self.zoom_atual)
        x2_real = int(x2 / self.zoom_atual)
        y2_real = int(y2 / self.zoom_atual)
        
        # Área de recorte para processamento em lote
        caixa_recorte = (x1_real, y1_real, x2_real, y2_real)
        
        # Recortar a imagem
        imagem_recortada = self.imagem_original.crop(caixa_recorte)
        
        # Chamar o callback com a imagem recortada e a caixa de recorte
        if self.callback_concluido:
            # Passa tanto a imagem quanto as coordenadas de recorte
            self.callback_concluido(imagem_recortada, caixa_recorte)
            
        self.accept()

class AreaDesenhoRecorte(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.inicio = None
        self.fim = None
        self.parent = parent
        
    def mousePressEvent(self, evento):
        """Inicia o desenho do retângulo"""
        self.inicio = QPoint(int(evento.position().x()), int(evento.position().y()))
        self.fim = self.inicio
        self.update()
        
    def mouseMoveEvent(self, evento):
        """Atualiza o retângulo enquanto o mouse se move"""
        if evento.buttons() & Qt.MouseButton.LeftButton and self.inicio:
            self.fim = QPoint(int(evento.position().x()), int(evento.position().y()))
            self.update()
            
    def wheelEvent(self, evento):
        """Propaga eventos de roda do mouse para o pai"""
        fator = 1.1 if evento.angleDelta().y() > 0 else 0.9
        self.parent.zoom(fator)
        
    def paintEvent(self, evento):
        """Desenha a imagem e o retângulo de seleção"""
        super().paintEvent(evento)
        
        if self.inicio and self.fim:
            pintor = QPainter(self)
            caneta = QPen(QColor(255, 0, 0))
            caneta.setWidth(2)
            pintor.setPen(caneta)
            
            x = min(self.inicio.x(), self.fim.x())
            y = min(self.inicio.y(), self.fim.y())
            largura = abs(self.fim.x() - self.inicio.x())
            altura = abs(self.fim.y() - self.inicio.y())
            
            pintor.drawRect(x, y, largura, altura)
