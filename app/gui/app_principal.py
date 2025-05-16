from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon

from app.configuracoes import (ALPHA_MATTING_PADRAO, EROSAO_MASCARA_PADRAO,
                              LIMIAR_FUNDO_PADRAO, LIMIAR_OBJETO_PADRAO,
                              MODELO_PADRAO, TITULO_APP, VERSAO)
from app.utils.estilos import configurar_paleta, obter_estilo_global
from app.processadores.removedor_fundo import RemoveFundo

# Importação dos módulos refatorados
from app.gui.interface_construtor import InterfaceConstrutor
from app.gui.operacoes_imagem import OperacoesImagem
from app.gui.operacoes_arquivo import OperacoesArquivo

class AplicativoRemoveFundo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(TITULO_APP)
        self.resize(1250, 850)
        self.setWindowIconText('Remover Fundo')
        self.setWindowIcon(QIcon('app/assets/icon.png'))

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
        InterfaceConstrutor.criar_cabecalho(self)
        InterfaceConstrutor.criar_menu(self)
        InterfaceConstrutor.criar_frame_principal(self)
        InterfaceConstrutor.criar_barra_status(self)

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

    def atualizar_estados_menu(self):
        """Atualiza os estados dos itens do menu com base no estado atual da aplicação"""
        tem_resultado = self.imagem_resultado_completa is not None
        tem_imagem = self.imagem_entrada_completa is not None

        self.acao_salvar.setEnabled(tem_resultado)
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

    # Métodos delegados para módulos
    def selecionar_imagem(self):
        OperacoesArquivo.selecionar_imagem(self)

    def aplicar_recorte(self, imagem_recortada, caixa_recorte=None):
        """Callback chamado quando o recorte é concluído"""
        # Em vez de modificar a imagem original, definimos o resultado
        self.imagem_resultado_completa = imagem_recortada
        OperacoesImagem.exibir_imagem_no_label(
            self, self.label_imagem_resultado, self.imagem_resultado_completa
        )
        self.atualizar_estados_menu()

        self.rotulo_status.setText('Imagem recortada com sucesso.')

    def aplicar_borracha(self, imagem_editada):
        """Callback chamado quando a edição com borracha é concluída"""
        # Em vez de modificar a imagem original, definimos o resultado
        self.imagem_resultado_completa = imagem_editada
        OperacoesImagem.exibir_imagem_no_label(
            self, self.label_imagem_resultado, self.imagem_resultado_completa
        )
        self.atualizar_estados_menu()

        self.rotulo_status.setText('Imagem editada com sucesso.')

    def abrir_ferramenta_recorte(self):
        OperacoesImagem.abrir_ferramenta_recorte(self)

    def abrir_ferramenta_borracha(self):
        OperacoesImagem.abrir_ferramenta_borracha(self)

    def processar_imagem(self):
        OperacoesImagem.processar_imagem(self)

    def finalizar_processamento(self, imagem_resultado):
        """Chamado quando o processamento é concluído com sucesso"""
        self.imagem_resultado_completa = imagem_resultado
        OperacoesImagem.exibir_imagem_no_label(
            self, self.label_imagem_resultado, self.imagem_resultado_completa
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
        OperacoesArquivo.salvar_imagem(self)

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
        OperacoesArquivo.processar_pasta(self)

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
        OperacoesImagem.mostrar_imagem_completa(self, tipo_imagem)

    def recortar_imagens_em_massa(self):
        OperacoesArquivo.recortar_imagens_em_massa(self)

    def iniciar_recorte_em_massa(self, pasta_origem, pasta_destino, caixa_recorte):
        OperacoesArquivo.iniciar_recorte_em_massa(self, pasta_origem, pasta_destino, caixa_recorte)

    def finalizar_recorte_em_massa(self, resultado):
        """Finaliza o recorte em massa e exibe o resultado"""
        self.processamento_ativo = False
        self.definir_interface_processando(False)
        self.barra_progresso.setVisible(False)

        processados, total, erros = resultado

        mensagem_final = f'Recorte em massa concluído.\n{processados}/{total} imagem(ns) processada(s) com sucesso.'

        if erros:
            mensagem_final += (
                f'\n\nOcorreram {len(erros)} erro(s):\n'
            )
            mensagem_final += '\n'.join(f'- {err}' for err in erros[:5])

            if len(erros) > 5:
                mensagem_final += '\n- ... (veja o console para mais detalhes)'

            QMessageBox.warning(self, 'Concluído', mensagem_final)
        else:
            QMessageBox.information(self, 'Concluído', mensagem_final)

        self.rotulo_status.setText('Recorte em massa concluído.')
