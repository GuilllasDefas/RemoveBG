import os
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal

from app.utils.imagem_utils import carregar_imagem
from app.processadores.editor_imagem import EditorImagem


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
        removedor = self.parent.removedor
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
                nome_base, ext = os.path.splitext(nome_arquivo)
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

        self.concluido.emit((processados, total, erros))
