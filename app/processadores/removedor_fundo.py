import io

from PIL import Image
from rembg import new_session, remove


class RemoveFundo:
    def __init__(self, nome_modelo='u2net'):
        self.nome_modelo = nome_modelo
        self.sessao = new_session(nome_modelo)

    def mudar_modelo(self, novo_modelo):
        """Muda para um novo modelo e atualiza a sessão"""
        if self.nome_modelo != novo_modelo:
            self.nome_modelo = novo_modelo
            self.sessao = new_session(novo_modelo)
            return True
        return False

    def processar_imagem(
        self,
        imagem,
        usar_alpha_matting=True,
        limiar_objeto=250,
        limiar_fundo=10,
        tamanho_erosao=5,
    ):
        """Remove o fundo de uma imagem usando as configurações especificadas"""
        # Converte a imagem PIL para bytes
        buffer = io.BytesIO()
        imagem.save(buffer, format='PNG')
        dados_imagem = buffer.getvalue()

        # Processa a remoção de fundo
        bytes_resultado = remove(
            dados_imagem,
            session=self.sessao,
            alpha_matting=usar_alpha_matting,
            alpha_matting_foreground_threshold=limiar_objeto,
            alpha_matting_background_threshold=limiar_fundo,
            alpha_matting_erode_size=tamanho_erosao,
        )

        # Converte o resultado de volta para imagem PIL
        imagem_resultado = Image.open(io.BytesIO(bytes_resultado)).convert(
            'RGBA'
        )
        return imagem_resultado

    def obter_bytes_processados(
        self,
        imagem,
        usar_alpha_matting=True,
        limiar_objeto=250,
        limiar_fundo=10,
        tamanho_erosao=5,
    ):
        """Processa a imagem e retorna os bytes resultantes (útil para salvar arquivo)"""
        buffer = io.BytesIO()
        imagem.save(buffer, format='PNG')
        dados_imagem = buffer.getvalue()

        bytes_resultado = remove(
            dados_imagem,
            session=self.sessao,
            alpha_matting=usar_alpha_matting,
            alpha_matting_foreground_threshold=limiar_objeto,
            alpha_matting_background_threshold=limiar_fundo,
            alpha_matting_erode_size=tamanho_erosao,
        )

        return bytes_resultado
