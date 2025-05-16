"""
Módulo para centralizar todos os estilos da aplicação RemoveBG
Tema escuro baseado no esquema de cores do ícone.
"""

# Cores principais - Tema Escuro baseado no ícone
CORES = {
    'principal': '#1B2C35',      # Azul muito escuro (quase preto) para fundos principais
    'secundaria': '#2B3F4B',     # Azul escuro secundário para painéis
    'destaque': '#48A3C6',       # Azul médio para destaque (sliders, seleções)
    'destaque_hover': '#62C0E3',  # Azul mais claro para hover
    'fundo': '#24323E',          # Fundo escuro para a aplicação
    'texto': '#E0E0E0',          # Texto claro para boa legibilidade em fundo escuro
    'texto_secundario': '#B0B0B0', # Texto secundário menos contrastante
    'borda': '#3A4956',          # Bordas mais escuras
    'desabilitado': '#4A5A68',   # Elementos desabilitados
    'sucesso': '#2E8B57',        # Verde escuro para sucessos
    'alerta': '#D68000',         # Laranja mais escuro para alertas
    'erro': '#A83232',           # Vermelho escuro para erros
    'botao': '#3A5269',          # Cor dos botões - azul médio
    'botao_hover': '#48A3C6',    # Cor quando mouse passa sobre botão - azul mais claro
    'botao_texto': '#FFFFFF',    # Texto dos botões - branco para contraste
    'menu_bg': '#1D2D38',        # Fundo do menu
    'menu_item': '#48A3C6',      # Item de menu selecionado
}

# Fontes - reduzidas para tamanhos mais adequados
FONTES = {
    'familia_padrao': 'Segoe UI, Helvetica, Arial, sans-serif',
    'titulo_app': "18pt 'Segoe UI'",       # Reduzido de 24pt
    'titulo_secao': "10pt 'Segoe UI'",     # Reduzido de 12pt
    'rotulos': "9pt 'Segoe UI'",           # Reduzido de 10pt
    'botoes': "bold 9pt 'Segoe UI'",       # Reduzido de 10pt
}

# Estilos para componentes específicos
ESTILOS_COMPONENTES = {
    'frame_ajustes': f"""
        background-color: {CORES['secundaria']};
        border: 1px solid {CORES['borda']};
        border-radius: 5px;
        padding: 10px;
    """,
    
    'cabecalho_titulo': f"""
        color: {CORES['texto']};
        padding: 12px;
        font: {FONTES['titulo_app']};
        font-weight: bold;
    """,
    
    'titulo_secao': f"""
        color: {CORES['texto']};
        margin-bottom: 8px;
        font: {FONTES['titulo_secao']};
        font-weight: bold;
    """,
    
    'titulo_painel_ajustes': f"""
        color: {CORES['texto']};
        padding-bottom: 12px;
        margin-bottom: 15px;
        border-bottom: 2px solid {CORES['borda']};
        font-weight: bold;
    """,
    
    'label_scroll_area': f"""
        background-color: {CORES['secundaria']};
        color: {CORES['texto']};
    """,
    
    'scroll_area': f"""
        background-color: {CORES['secundaria']};
        border: 1px solid {CORES['borda']};
        border-radius: 5px;
    """,
    
    'botao_padrao': f"""
        background-color: {CORES['botao']};
        color: {CORES['botao_texto']};
        border-radius: 3px;
        padding: 4px 10px;  /* Reduzido de 8px 16px */
        font-weight: bold;
        border: none;
    """,
    
    'botao_restaurar': f"""
        background-color: {CORES['botao']};
        color: {CORES['botao_texto']};
        padding: 5px 10px;  /* Reduzido de 10px */
        border-radius: 3px;
        font-weight: bold;
        margin-top: 10px;
    """,
    
    # Novo estilo para botão de destaque principal
    'botao_destaque': f"""
        background-color: {CORES['destaque']};
        color: white;
        border-radius: 3px;
        padding: 5px 12px;
        font-size: 11pt;
        font-weight: bold;
        border: none;
    """,
    
    # Novo estilo para menus dropdown (combobox)
    'combobox': f"""
        background-color: {CORES['secundaria']};
        color: {CORES['texto']};
        border: 1px solid {CORES['borda']};
        padding: 5px;
        border-radius: 4px;
        selection-background-color: {CORES['destaque']};
        selection-color: {CORES['botao_texto']};
    """
}

# Estilo global da aplicação
def obter_estilo_global():
    """Retorna o estilo CSS global da aplicação - tema escuro"""
    return f"""
        QMainWindow, QDialog {{
            background-color: {CORES['principal']};
            color: {CORES['texto']};
        }}
        
        QPushButton {{
            background-color: {CORES['botao']};
            color: {CORES['botao_texto']};
            border-radius: 3px;
            padding: 4px 10px;  /* Reduzido */
            font-weight: bold;
            border: none;
            min-height: 20px;   /* Reduzido de 24px */
        }}
        
        QPushButton:hover {{
            background-color: {CORES['botao_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: #2D4155;
        }}
        
        QPushButton:disabled {{
            background-color: {CORES['desabilitado']};
            color: {CORES['texto_secundario']};
        }}
        
        QLabel {{
            color: {CORES['texto']};
            font: {FONTES['rotulos']};
        }}
        
        QComboBox, QCheckBox, QSlider {{
            color: {CORES['texto']};
            font: {FONTES['rotulos']};
        }}
        
        QComboBox {{
            background-color: {CORES['secundaria']};
            border: 1px solid {CORES['borda']};
            border-radius: 3px;
            padding: 3px 6px;  /* Reduzido */
            color: {CORES['texto']};
            selection-background-color: {CORES['destaque']};
            selection-color: white;
            min-height: 20px;  /* Reduzido de 24px */
        }}
        
        QComboBox:hover {{
            border: 1px solid {CORES['destaque']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {CORES['secundaria']};
            color: {CORES['texto']};
            selection-background-color: {CORES['destaque']};
            selection-color: white;
            border: 1px solid {CORES['borda']};
        }}
        
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            background-color: {CORES['secundaria']};
            border: 1px solid {CORES['borda']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {CORES['destaque']};
            border: 1px solid {CORES['destaque']};
        }}
        
        QStatusBar {{
            background-color: {CORES['principal']};
            color: {CORES['texto']};
            font-weight: bold;
            min-height: 28px;
        }}
        
        QProgressBar {{
            border: 1px solid {CORES['borda']};
            border-radius: 5px;
            text-align: center;
            background-color: {CORES['secundaria']};
            color: {CORES['texto']};
            font-weight: bold;
        }}
        
        QProgressBar::chunk {{
            background-color: {CORES['destaque']};
            width: 10px;
        }}
        
        QScrollArea {{
            background-color: {CORES['secundaria']};
            border: 1px solid {CORES['borda']};
            border-radius: 4px;
        }}
        
        QScrollBar {{
            background-color: {CORES['secundaria']};
            width: 12px;
            height: 12px;
        }}
        
        QScrollBar::handle {{
            background-color: {CORES['botao']};
            border-radius: 4px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:hover {{
            background-color: {CORES['botao_hover']};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
            border: none;
        }}
        
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}
        
        QFrame#FrameDivisor {{
            background-color: {CORES['borda']};
        }}
        
        QSlider::groove:horizontal {{
            border: 1px solid {CORES['borda']};
            height: 10px;
            background: {CORES['secundaria']};
            margin: 2px 0;
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {CORES['destaque']};
            border: 1px solid {CORES['destaque']};
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {CORES['destaque_hover']};
        }}
        
        /* Estilizar o menu para melhor visibilidade */
        QMenuBar {{
            background-color: {CORES['menu_bg']};
            color: {CORES['texto']};
            padding: 3px;
            font-weight: bold;
            border-bottom: 1px solid {CORES['borda']};
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 5px 10px;
        }}
        
        QMenuBar::item:selected {{
            background: {CORES['destaque']};
            color: white;
            border-radius: 4px;
        }}
        
        QMenu {{
            background-color: {CORES['menu_bg']};
            color: {CORES['texto']};
            border: 1px solid {CORES['borda']};
            padding: 5px;
        }}
        
        QMenu::item {{
            padding: 6px 25px 6px 20px;
            border-radius: 3px;
            margin: 2px;
        }}
        
        QMenu::item:selected {{
            background-color: {CORES['menu_item']};
            color: white;
        }}
        
        /* Estilo para o widget central */
        QWidget#centralWidget {{
            background-color: {CORES['principal']};
        }}
    """


# Função de ajuda para definir a paleta de cores da aplicação
def configurar_paleta(app):
    """Configura a paleta de cores escuras para a aplicação"""
    from PyQt6.QtGui import QColor, QPalette

    paleta = QPalette()
    paleta.setColor(QPalette.ColorRole.Window, QColor(CORES['principal']))
    paleta.setColor(QPalette.ColorRole.WindowText, QColor(CORES['texto']))
    paleta.setColor(QPalette.ColorRole.Base, QColor(CORES['secundaria']))
    paleta.setColor(QPalette.ColorRole.AlternateBase, QColor(CORES['principal']))
    paleta.setColor(QPalette.ColorRole.Button, QColor(CORES['botao']))
    paleta.setColor(QPalette.ColorRole.ButtonText, QColor(CORES['botao_texto']))
    paleta.setColor(QPalette.ColorRole.Highlight, QColor(CORES['destaque']))
    paleta.setColor(QPalette.ColorRole.HighlightedText, QColor(CORES['botao_texto']))

    return paleta


# Estilos para janelas específicas
def estilo_visualizador():
    """Retorna o estilo para a janela visualizador"""
    return f"""
        QDialog {{
            background-color: {CORES['principal']};
        }}
        QPushButton {{
            background-color: {CORES['botao']};
            color: {CORES['botao_texto']};
            border-radius: 3px;
            padding: 4px 10px;  /* Reduzido */
            font-weight: bold;
            border: none;
            min-height: 20px;  /* Reduzido */
        }}
        QPushButton:hover {{
            background-color: {CORES['botao_hover']};
        }}
        QPushButton:pressed {{
            background-color: #2D4155;
        }}
        QLabel {{
            color: {CORES['texto']};
            font: {FONTES['rotulos']};
        }}
        QScrollArea {{
            border: 1px solid {CORES['borda']};
            border-radius: 4px;
            background-color: {CORES['secundaria']};
        }}
    """


def estilo_janela_ferramentas():
    """Retorna o estilo para as janelas de ferramentas (recorte e borracha)"""
    return f"""
        QDialog {{
            background-color: {CORES['principal']};
        }}
        QPushButton {{
            background-color: {CORES['botao']};
            color: {CORES['botao_texto']};
            border-radius: 3px;
            padding: 4px 10px;  /* Reduzido */
            font-weight: bold;
            border: none;
            min-height: 20px;  /* Reduzido */
        }}
        QPushButton:hover {{
            background-color: {CORES['botao_hover']};
        }}
        QPushButton:pressed {{
            background-color: #2D4155;
        }}
        QLabel {{
            color: {CORES['texto']};
            font: {FONTES['rotulos']};
        }}
        QScrollArea {{
            border: 1px solid {CORES['borda']};
            border-radius: 4px;
            background-color: {CORES['secundaria']};
        }}
        QSlider::groove:horizontal {{
            border: 1px solid {CORES['borda']};
            height: 10px;
            background: {CORES['secundaria']};
            margin: 2px 0;
            border-radius: 4px;
        }}
        QSlider::handle:horizontal {{
            background: {CORES['destaque']};
            border: 1px solid {CORES['destaque']};
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {CORES['destaque_hover']};
        }}
    """
