from PIL import Image, ImageDraw, ImageOps
import os
from app.configuracoes import EXTENSOES_SUPORTADAS

class EditorImagem:
    """Classe para manipular e editar imagens"""
    
    @staticmethod
    def recortar_imagem(imagem, caixa_recorte):
        """Recorta a imagem de acordo com as coordenadas fornecidas"""
        if not imagem:
            return None
            
        x1, y1, x2, y2 = caixa_recorte
        
        # Garantir que x1 < x2 e y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
            
        # Verificar se a área selecionada é válida
        if x2 - x1 <= 0 or y2 - y1 <= 0:
            return imagem
            
        return imagem.crop((x1, y1, x2, y2))
    
    @staticmethod
    def aplicar_borracha(imagem, posicoes, tamanho_borracha):
        """Apaga áreas da imagem usando uma borracha circular"""
        if not imagem:
            return None
            
        imagem_copia = imagem.copy()
        desenho = ImageDraw.Draw(imagem_copia)
        
        for x, y in posicoes:
            desenho.ellipse(
                (x - tamanho_borracha, y - tamanho_borracha, 
                 x + tamanho_borracha, y + tamanho_borracha), 
                fill=(0, 0, 0, 0)
            )
            
        return imagem_copia
    
    @staticmethod
    def recortar_em_massa(pasta_origem, pasta_destino, caixa_recorte):
        """Aplica o mesmo recorte a várias imagens em uma pasta"""
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
            
        arquivos_processados = 0
        erros = []
        
        try:
            todos_arquivos = os.listdir(pasta_origem)
            imagens = [f for f in todos_arquivos
                     if os.path.isfile(os.path.join(pasta_origem, f)) 
                     and f.lower().endswith(EXTENSOES_SUPORTADAS)]
                        
            for nome_arquivo in imagens:
                caminho_entrada = os.path.join(pasta_origem, nome_arquivo)
                nome_base, extensao = os.path.splitext(nome_arquivo)
                caminho_saida = os.path.join(pasta_destino, f"{nome_base}-recortado.png")
                
                try:
                    imagem = Image.open(caminho_entrada)
                    imagem = ImageOps.exif_transpose(imagem)
                    if imagem.mode != "RGBA":
                        imagem = imagem.convert("RGBA")
                        
                    imagem_recortada = EditorImagem.recortar_imagem(imagem, caixa_recorte)
                    imagem_recortada.save(caminho_saida)
                    arquivos_processados += 1
                    
                except Exception as e:
                    erros.append(f"{nome_arquivo}: {str(e)}")
                    
        except Exception as e:
            erros.append(f"Erro ao listar arquivos: {str(e)}")
            
        return arquivos_processados, len(imagens), erros
