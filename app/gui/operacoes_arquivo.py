import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from app.configuracoes import EXTENSOES_SUPORTADAS
from app.utils.imagem_utils import carregar_imagem
from app.gui.threads import ProcessadorLoteThread, RecorteMassaThread


class OperacoesArquivo:
    """Classe responsável por operações relacionadas a arquivos"""
    
    @staticmethod
    def selecionar_imagem(app):
        """Abre o diálogo para selecionar uma imagem"""
        if app.processamento_ativo:
            QMessageBox.warning(
                app, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        tipos_arquivo = f"Arquivos de Imagem ({' '.join(['*' + ext for ext in EXTENSOES_SUPORTADAS])})"
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            app, 'Selecione a Imagem', '', tipos_arquivo
        )

        if caminho_arquivo:
            try:
                app.rotulo_status.setText('Carregando imagem...')

                imagem = carregar_imagem(caminho_arquivo)
                app.imagem_entrada_completa = imagem
                app.caminho_arquivo_atual = caminho_arquivo
                app.imagem_resultado_completa = None

                from app.gui.operacoes_imagem import OperacoesImagem
                OperacoesImagem.exibir_imagem_no_label(
                    app, app.label_imagem_original, app.imagem_entrada_completa
                )
                app.label_imagem_resultado.clear()

                app.botao_ver_original.setEnabled(True)
                app.botao_ver_resultado.setEnabled(False)
                app.rotulo_status.setText(
                    f'Imagem carregada: {os.path.basename(caminho_arquivo)}'
                )
                app.atualizar_estados_menu()

            except Exception as e:
                QMessageBox.critical(
                    app, 'Erro', f'Falha ao abrir a imagem:\n{e}'
                )
                app.rotulo_status.setText('Erro ao carregar imagem!')
                app.resetar_estado_interface()

    @staticmethod
    def salvar_imagem(app):
        """Salva a imagem resultante (processada ou editada)"""
        if not app.imagem_resultado_completa:
            QMessageBox.warning(
                app,
                'Atenção',
                'Não há imagem processada ou editada para salvar!',
            )
            return

        if app.processamento_ativo:
            QMessageBox.warning(
                app, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        nome_arquivo_original = os.path.basename(
            app.caminho_arquivo_atual or 'imagem'
        )
        nome, _ = os.path.splitext(nome_arquivo_original)
        nome_padrao = f'{nome}_editado.png'

        caminho_arquivo, _ = QFileDialog.getSaveFileName(
            app, 'Salvar Imagem', nome_padrao, 'Arquivos PNG (*.png)'
        )

        if caminho_arquivo:
            try:
                app.rotulo_status.setText('Salvando imagem...')
                app.imagem_resultado_completa.save(caminho_arquivo)
                app.rotulo_status.setText('Imagem salva com sucesso!')
            except Exception as e:
                QMessageBox.critical(
                    app, 'Erro', f'Falha ao salvar a imagem:\n{e}'
                )
                app.rotulo_status.setText('Erro ao salvar!')

    @staticmethod
    def processar_pasta(app):
        """Abre diálogos para processar todas as imagens em uma pasta"""
        if app.processamento_ativo:
            QMessageBox.warning(
                app, 'Atenção', 'Aguarde o processamento atual terminar.'
            )
            return

        pasta_origem = QFileDialog.getExistingDirectory(
            app, 'Selecione a Pasta com Imagens'
        )
        if not pasta_origem:
            return

        pasta_destino = QFileDialog.getExistingDirectory(
            app, 'Selecione a Pasta de Destino'
        )
        if not pasta_destino:
            return

        if pasta_origem == pasta_destino:
            QMessageBox.critical(
                app,
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
                app,
                'Informação',
                'Nenhuma imagem compatível encontrada na pasta selecionada.',
            )
            return

        total_arquivos = len(imagens)
        nome_modelo = app.modelo_selecionado

        # Preparar interface para processamento
        app.processamento_ativo = True
        app.definir_interface_processando(True)
        app.barra_progresso.setVisible(True)
        app.barra_progresso.setValue(0)
        app.rotulo_status.setText(
            f'Iniciando lote ({nome_modelo}): {total_arquivos} imagens...'
        )

        # Criar thread do processador de lotes
        app.thread_lote = ProcessadorLoteThread(
            app,
            pasta_origem,
            pasta_destino,
            imagens,
            app.modelo_selecionado,
            app.check_alpha_matting.isChecked(),
            app.slider_limiar_objeto.value(),
            app.slider_limiar_fundo.value(),
            app.slider_erosao.value(),
        )

        # Conectar sinais
        app.thread_lote.progresso.connect(app.atualizar_progresso_lote)
        app.thread_lote.concluido.connect(app.finalizar_processamento_lote)

        # Iniciar o thread
        app.thread_lote.start()

    @staticmethod
    def recortar_imagens_em_massa(app):
        """Permite recortar várias imagens com base em uma área de recorte definida em uma imagem modelo"""
        # Selecionar pasta de origem
        pasta_origem = QFileDialog.getExistingDirectory(
            app, 'Selecione a Pasta com Imagens'
        )
        if not pasta_origem:
            return

        # Selecionar imagem modelo
        tipos_arquivo = f"Arquivos de Imagem ({' '.join(['*' + ext for ext in EXTENSOES_SUPORTADAS])})"
        modelo_caminho, _ = QFileDialog.getOpenFileName(
            app, 'Selecione a Imagem Modelo', '', tipos_arquivo
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
                    app.iniciar_recorte_em_massa(
                        pasta_origem, pasta_destino, caixa_recorte
                    )

            # Abre a janela de recorte
            from app.gui.janela_recorte import JanelaRecorte
            janela_recorte = JanelaRecorte(
                app, imagem_modelo, callback_recorte
            )
            janela_recorte.exec()

        except Exception as e:
            QMessageBox.critical(
                app, 'Erro', f'Falha ao abrir a imagem modelo:\n{e}'
            )

    @staticmethod
    def iniciar_recorte_em_massa(app, pasta_origem, pasta_destino, caixa_recorte):
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
                app,
                'Informação',
                'Nenhuma imagem compatível encontrada na pasta.',
            )
            return

        # Preparar interface para processamento
        app.processamento_ativo = True
        app.definir_interface_processando(True)
        app.barra_progresso.setVisible(True)
        app.barra_progresso.setValue(0)
        app.rotulo_status.setText(
            f'Iniciando recorte em massa: {total_arquivos} imagens...'
        )

        # Criar thread para processamento
        app.thread_recorte = RecorteMassaThread(
            app, pasta_origem, pasta_destino, imagens, caixa_recorte
        )

        # Conectar sinais
        app.thread_recorte.progresso.connect(app.atualizar_progresso_lote)
        app.thread_recorte.concluido.connect(app.finalizar_recorte_em_massa)

        # Iniciar o thread
        app.thread_recorte.start()
