from PIL import Image, ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QVBoxLayout, QWidget)

from app.utils.estilos import estilo_visualizador


class VisualizadorImagem(QDialog):
    def __init__(self, parent, imagem, titulo):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(800, 600)
        self.setModal(True)

        # Estilo visual da janela
        self.setStyleSheet(estilo_visualizador())

        self.imagem_original = imagem
        self.zoom_atual = 1.0

        # Layout principal
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)
        self.layout_principal.setSpacing(10)

        # Área de rolagem para a imagem
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Widget para conter a imagem
        self.container_imagem = QLabel()
        self.container_imagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.container_imagem)

        self.layout_principal.addWidget(self.scroll_area)

        # Frame de controles de zoom
        self.frame_zoom = QWidget()
        self.layout_zoom = QHBoxLayout(self.frame_zoom)
        self.layout_zoom.setContentsMargins(5, 5, 5, 5)

        self.botao_zoom_mais = QPushButton('+')
        self.botao_zoom_mais.setFixedWidth(40)
        self.botao_zoom_mais.clicked.connect(lambda: self.zoom(1.2))
        self.layout_zoom.addWidget(self.botao_zoom_mais)

        self.botao_zoom_menos = QPushButton('-')
        self.botao_zoom_menos.setFixedWidth(40)
        self.botao_zoom_menos.clicked.connect(lambda: self.zoom(0.8))
        self.layout_zoom.addWidget(self.botao_zoom_menos)

        self.botao_zoom_reset = QPushButton('1:1')
        self.botao_zoom_reset.setFixedWidth(40)
        self.botao_zoom_reset.clicked.connect(
            lambda: self.zoom(1.0 / self.zoom_atual)
        )
        self.layout_zoom.addWidget(self.botao_zoom_reset)

        self.rotulo_zoom = QLabel(f'Zoom: {self.zoom_atual:.1f}x')
        self.layout_zoom.addWidget(self.rotulo_zoom)

        self.layout_zoom.addStretch()

        self.layout_principal.addWidget(self.frame_zoom)

        # Atualizar o canvas com a imagem inicial
        self.atualizar_canvas()

        # Conectar eventos
        self.container_imagem.wheelEvent = self.ao_rolar_mouse

    def atualizar_canvas(self):
        """Atualiza a imagem com o zoom atual"""
        try:
            largura = int(self.imagem_original.width * self.zoom_atual)
            altura = int(self.imagem_original.height * self.zoom_atual)

            if largura < 1 or altura < 1:
                return

            metodo_redimensionamento = Image.Resampling.NEAREST
            if self.zoom_atual == 1.0:
                metodo_redimensionamento = Image.Resampling.LANCZOS

            imagem_redimensionada = self.imagem_original.resize(
                (largura, altura), metodo_redimensionamento
            )

            # Converter de PIL para QPixmap
            q_imagem = ImageQt.ImageQt(imagem_redimensionada)
            pixmap = QPixmap.fromImage(q_imagem)

            self.container_imagem.setPixmap(pixmap)
            self.container_imagem.setFixedSize(largura, altura)

            if hasattr(self, 'rotulo_zoom'):
                self.rotulo_zoom.setText(f'Zoom: {self.zoom_atual:.1f}x')

        except Exception as e:
            print(f'Erro ao atualizar canvas: {e}')

    def ao_rolar_mouse(self, evento):
        """Aplica zoom quando o usuário usa a roda do mouse"""
        fator = 1.1 if evento.angleDelta().y() > 0 else 0.9
        self.zoom(fator)

    def zoom(self, fator):
        """Aplica zoom na imagem"""
        novo_zoom = self.zoom_atual * fator

        if 0.1 <= novo_zoom <= 10.0:
            self.zoom_atual = novo_zoom
            self.atualizar_canvas()
