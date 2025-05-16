from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, 
                             QLabel, QProgressBar, QPushButton, QScrollArea, 
                             QSlider, QVBoxLayout, QWidget)

from app.configuracoes import (ALPHA_MATTING_PADRAO, EROSAO_MASCARA_PADRAO,
                               LIMIAR_FUNDO_PADRAO, LIMIAR_OBJETO_PADRAO,
                               MODELO_PADRAO, MODELOS_DISPONIVEIS, 
                               TITULO_APP, VERSAO)
from app.utils.estilos import CORES, ESTILOS_COMPONENTES


class InterfaceConstrutor:
    """Classe responsável por construir os elementos da interface do aplicativo"""
    
    @staticmethod
    def criar_cabecalho(app):
        """Cria o cabeçalho da aplicação"""
        app.frame_cabecalho = QWidget()
        app.layout_cabecalho = QHBoxLayout(app.frame_cabecalho)
        app.layout_cabecalho.setContentsMargins(10, 10, 10, 20)

        # Logo à esquerda
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        app.botao_sobre = QPushButton('Sobre')
        app.botao_sobre.setFixedWidth(100)
        app.botao_sobre.clicked.connect(app.mostrar_sobre)
        logo_layout.addWidget(app.botao_sobre)
        app.layout_cabecalho.addWidget(logo_container)

        # Título centralizado com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(22)
        fonte_titulo.setBold(True)

        app.rotulo_cabecalho = QLabel(f'Removedor de Fundos v{VERSAO} - Beta')
        app.rotulo_cabecalho.setFont(fonte_titulo)
        app.rotulo_cabecalho.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app.rotulo_cabecalho.setStyleSheet(
            ESTILOS_COMPONENTES['cabecalho_titulo']
        )
        app.layout_cabecalho.addWidget(app.rotulo_cabecalho, 1)

        # Espaço à direita para equilíbrio
        app.layout_cabecalho.addSpacing(100)

        app.layout_principal.addWidget(app.frame_cabecalho)

        # Linha divisória
        linha_divisoria = QFrame()
        linha_divisoria.setFrameShape(QFrame.Shape.HLine)
        linha_divisoria.setFrameShadow(QFrame.Shadow.Sunken)
        linha_divisoria.setObjectName('FrameDivisor')
        linha_divisoria.setFixedHeight(2)
        app.layout_principal.addWidget(linha_divisoria)

    @staticmethod
    def criar_menu(app):
        """Cria o menu principal da aplicação"""
        app.menu_principal = app.menuBar()

        # Menu Arquivo
        app.menu_arquivo = app.menu_principal.addMenu('Arquivo')

        app.acao_selecionar = QAction('Selecionar Imagem', app)
        app.acao_selecionar.triggered.connect(app.selecionar_imagem)
        app.menu_arquivo.addAction(app.acao_selecionar)

        app.acao_salvar = QAction('Salvar Resultado', app)
        app.acao_salvar.triggered.connect(lambda: app.salvar_imagem())
        app.acao_salvar.setEnabled(False)
        app.menu_arquivo.addAction(app.acao_salvar)

        app.menu_arquivo.addSeparator()

        app.acao_sair = QAction('Sair', app)
        app.acao_sair.triggered.connect(app.close)
        app.menu_arquivo.addAction(app.acao_sair)

        # Menu Ferramentas
        app.menu_ferramentas = app.menu_principal.addMenu('Ferramentas')

        app.acao_pasta = QAction('Processar Pasta', app)
        app.acao_pasta.triggered.connect(lambda: app.processar_pasta())
        app.menu_ferramentas.addAction(app.acao_pasta)

        app.acao_recorte = QAction('Cortar Imagem', app)
        app.acao_recorte.triggered.connect(
            lambda: app.abrir_ferramenta_recorte()
        )
        app.acao_recorte.setEnabled(False)
        app.menu_ferramentas.addAction(app.acao_recorte)

        app.acao_borracha = QAction('Borracha', app)
        app.acao_borracha.triggered.connect(
            lambda: app.abrir_ferramenta_borracha()
        )
        app.acao_borracha.setEnabled(False)
        app.menu_ferramentas.addAction(app.acao_borracha)

        app.acao_recorte_massa = QAction('Recorte em Massa', app)
        app.acao_recorte_massa.triggered.connect(
            lambda: app.recortar_imagens_em_massa()
        )
        app.menu_ferramentas.addAction(app.acao_recorte_massa)

        # Menu Ajuda
        app.menu_ajuda = app.menu_principal.addMenu('Ajuda')

        app.acao_sobre = QAction('Sobre', app)
        app.acao_sobre.triggered.connect(lambda: app.mostrar_sobre())
        app.menu_ajuda.addAction(app.acao_sobre)

    @staticmethod
    def criar_frame_principal(app):
        """Cria o frame principal da aplicação"""
        app.frame_principal = QWidget()
        app.layout_frame_principal = QHBoxLayout(app.frame_principal)

        InterfaceConstrutor.criar_painel_original(app)
        InterfaceConstrutor.criar_painel_resultado(app)
        InterfaceConstrutor.criar_painel_ajustes(app)

        app.layout_principal.addWidget(app.frame_principal, 1)

    @staticmethod
    def criar_painel_original(app):
        """Cria o painel da imagem original"""
        app.frame_original = QWidget()
        app.layout_original = QVBoxLayout(app.frame_original)
        app.layout_original.setContentsMargins(5, 5, 5, 5)

        # Título do painel com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(11)
        fonte_titulo.setBold(True)

        app.rotulo_original = QLabel('Imagem Original (Preview)')
        app.rotulo_original.setFont(fonte_titulo)
        app.rotulo_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app.rotulo_original.setStyleSheet(ESTILOS_COMPONENTES['titulo_secao'])
        app.layout_original.addWidget(app.rotulo_original)

        # Área de rolagem para a imagem original com estilo melhorado
        app.scroll_area_original = QScrollArea()
        app.scroll_area_original.setWidgetResizable(True)
        app.scroll_area_original.setFrameShape(QFrame.Shape.StyledPanel)
        app.scroll_area_original.setStyleSheet(
            ESTILOS_COMPONENTES['scroll_area']
        )

        # Label para a imagem
        app.label_imagem_original = QLabel()
        app.label_imagem_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app.label_imagem_original.setMinimumSize(400, 300)
        app.label_imagem_original.setStyleSheet(
            ESTILOS_COMPONENTES['label_scroll_area']
        )
        app.scroll_area_original.setWidget(app.label_imagem_original)

        app.layout_original.addWidget(app.scroll_area_original, 1)

        # Botão com estilo melhorado
        app.botao_ver_original = QPushButton('Ver Original')
        app.botao_ver_original.clicked.connect(
            lambda: app.mostrar_imagem_completa('original')
        )
        app.botao_ver_original.setEnabled(False)
        app.layout_original.addWidget(app.botao_ver_original)

        app.layout_frame_principal.addWidget(app.frame_original, 1)

    @staticmethod
    def criar_painel_resultado(app):
        """Cria o painel da imagem resultado"""
        app.frame_resultado = QWidget()
        app.layout_resultado = QVBoxLayout(app.frame_resultado)
        app.layout_resultado.setContentsMargins(5, 5, 5, 5)

        # Título do painel com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(11)
        fonte_titulo.setBold(True)

        app.rotulo_resultado = QLabel('Resultado (Preview)')
        app.rotulo_resultado.setFont(fonte_titulo)
        app.rotulo_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app.rotulo_resultado.setStyleSheet(
            ESTILOS_COMPONENTES['titulo_secao']
        )
        app.layout_resultado.addWidget(app.rotulo_resultado)

        # Área de rolagem para a imagem resultado com estilo melhorado
        app.scroll_area_resultado = QScrollArea()
        app.scroll_area_resultado.setWidgetResizable(True)
        app.scroll_area_resultado.setFrameShape(QFrame.Shape.StyledPanel)
        app.scroll_area_resultado.setStyleSheet(
            ESTILOS_COMPONENTES['scroll_area']
        )

        # Label para a imagem
        app.label_imagem_resultado = QLabel()
        app.label_imagem_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app.label_imagem_resultado.setMinimumSize(400, 300)
        app.label_imagem_resultado.setStyleSheet(
            ESTILOS_COMPONENTES['label_scroll_area']
        )
        app.scroll_area_resultado.setWidget(app.label_imagem_resultado)

        app.layout_resultado.addWidget(app.scroll_area_resultado, 1)

        # Botão com estilo melhorado
        app.botao_ver_resultado = QPushButton('Ver Resultado')
        app.botao_ver_resultado.clicked.connect(
            lambda: app.mostrar_imagem_completa('resultado')
        )
        app.botao_ver_resultado.setEnabled(False)
        app.layout_resultado.addWidget(app.botao_ver_resultado)

        app.layout_frame_principal.addWidget(app.frame_resultado, 1)

    @staticmethod
    def criar_painel_ajustes(app):
        """Cria o painel de ajustes e controles"""
        app.frame_ajustes = QWidget()
        app.frame_ajustes.setFixedWidth(250)
        app.frame_ajustes.setStyleSheet(ESTILOS_COMPONENTES['frame_ajustes'])
        app.layout_ajustes = QVBoxLayout(app.frame_ajustes)
        app.layout_ajustes.setContentsMargins(10, 20, 10, 20)
        app.layout_ajustes.setSpacing(10)

        # Título do painel com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(12)
        fonte_titulo.setBold(True)

        rotulo_ajustes = QLabel('Ajustes e Modelo')
        rotulo_ajustes.setFont(fonte_titulo)
        rotulo_ajustes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rotulo_ajustes.setStyleSheet(
            ESTILOS_COMPONENTES['titulo_painel_ajustes']
        )
        app.layout_ajustes.addWidget(rotulo_ajustes)

        # Botão principal "Remover Fundo" - adicionado aqui para destaque
        app.botao_remover_fundo = QPushButton('Remover Fundo')
        app.botao_remover_fundo.setMinimumHeight(40)  # Botão mais alto para destaque
        app.botao_remover_fundo.setStyleSheet(ESTILOS_COMPONENTES['botao_destaque'])
        app.botao_remover_fundo.clicked.connect(app.processar_imagem)
        app.botao_remover_fundo.setEnabled(False)  # Inicialmente desabilitado
        app.layout_ajustes.addWidget(app.botao_remover_fundo)
        
        # Adiciona um separador para destacar o botão principal
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet(f"background-color: {CORES['borda']};")
        separador.setFixedHeight(2)
        app.layout_ajustes.addWidget(separador)
        
        app.layout_ajustes.addSpacing(10)

        # Seleção de Modelo
        rotulo_modelo = QLabel('Modelo de IA:')
        rotulo_modelo.setStyleSheet('font-weight: bold; margin-top: 5px;')
        app.layout_ajustes.addWidget(rotulo_modelo)

        app.combo_modelo = QComboBox()
        app.combo_modelo.addItems(MODELOS_DISPONIVEIS)
        app.combo_modelo.setCurrentText(MODELO_PADRAO)
        app.combo_modelo.currentTextChanged.connect(app.ao_mudar_modelo)
        app.combo_modelo.setFixedHeight(30)
        app.layout_ajustes.addWidget(app.combo_modelo)

        app.layout_ajustes.addSpacing(10)

        # Controles Alpha Matting
        app.check_alpha_matting = QCheckBox('Alpha Matting')
        app.check_alpha_matting.stateChanged.connect(
            app.ao_mudar_configuracoes
        )
        app.check_alpha_matting.setStyleSheet('font-weight: bold;')
        app.layout_ajustes.addWidget(app.check_alpha_matting)

        app.layout_ajustes.addSpacing(10)

        # Limiar Objeto
        grupo_limiar_objeto = QWidget()
        layout_limiar_objeto = QVBoxLayout(grupo_limiar_objeto)
        layout_limiar_objeto.setContentsMargins(0, 0, 0, 0)
        layout_limiar_objeto.setSpacing(5)

        rotulo_limiar_objeto = QLabel('Limiar Objeto (0-255)')
        rotulo_limiar_objeto.setStyleSheet('font-weight: bold;')
        layout_limiar_objeto.addWidget(rotulo_limiar_objeto)

        app.slider_limiar_objeto = QSlider(Qt.Orientation.Horizontal)
        app.slider_limiar_objeto.setRange(0, 255)
        app.slider_limiar_objeto.setValue(LIMIAR_OBJETO_PADRAO)
        app.slider_limiar_objeto.valueChanged.connect(
            lambda v: app.atualizar_rotulo_slider(
                v, app.rotulo_limiar_objeto, 'Limiar Objeto'
            )
        )
        layout_limiar_objeto.addWidget(app.slider_limiar_objeto)

        app.rotulo_limiar_objeto = QLabel(
            f'Limiar Objeto: {LIMIAR_OBJETO_PADRAO}'
        )
        layout_limiar_objeto.addWidget(app.rotulo_limiar_objeto)

        app.layout_ajustes.addWidget(grupo_limiar_objeto)

        # Limiar Fundo
        grupo_limiar_fundo = QWidget()
        layout_limiar_fundo = QVBoxLayout(grupo_limiar_fundo)
        layout_limiar_fundo.setContentsMargins(0, 0, 0, 0)
        layout_limiar_fundo.setSpacing(5)

        rotulo_limiar_fundo = QLabel('Limiar Fundo (0-255)')
        rotulo_limiar_fundo.setStyleSheet('font-weight: bold;')
        layout_limiar_fundo.addWidget(rotulo_limiar_fundo)

        app.slider_limiar_fundo = QSlider(Qt.Orientation.Horizontal)
        app.slider_limiar_fundo.setRange(0, 255)
        app.slider_limiar_fundo.setValue(LIMIAR_FUNDO_PADRAO)
        app.slider_limiar_fundo.valueChanged.connect(
            lambda v: app.atualizar_rotulo_slider(
                v, app.rotulo_limiar_fundo, 'Limiar Fundo'
            )
        )
        layout_limiar_fundo.addWidget(app.slider_limiar_fundo)

        app.rotulo_limiar_fundo = QLabel(
            f'Limiar Fundo: {LIMIAR_FUNDO_PADRAO}'
        )
        layout_limiar_fundo.addWidget(app.rotulo_limiar_fundo)

        app.layout_ajustes.addWidget(grupo_limiar_fundo)

        # Erosão Máscara
        grupo_erosao = QWidget()
        layout_erosao = QVBoxLayout(grupo_erosao)
        layout_erosao.setContentsMargins(0, 0, 0, 0)
        layout_erosao.setSpacing(5)

        rotulo_erosao = QLabel('Erosão Máscara (0-50)')
        rotulo_erosao.setStyleSheet('font-weight: bold;')
        layout_erosao.addWidget(rotulo_erosao)

        app.slider_erosao = QSlider(Qt.Orientation.Horizontal)
        app.slider_erosao.setRange(0, 50)
        app.slider_erosao.setValue(EROSAO_MASCARA_PADRAO)
        app.slider_erosao.valueChanged.connect(
            lambda v: app.atualizar_rotulo_slider(
                v, app.rotulo_erosao, 'Erosão Máscara'
            )
        )
        layout_erosao.addWidget(app.slider_erosao)

        app.rotulo_erosao = QLabel(f'Erosão Máscara: {EROSAO_MASCARA_PADRAO}')
        layout_erosao.addWidget(app.rotulo_erosao)

        app.layout_ajustes.addWidget(grupo_erosao)

        app.layout_ajustes.addSpacing(20)

        # Botão Restaurar Padrões com estilo melhorado
        app.botao_restaurar_padroes = QPushButton('Restaurar Padrões')
        app.botao_restaurar_padroes.clicked.connect(app.restaurar_padroes)
        app.botao_restaurar_padroes.setStyleSheet(ESTILOS_COMPONENTES['botao_restaurar'])
        app.layout_ajustes.addWidget(app.botao_restaurar_padroes)

        # Adicionar espaçador para empurrar widgets para cima
        app.layout_ajustes.addStretch(1)

        app.layout_frame_principal.addWidget(app.frame_ajustes)

    @staticmethod
    def criar_barra_status(app):
        """Cria a barra de status e progresso"""
        app.barra_status = app.statusBar()
        app.barra_status.setFixedHeight(28)

        app.rotulo_status = QLabel('Pronto')
        app.rotulo_status.setStyleSheet('color: white; padding: 0 10px;')
        app.barra_status.addWidget(app.rotulo_status, 1)

        app.barra_progresso = QProgressBar()
        app.barra_progresso.setFixedWidth(200)
        app.barra_progresso.setFixedHeight(18)
        app.barra_progresso.setVisible(False)
        app.barra_status.addPermanentWidget(app.barra_progresso)
