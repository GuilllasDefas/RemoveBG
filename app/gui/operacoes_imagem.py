import os

from PIL import ImageQt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox

from app.gui.visualizador import VisualizadorImagem
from app.gui.janela_recorte import JanelaRecorte
from app.gui.janela_borracha import JanelaBorracha
from app.utils.imagem_utils import criar_preview
from app.gui.threads import ProcessadorThread


class OperacoesImagem:
    """Classe responsável por operações relacionadas ao processamento de imagens"""
    
    @staticmethod
    def exibir_imagem_no_label(app, label, imagem_pil):
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
    
    @staticmethod
    def processar_imagem(app):
        """Processa a imagem para remover o fundo"""
        if not app.imagem_entrada_completa:
            QMessageBox.warning(
                app, 'Atenção', 'Selecione uma imagem primeiro!'
            )
            return

        if app.processamento_ativo:
            QMessageBox.warning(
                app, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        # Obter valores de configuração
        usar_alpha_matting = app.check_alpha_matting.isChecked()
        limiar_objeto = app.slider_limiar_objeto.value()
        limiar_fundo = app.slider_limiar_fundo.value()
        tamanho_erosao = app.slider_erosao.value()

        # Iniciar thread de processamento
        app.processamento_ativo = True
        app.definir_interface_processando(True)
        app.rotulo_status.setText(
            f"Processando com modelo '{app.modelo_selecionado}'..."
        )

        # Criar thread de processamento
        app.thread_processamento = ProcessadorThread(
            app.removedor.processar_imagem,
            app.imagem_entrada_completa,
            usar_alpha_matting,
            limiar_objeto,
            limiar_fundo,
            tamanho_erosao,
        )

        # Conectar sinais
        app.thread_processamento.concluido.connect(
            app.finalizar_processamento
        )
        app.thread_processamento.erro.connect(app.erro_processamento)

        # Iniciar thread
        app.thread_processamento.start()
    
    @staticmethod
    def mostrar_imagem_completa(app, tipo_imagem):
        """Abre uma janela para exibir a imagem em tamanho completo"""
        if app.processamento_ativo:
            return

        imagem_para_mostrar = None
        titulo = ''

        if tipo_imagem == 'original' and app.imagem_entrada_completa:
            imagem_para_mostrar = app.imagem_entrada_completa
            titulo = f"Original - {os.path.basename(app.caminho_arquivo_atual or '')}"
        elif tipo_imagem == 'resultado' and app.imagem_resultado_completa:
            imagem_para_mostrar = app.imagem_resultado_completa
            titulo = f"Resultado ({app.modelo_selecionado}) - {os.path.basename(app.caminho_arquivo_atual or '')}"
        else:
            return

        try:
            # Criar a janela visualizadora
            visualizador = VisualizadorImagem(
                app, imagem_para_mostrar, titulo
            )
            visualizador.exec()
        except Exception as e:
            QMessageBox.critical(
                app,
                'Erro de Visualização',
                f'Não foi possível exibir a imagem em tamanho real:\n{e}',
            )
    
    @staticmethod
    def abrir_ferramenta_recorte(app):
        """Abre a janela para recortar a imagem"""
        if not app.imagem_entrada_completa:
            QMessageBox.warning(
                app, 'Atenção', 'Nenhuma imagem carregada para recorte!'
            )
            return

        # Se já tiver uma imagem resultado, use-a como base para recorte
        imagem_base = (
            app.imagem_resultado_completa
            if app.imagem_resultado_completa
            else app.imagem_entrada_completa
        )

        janela_recorte = JanelaRecorte(app, imagem_base, app.aplicar_recorte)
        janela_recorte.exec()
    
    @staticmethod
    def abrir_ferramenta_borracha(app):
        """Abre a janela para apagar áreas da imagem com uma borracha"""
        if not app.imagem_entrada_completa:
            QMessageBox.warning(
                app, 'Atenção', 'Nenhuma imagem carregada para edição!'
            )
            return

        # Se já tiver uma imagem resultado, use-a como base para edição
        imagem_base = (
            app.imagem_resultado_completa
            if app.imagem_resultado_completa
            else app.imagem_entrada_completa
        )

        janela_borracha = JanelaBorracha(
            app, imagem_base, app.aplicar_borracha
        )
        janela_borracha.exec()
