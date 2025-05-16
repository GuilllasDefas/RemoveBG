from PIL import Image, ImageDraw, ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QSlider, QVBoxLayout, QWidget)

from app.utils.estilos import estilo_janela_ferramentas

 

class JanelaBorracha(QDialog):
    def __init__(self, parent, imagem, callback_concluido):
        super().__init__(parent)
        self.setWindowTitle('Ferramenta de Borracha')
        self.resize(800, 600)
        self.setModal(True)

        # Estilo visual da janela
        self.setStyleSheet(estilo_janela_ferramentas())

        self.imagem_original = imagem
        self.imagem_editavel = imagem.copy()
        self.callback_concluido = callback_concluido
        self.zoom_atual = 1.0
        self.tamanho_borracha = 20

        # Layout principal
        self.layout_principal = QVBoxLayout(self)

        # Widget de canvas para desenhar
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Widget personalizado para desenhar
        self.area_desenho = AreaDesenhoBorracha(self)
        self.scroll_area.setWidget(self.area_desenho)

        self.layout_principal.addWidget(self.scroll_area)

        # Frame de controles
        self.frame_controles = QWidget()
        self.layout_controles = QHBoxLayout(self.frame_controles)

        # Slider para o tamanho da borracha
        self.layout_controles.addWidget(QLabel('Tamanho da Borracha:'))

        self.slider_tamanho = QSlider(Qt.Orientation.Horizontal)
        self.slider_tamanho.setRange(5, 100)
        self.slider_tamanho.setValue(self.tamanho_borracha)
        self.slider_tamanho.valueChanged.connect(
            self.atualizar_tamanho_borracha
        )
        self.layout_controles.addWidget(self.slider_tamanho)

        # Botões de zoom
        self.botao_zoom_mais = QPushButton('Zoom +')
        self.botao_zoom_mais.clicked.connect(lambda: self.zoom(1.2))
        self.layout_controles.addWidget(self.botao_zoom_mais)

        self.botao_zoom_menos = QPushButton('Zoom -')
        self.botao_zoom_menos.clicked.connect(lambda: self.zoom(0.8))
        self.layout_controles.addWidget(self.botao_zoom_menos)

        # Botões de ação
        self.botao_salvar = QPushButton('Salvar Alterações')
        self.botao_salvar.clicked.connect(self.salvar_alteracoes)
        self.layout_controles.addWidget(self.botao_salvar)

        self.botao_cancelar = QPushButton('Cancelar')
        self.botao_cancelar.clicked.connect(self.reject)
        self.layout_controles.addWidget(self.botao_cancelar)

        self.layout_principal.addWidget(self.frame_controles)

        # Atualizar a imagem
        self.atualizar_canvas()

    def atualizar_canvas(self):
        """Atualiza a imagem exibida com o zoom atual"""
        largura = int(self.imagem_editavel.width * self.zoom_atual)
        altura = int(self.imagem_editavel.height * self.zoom_atual)

        imagem_redimensionada = self.imagem_editavel.resize(
            (largura, altura), Image.Resampling.NEAREST
        )

        # Converter de PIL para QPixmap
        q_imagem = ImageQt.ImageQt(imagem_redimensionada)
        self.pixmap = QPixmap.fromImage(q_imagem)

        # Atualizar o widget de desenho
        self.area_desenho.setPixmap(self.pixmap)
        self.area_desenho.setFixedSize(largura, altura)
        self.area_desenho.update()

    def apagar(self, x, y):
        """Apaga a área onde o mouse é clicado ou arrastado"""
        x_real = int(x / self.zoom_atual)
        y_real = int(y / self.zoom_atual)

        desenho = ImageDraw.Draw(self.imagem_editavel)
        desenho.ellipse(
            (
                x_real - self.tamanho_borracha,
                y_real - self.tamanho_borracha,
                x_real + self.tamanho_borracha,
                y_real + self.tamanho_borracha,
            ),
            fill=(0, 0, 0, 0),
        )

        self.atualizar_canvas()

    def atualizar_tamanho_borracha(self, valor):
        """Atualiza o tamanho da borracha com base no slider"""
        self.tamanho_borracha = valor
        self.area_desenho.tamanho_cursor = valor
        self.area_desenho.update()

    def zoom(self, fator):
        """Aplica zoom na imagem"""
        novo_zoom = self.zoom_atual * fator

        if 0.1 <= novo_zoom <= 10.0:
            self.zoom_atual = novo_zoom
            self.atualizar_canvas()

    def salvar_alteracoes(self):
        """Salva as alterações e fecha a janela"""
        if self.callback_concluido:
            self.callback_concluido(self.imagem_editavel)
        self.accept()


class AreaDesenhoBorracha(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.parent = parent
        self.ultima_posicao = None
        self.tamanho_cursor = parent.tamanho_borracha

    def mousePressEvent(self, evento):
        """Iniciar o apagamento"""
        pos = evento.position()
        self.ultima_posicao = (int(pos.x()), int(pos.y()))
        self.parent.apagar(int(pos.x()), int(pos.y()))

    def mouseMoveEvent(self, evento):
        """Continuar apagando enquanto arrasta o mouse"""
        pos = evento.position()
        if evento.buttons() & Qt.MouseButton.LeftButton:
            x, y = int(pos.x()), int(pos.y())
            self.parent.apagar(x, y)

        self.update()  # Atualiza o cursor

    def wheelEvent(self, evento):
        """Propaga eventos de roda do mouse para o pai"""
        fator = 1.1 if evento.angleDelta().y() > 0 else 0.9
        self.parent.zoom(fator)

    def paintEvent(self, evento):
        """Desenha a imagem e o cursor da borracha"""
        super().paintEvent(evento)

        # Desenha o cursor da borracha
        if self.underMouse():
            pintor = QPainter(self)
            pintor.setPen(QPen(QColor(255, 0, 0), 2))

            # Desenha borracha semi-transparente
            pintor.setBrush(QBrush(QColor(128, 128, 128, 128)))

            # Posição do mouse
            pos = self.mapFromGlobal(self.cursor().pos())
            raio = self.tamanho_cursor * self.parent.zoom_atual

            # Convertendo para inteiros para evitar o erro de tipo
            pintor.drawEllipse(
                int(pos.x() - raio),
                int(pos.y() - raio),
                int(raio * 2),
                int(raio * 2),
            )
