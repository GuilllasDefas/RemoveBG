RemoveBG\
├── main.py                    # Ponto de entrada da aplicação
├── .gitignore                 # Arquivo já criado
├── app/                       # Pasta principal da aplicação
│   ├── __init__.py
│   ├── configuracoes.py       # Configurações globais
│   ├── gui/                   # Componentes de interface
│   │   ├── __init__.py
│   │   ├── app_principal.py   # Janela principal 
│   │   ├── janela_recorte.py  # Ferramenta de recorte
│   │   ├── janela_borracha.py # Ferramenta de borracha
│   │   ├── visualizador.py    # Visualização em tamanho real
│   │   └── componentes.py     # Componentes reutilizáveis (tooltips)
│   ├── processadores/         # Lógica de processamento
│   │   ├── __init__.py
│   │   ├── removedor_fundo.py # Funções de remoção de fundo
│   │   ├── processador_lote.py # Processamento em lote
│   │   └── editor_imagem.py   # Funções de edição
│   └── utils/                 # Utilitários
│       ├── __init__.py
│       └── imagem_utils.py    # Funções auxiliares