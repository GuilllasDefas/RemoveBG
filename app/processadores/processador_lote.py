import os

from app.configuracoes import EXTENSOES_SUPORTADAS
from app.utils.imagem_utils import carregar_imagem


class ProcessadorLote:
    def __init__(
        self,
        removedor_fundo,
        pasta_origem,
        pasta_destino,
        callback_progresso=None,
    ):
        self.removedor_fundo = removedor_fundo
        self.pasta_origem = pasta_origem
        self.pasta_destino = pasta_destino
        self.callback_progresso = callback_progresso
        self.arquivos_processados = 0
        self.arquivos_com_erro = []

    def listar_imagens(self):
        """Lista todos os arquivos de imagem na pasta de origem"""
        try:
            todos_arquivos = os.listdir(self.pasta_origem)
            imagens = [
                f
                for f in todos_arquivos
                if os.path.isfile(os.path.join(self.pasta_origem, f))
                and f.lower().endswith(EXTENSOES_SUPORTADAS)
            ]
            return imagens
        except Exception as e:
            print(f'Erro ao listar arquivos: {e}')
            return []

    def processar(
        self,
        usar_alpha_matting=True,
        limiar_objeto=250,
        limiar_fundo=10,
        tamanho_erosao=5,
    ):
        """Processa todas as imagens da pasta de origem"""
        imagens = self.listar_imagens()
        self.arquivos_processados = 0
        self.arquivos_com_erro = []
        total_arquivos = len(imagens)

        if total_arquivos == 0:
            return 0, 0, []

        for i, nome_arquivo in enumerate(imagens):
            caminho_entrada = os.path.join(self.pasta_origem, nome_arquivo)
            nome_base, _ = os.path.splitext(nome_arquivo)
            nome_saida = (
                f'{nome_base}_{self.removedor_fundo.nome_modelo}_sem_fundo.png'
            )
            caminho_saida = os.path.join(self.pasta_destino, nome_saida)

            # Atualiza o progresso
            if self.callback_progresso:
                progresso = (i + 1) / total_arquivos
                status = f'Lote ({self.removedor_fundo.nome_modelo}) {i+1}/{total_arquivos}: {nome_arquivo}'
                self.callback_progresso(progresso, status)

            try:
                # Carrega a imagem
                imagem = carregar_imagem(caminho_entrada)

                # Processa a remoção de fundo
                bytes_resultado = self.removedor_fundo.obter_bytes_processados(
                    imagem,
                    usar_alpha_matting,
                    limiar_objeto,
                    limiar_fundo,
                    tamanho_erosao,
                )

                # Salva o resultado
                with open(caminho_saida, 'wb') as f_out:
                    f_out.write(bytes_resultado)

                self.arquivos_processados += 1

            except Exception as e:
                erro_msg = f"'{nome_arquivo}': {e}"
                self.arquivos_com_erro.append(erro_msg)
                print(f'Erro ao processar {nome_arquivo}: {e}')

        return (
            self.arquivos_processados,
            total_arquivos,
            self.arquivos_com_erro,
        )
