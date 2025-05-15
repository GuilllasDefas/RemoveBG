from PIL import Image, ImageOps

def criar_preview(imagem, largura_max, altura_max):
    """Cria uma versão redimensionada da imagem para preview"""
    if not imagem:
        return None
        
    img_larg, img_alt = imagem.size
    if img_larg == 0 or img_alt == 0 or largura_max <= 0 or altura_max <= 0:
        return Image.new('RGBA', (1, 1), (0, 0, 0, 0))

    proporcao = min(largura_max / img_larg, altura_max / img_alt)
    if proporcao < 1.0:
        novo_tamanho = (max(1, int(img_larg * proporcao)), max(1, int(img_alt * proporcao)))
        try:
            return imagem.resize(novo_tamanho, Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Erro ao redimensionar preview: {e}")
            return imagem
    return imagem

def carregar_imagem(caminho_arquivo):
    """Carrega uma imagem de um arquivo e a prepara para processamento"""
    imagem = Image.open(caminho_arquivo)
    imagem = ImageOps.exif_transpose(imagem)
    if imagem.mode != "RGBA":
        imagem = imagem.convert("RGBA")
    return imagem
