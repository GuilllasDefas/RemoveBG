# Arquivo de configurações globais

# Versão do aplicativo
VERSAO = "0.9.0"
TITULO_APP = f"Remover Fundo v{VERSAO} - Beta"

# Modelos disponíveis no rembg
MODELOS_DISPONIVEIS = [
    "u2net", 
    "u2netp", 
    "u2net_human_seg", 
    "silueta", 
    "isnet-general-use", 
    "isnet-anime"
]

# Modelo padrão
MODELO_PADRAO = "isnet-general-use"

# Configurações padrão
ALPHA_MATTING_PADRAO = True
LIMIAR_OBJETO_PADRAO = 250
LIMIAR_FUNDO_PADRAO = 10
EROSAO_MASCARA_PADRAO = 5

# Extensões de imagem suportadas
EXTENSOES_SUPORTADAS = ('.png', '.jpg', '.jpeg', '.webp')
