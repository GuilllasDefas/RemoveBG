import io
import os
import threading

from PIL import Image, ImageQt
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import (QAction, QColor, QFont, QFontDatabase, QIcon,
                         QPalette, QPixmap)
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QFrame,
                             QGridLayout, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QProgressBar, QPushButton,
                             QScrollArea, QSlider, QStatusBar, QVBoxLayout,
                             QWidget)

from app.configuracoes import (ALPHA_MATTING_PADRAO, EROSAO_MASCARA_PADRAO,
                               EXTENSOES_SUPORTADAS, LIMIAR_FUNDO_PADRAO,
                               LIMIAR_OBJETO_PADRAO, MODELO_PADRAO,
                               MODELOS_DISPONIVEIS, TITULO_APP, VERSAO)
from app.gui.componentes import DicaFlutuante
from app.utils.estilos import (CORES, ESTILOS_COMPONENTES, FONTES,
                             configurar_paleta, obter_estilo_global)
from app.gui.janela_borracha import JanelaBorracha
from app.gui.janela_recorte import JanelaRecorte
from app.gui.visualizador import VisualizadorImagem
from app.processadores.editor_imagem import EditorImagem
from app.processadores.removedor_fundo import RemoveFundo
from app.utils.imagem_utils import carregar_imagem, criar_preview


class ProcessadorThread(QThread):
    """Thread para processar imagens em segundo plano"""

    concluido = pyqtSignal(object)
    progresso = pyqtSignal(float, str)
    erro = pyqtSignal(str)

    def __init__(self, funcao, *args, **kwargs):
        super().__init__()
        self.funcao = funcao
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            resultado = self.funcao(*self.args, **self.kwargs)
            self.concluido.emit(resultado)
        except Exception as e:
            self.erro.emit(str(e))


class AplicativoRemoveFundo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(TITULO_APP)
        self.resize(1250, 850)
        self.setWindowIcon(QIcon('app/gui/icon.ico'))

        # Configurar esquema de cores e estilos
        self.configurar_estilo()

        # Variáveis para guardar o modelo selecionado
        self.modelo_selecionado = MODELO_PADRAO

        # Objeto removedor de fundo
        self.removedor = RemoveFundo(self.modelo_selecionado)

        # Widget central
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)

        # Layout principal
        self.layout_principal = QVBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)
        self.layout_principal.setSpacing(10)

        # --- Criação da GUI ---
        self.criar_cabecalho()
        self.criar_menu()
        self.criar_frame_principal()
        self.criar_barra_status()

        # --- Variáveis de Estado ---
        self.imagem_entrada_completa = None
        self.imagem_resultado_completa = None
        self.pixmap_entrada = None
        self.pixmap_resultado = None
        self.caminho_arquivo_atual = None
        self.processamento_ativo = False

        # Inicializar as configurações padrão
        self.restaurar_padroes()

        # Atualizar estados dos menus
        self.atualizar_estados_menu()

    def configurar_estilo(self):
        """Configura o estilo visual da aplicação"""
        # Definir paleta de cores
        self.setPalette(configurar_paleta(self))

        # Aplicar estilo global
        self.setStyleSheet(obter_estilo_global())

    def criar_cabecalho(self):
        """Cria o cabeçalho da aplicação"""
        self.frame_cabecalho = QWidget()
        self.layout_cabecalho = QHBoxLayout(self.frame_cabecalho)
        self.layout_cabecalho.setContentsMargins(10, 10, 10, 20)

        # Logo à esquerda
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        self.botao_sobre = QPushButton('Sobre')
        self.botao_sobre.setFixedWidth(100)
        self.botao_sobre.clicked.connect(self.mostrar_sobre)
        logo_layout.addWidget(self.botao_sobre)
        self.layout_cabecalho.addWidget(logo_container)

        # Título centralizado com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(22)
        fonte_titulo.setBold(True)

        self.rotulo_cabecalho = QLabel(f'Removedor de Fundos v{VERSAO} - Beta')
        self.rotulo_cabecalho.setFont(fonte_titulo)
        self.rotulo_cabecalho.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rotulo_cabecalho.setStyleSheet(
            ESTILOS_COMPONENTES['cabecalho_titulo']
        )
        self.layout_cabecalho.addWidget(self.rotulo_cabecalho, 1)

        # Espaço à direita para equilíbrio
        self.layout_cabecalho.addSpacing(100)

        self.layout_principal.addWidget(self.frame_cabecalho)

        # Linha divisória
        linha_divisoria = QFrame()
        linha_divisoria.setFrameShape(QFrame.Shape.HLine)
        linha_divisoria.setFrameShadow(QFrame.Shadow.Sunken)
        linha_divisoria.setObjectName('FrameDivisor')
        linha_divisoria.setFixedHeight(2)
        self.layout_principal.addWidget(linha_divisoria)

    def criar_menu(self):
        """Cria o menu principal da aplicação"""
        self.menu_principal = self.menuBar()

        # Menu Arquivo
        self.menu_arquivo = self.menu_principal.addMenu('Arquivo')

        self.acao_selecionar = QAction('Selecionar Imagem', self)
        self.acao_selecionar.triggered.connect(self.selecionar_imagem)
        self.menu_arquivo.addAction(self.acao_selecionar)

        self.acao_salvar = QAction('Salvar Resultado', self)
        self.acao_salvar.triggered.connect(lambda: self.salvar_imagem())
        self.acao_salvar.setEnabled(False)
        self.menu_arquivo.addAction(self.acao_salvar)

        self.menu_arquivo.addSeparator()

        self.acao_sair = QAction('Sair', self)
        self.acao_sair.triggered.connect(self.close)
        self.menu_arquivo.addAction(self.acao_sair)

        # Menu Ferramentas
        self.menu_ferramentas = self.menu_principal.addMenu('Ferramentas')

        self.acao_pasta = QAction('Processar Pasta', self)
        self.acao_pasta.triggered.connect(lambda: self.processar_pasta())
        self.menu_ferramentas.addAction(self.acao_pasta)

        # Removendo o botão "Aplicar Ajustes" pois já temos o botão "Remover Fundo"
        # que faz a mesma função

        self.acao_recorte = QAction('Cortar Imagem', self)
        self.acao_recorte.triggered.connect(
            lambda: self.abrir_ferramenta_recorte()
        )
        self.acao_recorte.setEnabled(False)
        self.menu_ferramentas.addAction(self.acao_recorte)

        self.acao_borracha = QAction('Borracha', self)
        self.acao_borracha.triggered.connect(
            lambda: self.abrir_ferramenta_borracha()
        )
        self.acao_borracha.setEnabled(False)
        self.menu_ferramentas.addAction(self.acao_borracha)

        self.acao_recorte_massa = QAction('Recorte em Massa', self)
        self.acao_recorte_massa.triggered.connect(
            lambda: self.recortar_imagens_em_massa()
        )
        self.menu_ferramentas.addAction(self.acao_recorte_massa)

        # Menu Ajuda
        self.menu_ajuda = self.menu_principal.addMenu('Ajuda')

        self.acao_sobre = QAction('Sobre', self)
        self.acao_sobre.triggered.connect(lambda: self.mostrar_sobre())
        self.menu_ajuda.addAction(self.acao_sobre)

    def criar_frame_principal(self):
        """Cria o frame principal da aplicação"""
        self.frame_principal = QWidget()
        self.layout_frame_principal = QHBoxLayout(self.frame_principal)

        self.criar_painel_original()
        self.criar_painel_resultado()
        self.criar_painel_ajustes()

        self.layout_principal.addWidget(self.frame_principal, 1)

    def criar_painel_original(self):
        """Cria o painel da imagem original"""
        self.frame_original = QWidget()
        self.layout_original = QVBoxLayout(self.frame_original)
        self.layout_original.setContentsMargins(5, 5, 5, 5)

        # Título do painel com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(11)
        fonte_titulo.setBold(True)

        self.rotulo_original = QLabel('Imagem Original (Preview)')
        self.rotulo_original.setFont(fonte_titulo)
        self.rotulo_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rotulo_original.setStyleSheet(ESTILOS_COMPONENTES['titulo_secao'])
        self.layout_original.addWidget(self.rotulo_original)

        # Área de rolagem para a imagem original com estilo melhorado
        self.scroll_area_original = QScrollArea()
        self.scroll_area_original.setWidgetResizable(True)
        self.scroll_area_original.setFrameShape(QFrame.Shape.StyledPanel)
        self.scroll_area_original.setStyleSheet(
            ESTILOS_COMPONENTES['scroll_area']
        )

        # Label para a imagem
        self.label_imagem_original = QLabel()
        self.label_imagem_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagem_original.setMinimumSize(400, 300)
        self.label_imagem_original.setStyleSheet(
            ESTILOS_COMPONENTES['label_scroll_area']
        )
        self.scroll_area_original.setWidget(self.label_imagem_original)

        self.layout_original.addWidget(self.scroll_area_original, 1)

        # Botão com estilo melhorado
        self.botao_ver_original = QPushButton('Ver Original')
        self.botao_ver_original.clicked.connect(
            lambda: self.mostrar_imagem_completa('original')
        )
        self.botao_ver_original.setEnabled(False)
        self.layout_original.addWidget(self.botao_ver_original)

        self.layout_frame_principal.addWidget(self.frame_original, 1)

    def criar_painel_resultado(self):
        """Cria o painel da imagem resultado"""
        self.frame_resultado = QWidget()
        self.layout_resultado = QVBoxLayout(self.frame_resultado)
        self.layout_resultado.setContentsMargins(5, 5, 5, 5)

        # Título do painel com estilo melhorado
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(11)
        fonte_titulo.setBold(True)

        self.rotulo_resultado = QLabel('Resultado (Preview)')
        self.rotulo_resultado.setFont(fonte_titulo)
        self.rotulo_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rotulo_resultado.setStyleSheet(
            ESTILOS_COMPONENTES['titulo_secao']
        )
        self.layout_resultado.addWidget(self.rotulo_resultado)

        # Área de rolagem para a imagem resultado com estilo melhorado
        self.scroll_area_resultado = QScrollArea()
        self.scroll_area_resultado.setWidgetResizable(True)
        self.scroll_area_resultado.setFrameShape(QFrame.Shape.StyledPanel)
        self.scroll_area_resultado.setStyleSheet(
            ESTILOS_COMPONENTES['scroll_area']
        )

        # Label para a imagem
        self.label_imagem_resultado = QLabel()
        self.label_imagem_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagem_resultado.setMinimumSize(400, 300)
        self.label_imagem_resultado.setStyleSheet(
            ESTILOS_COMPONENTES['label_scroll_area']
        )
        self.scroll_area_resultado.setWidget(self.label_imagem_resultado)

        self.layout_resultado.addWidget(self.scroll_area_resultado, 1)

        # Botão com estilo melhorado
        self.botao_ver_resultado = QPushButton('Ver Resultado')
        self.botao_ver_resultado.clicked.connect(
            lambda: self.mostrar_imagem_completa('resultado')
        )
        self.botao_ver_resultado.setEnabled(False)
        self.layout_resultado.addWidget(self.botao_ver_resultado)

        self.layout_frame_principal.addWidget(self.frame_resultado, 1)

    def criar_painel_ajustes(self):
        """Cria o painel de ajustes e controles"""
        self.frame_ajustes = QWidget()
        self.frame_ajustes.setFixedWidth(250)
        self.frame_ajustes.setStyleSheet(ESTILOS_COMPONENTES['frame_ajustes'])
        self.layout_ajustes = QVBoxLayout(self.frame_ajustes)
        self.layout_ajustes.setContentsMargins(10, 20, 10, 20)
        self.layout_ajustes.setSpacing(10)

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
        self.layout_ajustes.addWidget(rotulo_ajustes)

        # Botão principal "Remover Fundo" - adicionado aqui para destaque
        self.botao_remover_fundo = QPushButton('Remover Fundo')
        self.botao_remover_fundo.setMinimumHeight(40)  # Botão mais alto para destaque
        self.botao_remover_fundo.setStyleSheet(ESTILOS_COMPONENTES['botao_destaque'])
        self.botao_remover_fundo.clicked.connect(self.processar_imagem)
        self.botao_remover_fundo.setEnabled(False)  # Inicialmente desabilitado
        self.layout_ajustes.addWidget(self.botao_remover_fundo)
        
        # Adiciona um separador para destacar o botão principal
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet(f"background-color: {CORES['borda']};")
        separador.setFixedHeight(2)
        self.layout_ajustes.addWidget(separador)
        
        self.layout_ajustes.addSpacing(10)

        # Seleção de Modelo
        rotulo_modelo = QLabel('Modelo de IA:')
        rotulo_modelo.setStyleSheet('font-weight: bold; margin-top: 5px;')
        self.layout_ajustes.addWidget(rotulo_modelo)

        self.combo_modelo = QComboBox()
        self.combo_modelo.addItems(MODELOS_DISPONIVEIS)
        self.combo_modelo.setCurrentText(MODELO_PADRAO)
        self.combo_modelo.currentTextChanged.connect(self.ao_mudar_modelo)
        self.combo_modelo.setFixedHeight(30)
        self.layout_ajustes.addWidget(self.combo_modelo)

        self.layout_ajustes.addSpacing(10)

        # Controles Alpha Matting
        self.check_alpha_matting = QCheckBox('Alpha Matting')
        self.check_alpha_matting.stateChanged.connect(
            self.ao_mudar_configuracoes
        )
        self.check_alpha_matting.setStyleSheet('font-weight: bold;')
        self.layout_ajustes.addWidget(self.check_alpha_matting)

        self.layout_ajustes.addSpacing(10)

        # Limiar Objeto
        grupo_limiar_objeto = QWidget()
        layout_limiar_objeto = QVBoxLayout(grupo_limiar_objeto)
        layout_limiar_objeto.setContentsMargins(0, 0, 0, 0)
        layout_limiar_objeto.setSpacing(5)

        rotulo_limiar_objeto = QLabel('Limiar Objeto (0-255)')
        rotulo_limiar_objeto.setStyleSheet('font-weight: bold;')
        layout_limiar_objeto.addWidget(rotulo_limiar_objeto)

        self.slider_limiar_objeto = QSlider(Qt.Orientation.Horizontal)
        self.slider_limiar_objeto.setRange(0, 255)
        self.slider_limiar_objeto.setValue(LIMIAR_OBJETO_PADRAO)
        self.slider_limiar_objeto.valueChanged.connect(
            lambda v: self.atualizar_rotulo_slider(
                v, self.rotulo_limiar_objeto, 'Limiar Objeto'
            )
        )
        layout_limiar_objeto.addWidget(self.slider_limiar_objeto)

        self.rotulo_limiar_objeto = QLabel(
            f'Limiar Objeto: {LIMIAR_OBJETO_PADRAO}'
        )
        layout_limiar_objeto.addWidget(self.rotulo_limiar_objeto)

        self.layout_ajustes.addWidget(grupo_limiar_objeto)

        # Limiar Fundo
        grupo_limiar_fundo = QWidget()
        layout_limiar_fundo = QVBoxLayout(grupo_limiar_fundo)
        layout_limiar_fundo.setContentsMargins(0, 0, 0, 0)
        layout_limiar_fundo.setSpacing(5)

        rotulo_limiar_fundo = QLabel('Limiar Fundo (0-255)')
        rotulo_limiar_fundo.setStyleSheet('font-weight: bold;')
        layout_limiar_fundo.addWidget(rotulo_limiar_fundo)

        self.slider_limiar_fundo = QSlider(Qt.Orientation.Horizontal)
        self.slider_limiar_fundo.setRange(0, 255)
        self.slider_limiar_fundo.setValue(LIMIAR_FUNDO_PADRAO)
        self.slider_limiar_fundo.valueChanged.connect(
            lambda v: self.atualizar_rotulo_slider(
                v, self.rotulo_limiar_fundo, 'Limiar Fundo'
            )
        )
        layout_limiar_fundo.addWidget(self.slider_limiar_fundo)

        self.rotulo_limiar_fundo = QLabel(
            f'Limiar Fundo: {LIMIAR_FUNDO_PADRAO}'
        )
        layout_limiar_fundo.addWidget(self.rotulo_limiar_fundo)

        self.layout_ajustes.addWidget(grupo_limiar_fundo)

        # Erosão Máscara
        grupo_erosao = QWidget()
        layout_erosao = QVBoxLayout(grupo_erosao)
        layout_erosao.setContentsMargins(0, 0, 0, 0)
        layout_erosao.setSpacing(5)

        rotulo_erosao = QLabel('Erosão Máscara (0-50)')
        rotulo_erosao.setStyleSheet('font-weight: bold;')
        layout_erosao.addWidget(rotulo_erosao)

        self.slider_erosao = QSlider(Qt.Orientation.Horizontal)
        self.slider_erosao.setRange(0, 50)
        self.slider_erosao.setValue(EROSAO_MASCARA_PADRAO)
        self.slider_erosao.valueChanged.connect(
            lambda v: self.atualizar_rotulo_slider(
                v, self.rotulo_erosao, 'Erosão Máscara'
            )
        )
        layout_erosao.addWidget(self.slider_erosao)

        self.rotulo_erosao = QLabel(f'Erosão Máscara: {EROSAO_MASCARA_PADRAO}')
        layout_erosao.addWidget(self.rotulo_erosao)

        self.layout_ajustes.addWidget(grupo_erosao)

        self.layout_ajustes.addSpacing(20)

        # Botão Restaurar Padrões com estilo melhorado
        self.botao_restaurar_padroes = QPushButton('Restaurar Padrões')
        self.botao_restaurar_padroes.clicked.connect(self.restaurar_padroes)
        self.botao_restaurar_padroes.setStyleSheet(ESTILOS_COMPONENTES['botao_restaurar'])
        self.layout_ajustes.addWidget(self.botao_restaurar_padroes)

        # Adicionar espaçador para empurrar widgets para cima
        self.layout_ajustes.addStretch(1)

        self.layout_frame_principal.addWidget(self.frame_ajustes)

    def criar_barra_status(self):
        """Cria a barra de status e progresso"""
        self.barra_status = QStatusBar()
        self.setStatusBar(self.barra_status)
        self.barra_status.setFixedHeight(28)

        self.rotulo_status = QLabel('Pronto')
        self.rotulo_status.setStyleSheet('color: white; padding: 0 10px;')
        self.barra_status.addWidget(self.rotulo_status, 1)

        self.barra_progresso = QProgressBar()
        self.barra_progresso.setFixedWidth(200)
        self.barra_progresso.setFixedHeight(18)
        self.barra_progresso.setVisible(False)
        self.barra_status.addPermanentWidget(self.barra_progresso)

    def atualizar_estados_menu(self):
        """Atualiza os estados dos itens do menu com base no estado atual da aplicação"""
        tem_resultado = self.imagem_resultado_completa is not None
        tem_imagem = self.imagem_entrada_completa is not None

        self.acao_salvar.setEnabled(tem_resultado)
        # Removida a referência ao self.acao_processar
        self.acao_recorte.setEnabled(tem_imagem)
        self.acao_borracha.setEnabled(tem_imagem)
        self.botao_ver_resultado.setEnabled(tem_resultado)
        
        # Atualizar o estado do botão principal
        self.botao_remover_fundo.setEnabled(tem_imagem and not self.processamento_ativo)

    def mostrar_sobre(self):
        """Exibe informações sobre o aplicativo"""
        texto_info = (
            f'Remover Fundo v{VERSAO}\n\n'
            'Criado por: Guilherme de Freitas Moreira\n'
            'Funcionalidades:\n'
            '- Remove fundo de imagens (PNG, JPG, JPEG, WEBP).\n'
            '- Processamento em lote de pastas.\n'
            '- Visualização de alta resolução com Zoom.\n'
            '- Seleção de Modelo de IA (afeta qualidade e velocidade).\n'
            '- Ajustes finos (Alpha Matting, Limiares, Erosão) para refinar o recorte.\n'
            '- Barra de progresso para lotes.\n\n'
            'Dica: Passe o mouse sobre os controles de ajuste para ver o que eles fazem! '
            'Experimente diferentes modelos e ajustes para obter o melhor resultado.'
        )
        QMessageBox.information(self, 'Sobre', texto_info)

    def ao_mudar_modelo(self, modelo_selecionado):
        """Chamado quando o usuário seleciona um novo modelo"""
        print(f'Modelo selecionado: {modelo_selecionado}')
        try:
            # Atualiza o modelo no removedor
            self.modelo_selecionado = modelo_selecionado
            self.removedor.mudar_modelo(modelo_selecionado)
            print('Sessão rembg atualizada.')
            # Habilita o botão de reprocessar se uma imagem estiver carregada
            self.ao_mudar_configuracoes()
        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro de Modelo',
                f"Não foi possível carregar o modelo '{modelo_selecionado}':\n{e}\n\n"
                'Verifique se o rembg e suas dependências estão instalados corretamente '
                'ou se o modelo é válido.',
            )
            self.combo_modelo.setCurrentText(MODELO_PADRAO)
            self.removedor.mudar_modelo(MODELO_PADRAO)

    def atualizar_rotulo_slider(self, valor, rotulo, prefixo):
        """Atualiza o texto do rótulo de um slider e habilita reprocessamento"""
        rotulo.setText(f'{prefixo}: {valor}')
        self.ao_mudar_configuracoes()

    def ao_mudar_configuracoes(self):
        """Chamado quando qualquer controle de ajuste (slider, checkbox, modelo) muda"""
        if self.imagem_entrada_completa and not self.processamento_ativo:
            self.atualizar_estados_menu()

    def selecionar_imagem(self):
        """Abre o diálogo para selecionar uma imagem"""
        if self.processamento_ativo:
            QMessageBox.warning(
                self, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        tipos_arquivo = f"Arquivos de Imagem ({' '.join(['*' + ext for ext in EXTENSOES_SUPORTADAS])})"
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self, 'Selecione a Imagem', '', tipos_arquivo
        )

        if caminho_arquivo:
            try:
                self.rotulo_status.setText('Carregando imagem...')

                imagem = carregar_imagem(caminho_arquivo)
                self.imagem_entrada_completa = imagem
                self.caminho_arquivo_atual = caminho_arquivo
                self.imagem_resultado_completa = None

                self.exibir_imagem_no_label(
                    self.label_imagem_original, self.imagem_entrada_completa
                )
                self.label_imagem_resultado.clear()

                self.botao_ver_original.setEnabled(True)
                self.botao_ver_resultado.setEnabled(False)
                self.rotulo_status.setText(
                    f'Imagem carregada: {os.path.basename(caminho_arquivo)}'
                )
                self.atualizar_estados_menu()

            except Exception as e:
                QMessageBox.critical(
                    self, 'Erro', f'Falha ao abrir a imagem:\n{e}'
                )
                self.rotulo_status.setText('Erro ao carregar imagem!')
                self.resetar_estado_interface()

    def exibir_imagem_no_label(self, label, imagem_pil):
        """Exibe uma imagem PIL no label especificado"""
        try:
            # Obter o tamanho disponível para exibição
            largura_disponivel = label.width()
            altura_disponivel = label.height()

            if largura_disponivel <= 1 or altura_disponivel <= 1:
                # Se o widget ainda não foi renderizado completamente
                largura_disponivel = 400
                altura_disponivel = 300

            # Criar preview redimensionado
            imagem_preview = criar_preview(
                imagem_pil, largura_disponivel, altura_disponivel
            )

            # Converter de PIL para QPixmap
            q_imagem = ImageQt.ImageQt(imagem_preview)
            pixmap = QPixmap.fromImage(q_imagem)

            # Definir a imagem no label
            label.setPixmap(pixmap)

        except Exception as e:
            print(f'Erro ao exibir imagem no label: {e}')

    def aplicar_recorte(self, imagem_recortada, caixa_recorte=None):
        """Callback chamado quando o recorte é concluído"""
        # Em vez de modificar a imagem original, definimos o resultado
        self.imagem_resultado_completa = imagem_recortada
        self.exibir_imagem_no_label(
            self.label_imagem_resultado, self.imagem_resultado_completa
        )
        self.atualizar_estados_menu()

        self.rotulo_status.setText('Imagem recortada com sucesso.')

    def abrir_ferramenta_borracha(self):
        """Abre a janela para apagar áreas da imagem com uma borracha"""
        if not self.imagem_entrada_completa:
            QMessageBox.warning(
                self, 'Atenção', 'Nenhuma imagem carregada para edição!'
            )
            return

        # Se já tiver uma imagem resultado, use-a como base para edição
        imagem_base = (
            self.imagem_resultado_completa
            if self.imagem_resultado_completa
            else self.imagem_entrada_completa
        )

        janela_borracha = JanelaBorracha(
            self, imagem_base, self.aplicar_borracha
        )
        janela_borracha.exec()

    def aplicar_borracha(self, imagem_editada):
        """Callback chamado quando a edição com borracha é concluída"""
        # Em vez de modificar a imagem original, definimos o resultado
        self.imagem_resultado_completa = imagem_editada
        self.exibir_imagem_no_label(
            self.label_imagem_resultado, self.imagem_resultado_completa
        )
        self.atualizar_estados_menu()

        self.rotulo_status.setText('Imagem editada com sucesso.')

    def abrir_ferramenta_recorte(self):
        """Abre a janela para recortar a imagem"""
        if not self.imagem_entrada_completa:
            QMessageBox.warning(
                self, 'Atenção', 'Nenhuma imagem carregada para recorte!'
            )
            return

        # Se já tiver uma imagem resultado, use-a como base para recorte
        imagem_base = (
            self.imagem_resultado_completa
            if self.imagem_resultado_completa
            else self.imagem_entrada_completa
        )

        janela_recorte = JanelaRecorte(self, imagem_base, self.aplicar_recorte)
        janela_recorte.exec()

    def processar_imagem(self):
        """Processa a imagem para remover o fundo"""
        if not self.imagem_entrada_completa:
            QMessageBox.warning(
                self, 'Atenção', 'Selecione uma imagem primeiro!'
            )
            return

        if self.processamento_ativo:
            QMessageBox.warning(
                self, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        # Obter valores de configuração
        usar_alpha_matting = self.check_alpha_matting.isChecked()
        limiar_objeto = self.slider_limiar_objeto.value()
        limiar_fundo = self.slider_limiar_fundo.value()
        tamanho_erosao = self.slider_erosao.value()

        # Iniciar thread de processamento
        self.processamento_ativo = True
        self.definir_interface_processando(True)
        self.rotulo_status.setText(
            f"Processando com modelo '{self.modelo_selecionado}'..."
        )

        # Criar thread de processamento
        self.thread_processamento = ProcessadorThread(
            self.removedor.processar_imagem,
            self.imagem_entrada_completa,
            usar_alpha_matting,
            limiar_objeto,
            limiar_fundo,
            tamanho_erosao,
        )

        # Conectar sinais
        self.thread_processamento.concluido.connect(
            self.finalizar_processamento
        )
        self.thread_processamento.erro.connect(self.erro_processamento)

        # Iniciar thread
        self.thread_processamento.start()

    def finalizar_processamento(self, imagem_resultado):
        """Chamado quando o processamento é concluído com sucesso"""
        self.imagem_resultado_completa = imagem_resultado
        self.exibir_imagem_no_label(
            self.label_imagem_resultado, self.imagem_resultado_completa
        )
        self.rotulo_status.setText('Processamento concluído!')
        self.botao_ver_resultado.setEnabled(True)

        self.processamento_ativo = False
        self.definir_interface_processando(False)
        self.atualizar_estados_menu()

    def erro_processamento(self, mensagem_erro):
        """Chamado quando ocorre um erro durante o processamento"""
        QMessageBox.critical(
            self,
            'Erro de Processamento',
            f'Falha ao remover o fundo:\n{mensagem_erro}',
        )
        self.rotulo_status.setText('Erro no processamento!')

        self.processamento_ativo = False
        self.definir_interface_processando(False)

    def definir_interface_processando(self, processando):
        """Atualiza o estado da interface durante o processamento"""
        estado = not processando  # True se não estiver processando

        # Atualizar estado dos menus
        self.menu_arquivo.setEnabled(estado)
        self.menu_ferramentas.setEnabled(estado)
        self.menu_ajuda.setEnabled(estado)
        
        # Desabilitar o botão principal durante o processamento
        self.botao_remover_fundo.setEnabled(estado and self.imagem_entrada_completa is not None)

        # Exibir ou ocultar a barra de progresso
        self.barra_progresso.setVisible(processando)
        if processando:
            self.barra_progresso.setValue(0)

    def resetar_estado_interface(self):
        """Reseta o estado da interface"""
        self.imagem_entrada_completa = None
        self.imagem_resultado_completa = None
        self.caminho_arquivo_atual = None

        self.label_imagem_original.clear()
        self.label_imagem_resultado.clear()

        self.definir_interface_processando(False)
        self.rotulo_status.setText('Pronto')
        self.botao_ver_original.setEnabled(False)
        self.botao_ver_resultado.setEnabled(False)
        self.atualizar_estados_menu()

    def salvar_imagem(self):
        """Salva a imagem resultante (processada ou editada)"""
        if not self.imagem_resultado_completa:
            QMessageBox.warning(
                self,
                'Atenção',
                'Não há imagem processada ou editada para salvar!',
            )
            return

        if self.processamento_ativo:
            QMessageBox.warning(
                self, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        nome_arquivo_original = os.path.basename(
            self.caminho_arquivo_atual or 'imagem'
        )
        nome, _ = os.path.splitext(nome_arquivo_original)
        nome_padrao = f'{nome}_editado.png'

        caminho_arquivo, _ = QFileDialog.getSaveFileName(
            self, 'Salvar Imagem', nome_padrao, 'Arquivos PNG (*.png)'
        )

        if caminho_arquivo:
            try:
                self.rotulo_status.setText('Salvando imagem...')
                self.imagem_resultado_completa.save(caminho_arquivo)
                self.rotulo_status.setText('Imagem salva com sucesso!')
            except Exception as e:
                QMessageBox.critical(
                    self, 'Erro', f'Falha ao salvar a imagem:\n{e}'
                )
                self.rotulo_status.setText('Erro ao salvar!')

    def restaurar_padroes(self):
        """Restaura as configurações para os valores padrão"""
        # Modelo
        self.modelo_selecionado = MODELO_PADRAO
        self.combo_modelo.setCurrentText(MODELO_PADRAO)

        try:
            self.removedor.mudar_modelo(MODELO_PADRAO)
            print('Sessão rembg restaurada para o padrão:', MODELO_PADRAO)
        except Exception as e:
            QMessageBox.critical(
                self, 'Erro', f'Falha ao restaurar o modelo padrão:\n{e}'
            )

        # Outros controles
        self.check_alpha_matting.setChecked(ALPHA_MATTING_PADRAO)
        self.slider_limiar_objeto.setValue(LIMIAR_OBJETO_PADRAO)
        self.slider_limiar_fundo.setValue(LIMIAR_FUNDO_PADRAO)
        self.slider_erosao.setValue(EROSAO_MASCARA_PADRAO)

        # Atualizar rótulos
        self.rotulo_limiar_objeto.setText(
            f'Limiar Objeto: {LIMIAR_OBJETO_PADRAO}'
        )
        self.rotulo_limiar_fundo.setText(
            f'Limiar Fundo: {LIMIAR_FUNDO_PADRAO}'
        )
        self.rotulo_erosao.setText(f'Erosão Máscara: {EROSAO_MASCARA_PADRAO}')

        self.rotulo_status.setText('Valores restaurados para os padrões.')

    def processar_pasta(self):
        """Abre diálogos para processar todas as imagens em uma pasta"""
        if self.processamento_ativo:
            QMessageBox.warning(
                self, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        pasta_origem = QFileDialog.getExistingDirectory(
            self, 'Selecione a Pasta com Imagens'
        )
        if not pasta_origem:
            return

        pasta_destino = QFileDialog.getExistingDirectory(
            self, 'Selecione a Pasta de Destino'
        )
        if not pasta_destino:
            return

        if pasta_origem == pasta_destino:
            QMessageBox.critical(
                self,
                'Erro',
                'A pasta de origem e destino não podem ser a mesma.',
            )
            return

        # Identificar as imagens na pasta
        imagens = [
            f
            for f in os.listdir(pasta_origem)
            if os.path.isfile(os.path.join(pasta_origem, f))
            and f.lower().endswith(tuple(EXTENSOES_SUPORTADAS))
        ]

        if not imagens:
            QMessageBox.information(
                self,
                'Informação',
                'Nenhuma imagem compatível encontrada na pasta selecionada.',
            )
            return

        total_arquivos = len(imagens)
        nome_modelo = self.modelo_selecionado

        # Preparar interface para processamento
        self.processamento_ativo = True
        self.definir_interface_processando(True)
        self.barra_progresso.setVisible(True)
        self.barra_progresso.setValue(0)
        self.rotulo_status.setText(
            f'Iniciando lote ({nome_modelo}): {total_arquivos} imagens...'
        )

        # Criar thread do processador de lotes
        self.thread_lote = ProcessadorLoteThread(
            self,
            pasta_origem,
            pasta_destino,
            imagens,
            self.modelo_selecionado,
            self.check_alpha_matting.isChecked(),
            self.slider_limiar_objeto.value(),
            self.slider_limiar_fundo.value(),
            self.slider_erosao.value(),
        )

        # Conectar sinais
        self.thread_lote.progresso.connect(self.atualizar_progresso_lote)
        self.thread_lote.concluido.connect(self.finalizar_processamento_lote)

        # Iniciar o thread
        self.thread_lote.start()

    def atualizar_progresso_lote(self, valor_progresso, texto_status):
        """Atualiza a barra de progresso e o status durante processamento em lote"""
        self.barra_progresso.setValue(int(valor_progresso * 100))
        self.rotulo_status.setText(texto_status)

    def finalizar_processamento_lote(self, resultado):
        """Finaliza o processamento em lote e atualiza a interface"""
        self.processamento_ativo = False
        self.definir_interface_processando(False)
        self.barra_progresso.setVisible(False)

        processados, total, erros, nome_modelo = resultado

        mensagem_final = f'Processamento em lote ({nome_modelo}) concluído.\n'
        mensagem_final += (
            f'{processados}/{total} imagem(ns) processada(s) com sucesso!'
        )

        texto_status = f'Lote ({nome_modelo}) finalizado: {processados} sucesso(s), {len(erros)} erro(s).'

        if erros:
            mensagem_final += f'\n\nOcorreram {len(erros)} erro(s):\n'
            mensagem_final += '\n'.join(f'- {err}' for err in erros[:5])

            if len(erros) > 5:
                mensagem_final += (
                    '\n- ... (veja o console/log para mais detalhes)'
                )

            QMessageBox.warning(
                self, 'Lote Concluído com Erros', mensagem_final
            )
        else:
            QMessageBox.information(self, 'Lote Concluído', mensagem_final)

        self.rotulo_status.setText(texto_status)

    def mostrar_imagem_completa(self, tipo_imagem):
        """Abre uma janela para exibir a imagem em tamanho completo"""
        if self.processamento_ativo:
            return

        imagem_para_mostrar = None
        titulo = ''

        if tipo_imagem == 'original' and self.imagem_entrada_completa:
            imagem_para_mostrar = self.imagem_entrada_completa
            titulo = f"Original - {os.path.basename(self.caminho_arquivo_atual or '')}"
        elif tipo_imagem == 'resultado' and self.imagem_resultado_completa:
            imagem_para_mostrar = self.imagem_resultado_completa
            titulo = f"Resultado ({self.modelo_selecionado}) - {os.path.basename(self.caminho_arquivo_atual or '')}"
        else:
            return

        try:
            # Criar a janela visualizadora
            visualizador = VisualizadorImagem(
                self, imagem_para_mostrar, titulo
            )
            visualizador.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro de Visualização',
                f'Não foi possível exibir a imagem em tamanho real:\n{e}',
            )

    def recortar_imagens_em_massa(self):
        """Permite recortar várias imagens com base em uma área de recorte definida em uma imagem modelo"""
        # Selecionar pasta de origem
        pasta_origem = QFileDialog.getExistingDirectory(
            self, 'Selecione a Pasta com Imagens'
        )
        if not pasta_origem:
            return

        # Selecionar imagem modelo
        tipos_arquivo = f"Arquivos de Imagem ({' '.join(['*' + ext for ext in EXTENSOES_SUPORTADAS])})"
        modelo_caminho, _ = QFileDialog.getOpenFileName(
            self, 'Selecione a Imagem Modelo', '', tipos_arquivo
        )

        if not modelo_caminho:
            return

        try:
            imagem_modelo = carregar_imagem(modelo_caminho)

            # Criar pasta de destino
            pasta_destino = os.path.join(pasta_origem, 'recorte_output')
            os.makedirs(pasta_destino, exist_ok=True)

            # Função de callback que recebe tanto a imagem quanto a caixa de recorte
            def callback_recorte(imagem_recortada, caixa_recorte):
                if caixa_recorte:
                    self.iniciar_recorte_em_massa(
                        pasta_origem, pasta_destino, caixa_recorte
                    )

            # Abre a janela de recorte
            janela_recorte = JanelaRecorte(
                self, imagem_modelo, callback_recorte
            )
            janela_recorte.exec()

        except Exception as e:
            QMessageBox.critical(
                self, 'Erro', f'Falha ao abrir a imagem modelo:\n{e}'
            )

    def iniciar_recorte_em_massa(
        self, pasta_origem, pasta_destino, caixa_recorte
    ):
        """Inicia o processamento de recorte em massa"""
        imagens = [
            f
            for f in os.listdir(pasta_origem)
            if os.path.isfile(os.path.join(pasta_origem, f))
            and f.lower().endswith(tuple(EXTENSOES_SUPORTADAS))
        ]

        total_arquivos = len(imagens)

        if total_arquivos == 0:
            QMessageBox.information(
                self,
                'Informação',
                'Nenhuma imagem compatível encontrada na pasta.',
            )
            return

        # Preparar interface para processamento
        self.processamento_ativo = True
        self.definir_interface_processando(True)
        self.barra_progresso.setVisible(True)
        self.barra_progresso.setValue(0)
        self.rotulo_status.setText(
            f'Iniciando recorte em massa: {total_arquivos} imagens...'
        )

        # Criar thread para processamento
        self.thread_recorte = RecorteMassaThread(
            self, pasta_origem, pasta_destino, imagens, caixa_recorte
        )

        # Conectar sinais
        self.thread_recorte.progresso.connect(self.atualizar_progresso_lote)
        self.thread_recorte.concluido.connect(self.finalizar_recorte_em_massa)

        # Iniciar o thread
        self.thread_recorte.start()

    def finalizar_recorte_em_massa(self, resultado):
        """Finaliza o recorte em massa e exibe o resultado"""
        self.processamento_ativo = False
        self.definir_interface_processando(False)
        self.barra_progresso.setVisible(False)

        processados, total, erros = resultado

        mensagem_final = f'Recorte em massa concluído.\n{processados}/{total} imagem(ns) processada(s) com sucesso.'

        if erros:
            mensagem_final += (
                f'\n\nOcorreram {len(erros)} erro(s):\n' + '\n'.join(erros[:5])
            )

            if len(erros) > 5:
                mensagem_final += '\n... (veja o console para mais detalhes)'

            QMessageBox.warning(self, 'Concluído', mensagem_final)
        else:
            QMessageBox.information(self, 'Concluído', mensagem_final)

        self.rotulo_status.setText('Recorte em massa concluído.')


class ProcessadorLoteThread(QThread):
    """Thread para processar imagens em lote"""

    progresso = pyqtSignal(float, str)
    concluido = pyqtSignal(tuple)

    def __init__(
        self,
        parent,
        pasta_origem,
        pasta_destino,
        arquivos,
        modelo,
        alpha_matting,
        limiar_objeto,
        limiar_fundo,
        erosao,
    ):
        super().__init__(parent)
        self.pasta_origem = pasta_origem
        self.pasta_destino = pasta_destino
        self.arquivos = arquivos
        self.modelo = modelo
        self.alpha_matting = alpha_matting
        self.limiar_objeto = limiar_objeto
        self.limiar_fundo = limiar_fundo
        self.erosao = erosao
        self.parent = parent

    def run(self):
        removedor = RemoveFundo(self.modelo)
        processados = 0
        erros = []
        total = len(self.arquivos)

        for i, nome_arquivo in enumerate(self.arquivos):
            caminho_entrada = os.path.join(self.pasta_origem, nome_arquivo)
            nome_saida = f'{os.path.splitext(nome_arquivo)[0]}_{self.modelo}_sem_fundo.png'
            caminho_saida = os.path.join(self.pasta_destino, nome_saida)

            # Atualizar progresso
            progresso = (i + 1) / total
            status_texto = (
                f'Lote ({self.modelo}) {i+1}/{total}: {nome_arquivo}'
            )
            self.progresso.emit(progresso, status_texto)

            try:
                # Carregar imagem e processar
                imagem = carregar_imagem(caminho_entrada)
                imagem_resultado = removedor.processar_imagem(
                    imagem,
                    self.alpha_matting,
                    self.limiar_objeto,
                    self.limiar_fundo,
                    self.erosao,
                )

                # Salvar resultado
                imagem_resultado.save(caminho_saida)
                processados += 1

            except Exception as e:
                erro_msg = f"'{nome_arquivo}': {e}"
                erros.append(erro_msg)
                print(f'Erro ao processar {nome_arquivo}: {e}')

        # Emitir resultado final
        self.concluido.emit((processados, total, erros, self.modelo))


class RecorteMassaThread(QThread):
    """Thread para recortar imagens em massa"""

    progresso = pyqtSignal(float, str)
    concluido = pyqtSignal(tuple)

    def __init__(
        self, parent, pasta_origem, pasta_destino, arquivos, caixa_recorte
    ):
        super().__init__(parent)
        self.pasta_origem = pasta_origem
        self.pasta_destino = pasta_destino
        self.arquivos = arquivos
        self.caixa_recorte = caixa_recorte
        self.parent = parent

    def run(self):
        processados = 0
        erros = []
        total = len(self.arquivos)

        for i, nome_arquivo in enumerate(self.arquivos):
            try:
                caminho_entrada = os.path.join(self.pasta_origem, nome_arquivo)
                nome_base, extensao = os.path.splitext(nome_arquivo)
                caminho_saida = os.path.join(
                    self.pasta_destino, f'{nome_base}-recortado.png'
                )

                # Atualizar progresso
                progresso = (i + 1) / total
                texto_status = (
                    f'Recorte em massa {i+1}/{total}: {nome_arquivo}'
                )
                self.progresso.emit(progresso, texto_status)

                # Carregar e recortar a imagem
                imagem = carregar_imagem(caminho_entrada)
                imagem_recortada = EditorImagem.recortar_imagem(
                    imagem, self.caixa_recorte
                )

                # Salvar o resultado
                imagem_recortada.save(caminho_saida)
                processados += 1

            except Exception as e:
                erro_msg = f'{nome_arquivo}: {str(e)}'
                erros.append(erro_msg)




        self.concluido.emit((processados, total, erros))        # Emitir resultado final                print(f'Erro ao processar {nome_arquivo}: {e}')        self.concluido.emit((processados, total, erros))
