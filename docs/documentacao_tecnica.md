# Documentação Técnica - RemoveBG

Esta documentação fornece detalhes técnicos sobre a arquitetura, estrutura de código e funcionamento interno do RemoveBG.

## Arquitetura do Projeto

O RemoveBG segue uma arquitetura modular com separação clara entre interface gráfica, lógica de processamento e utilitários.

### Estrutura de Diretórios

```
RemoveBG/
│
├── app/                   # Pacote principal da aplicação
│   ├── __init__.py        # Inicialização do pacote
│   ├── configuracoes.py   # Configurações globais
│   │
│   ├── gui/               # Interface gráfica
│   │   ├── __init__.py
│   │   ├── app_principal.py    # Janela principal
│   │   ├── componentes.py      # Componentes reutilizáveis
│   │   ├── janela_borracha.py  # Ferramenta de borracha
│   │   ├── janela_recorte.py   # Ferramenta de recorte
│   │   └── visualizador.py     # Visualizador de imagens
│   │
│   ├── processadores/     # Lógica de processamento
│   │   ├── __init__.py
│   │   ├── editor_imagem.py     # Edição de imagens
│   │   ├── processador_lote.py  # Processamento em lote
│   │   └── removedor_fundo.py   # Remoção de fundo
│   │
│   └── utils/             # Utilitários
│       ├── __init__.py
│       ├── estilos.py  # Estilos globais de cores
│       └── imagem_utils.py  # Funções de manipulação de imagens
│
├── main.py                # Ponto de entrada da aplicação
└── .gitignore             # Arquivos ignorados pelo Git
```

## Framework e Bibliotecas

O projeto utiliza as seguintes tecnologias principais:

- **Python**: Linguagem de programação base
- **PyQt6**: Framework para interface gráfica
- **PIL (Pillow)**: Manipulação de imagens
- **rembg**: Remoção de fundo com IA

## Componentes Principais

### 1. Interface Gráfica (`app/gui/`)

#### `app_principal.py`
Implementa a janela principal da aplicação usando PyQt6, com:
- Organização em painéis (imagem original, resultado e ajustes)
- Menus e ações
- Gerenciamento de estado da aplicação
- Integração com processadores

Classes principais:
- `AplicativoRemoveFundo`: Janela principal
- `ProcessadorThread`: Thread para processamento assíncrono
- `ProcessadorLoteThread`: Thread para processamento em lote
- `RecorteMassaThread`: Thread para recorte em massa

#### Janelas Auxiliares
- `visualizador.py`: Visualização de imagens em tamanho completo com zoom
- `janela_recorte.py`: Implementa a ferramenta de recorte
- `janela_borracha.py`: Implementa a ferramenta de borracha

#### Componentes Reutilizáveis
- `componentes.py`: Implementa componentes como tooltips personalizados

### 2. Processadores (`app/processadores/`)

#### `removedor_fundo.py`
Encapsula a biblioteca rembg para remoção de fundo:
- Gerenciamento de modelos e sessões
- Processamento de imagens individuais
- Controle de parâmetros (alpha matting, limiares, erosão)

#### `processador_lote.py`
Implementa o processamento de múltiplas imagens em uma pasta:
- Listagem de arquivos de imagem
- Processamento sequencial
- Relatórios de sucesso/erro

#### `editor_imagem.py`
Implementa ferramentas de edição:
- Recorte de imagens
- Aplicação de borracha
- Operações em massa

### 3. Utilitários (`app/utils/`)

#### `imagem_utils.py`
Fornece funções auxiliares para manipulação de imagens:
- Criação de previews
- Carregamento com tratamento de EXIF
- Conversão entre formatos de imagem

### 4. Configurações (`app/configuracoes.py`)

Centraliza constantes e configurações:
- Versão do aplicativo
- Modelos disponíveis
- Valores padrão para parâmetros
- Extensões de arquivo suportadas

## Fluxo de Execução

1. **Inicialização** (`main.py`):
   - Cria a instância do aplicativo PyQt6
   - Inicia a janela principal
   - Configura o estilo da aplicação
   - Inicia o loop de eventos

2. **Carregamento de Imagem**:
   - Seleção de arquivo através do diálogo
   - Carregamento com Pillow
   - Normalização (EXIF, conversão para RGBA)
   - Exibição de preview

3. **Remoção de Fundo**:
   - Configuração dos parâmetros
   - Processamento assíncrono em thread separada
   - Conversão da imagem para bytes
   - Chamada à biblioteca rembg
   - Conversão do resultado de volta para PIL

4. **Processamento em Lote**:
   - Seleção de pastas de origem e destino
   - Listagem e filtragem de arquivos
   - Criação de thread de processamento
   - Processamento sequencial com feedback
   - Geração de relatório final

## Gerenciamento de Estado

A aplicação mantém o estado através de variáveis de instância na classe `AplicativoRemoveFundo`:
- `imagem_entrada_completa`: Imagem original carregada
- `imagem_resultado_completa`: Resultado após processamento
- `modelo_selecionado`: Modelo de IA atual
- `processamento_ativo`: Indica processamento em andamento

## Processamento Assíncrono

Para manter a interface responsiva durante o processamento:
- Operações pesadas são realizadas em threads separadas
- Comunicação através de sinais PyQt
- Atualização da interface ao concluir processamento
- Exibição de barras de progresso para operações longas

## Detalhes de Implementação

### Remoção de Fundo com rembg

```python
def processar_imagem(self, imagem, usar_alpha_matting=True, 
                     limiar_objeto=250, limiar_fundo=10, tamanho_erosao=5):
    # Converte a imagem PIL para bytes
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    dados_imagem = buffer.getvalue()
    
    # Processa a remoção de fundo
    bytes_resultado = remove(
        dados_imagem,
        session=self.sessao,
        alpha_matting=usar_alpha_matting,
        alpha_matting_foreground_threshold=limiar_objeto,
        alpha_matting_background_threshold=limiar_fundo,
        alpha_matting_erode_size=tamanho_erosao
    )
    
    # Converte o resultado de volta para imagem PIL
    imagem_resultado = Image.open(io.BytesIO(bytes_resultado)).convert("RGBA")
    return imagem_resultado
```

### Carregamento de Modelos

A biblioteca rembg gerencia o download e armazenamento de modelos. Na primeira utilização, os modelos são baixados automaticamente para a pasta `.rembg_cache` no diretório do usuário.

```python
def __init__(self, nome_modelo="u2net"):
    self.nome_modelo = nome_modelo
    self.sessao = new_session(nome_modelo)
```

### Conversão entre Formatos de Imagem

A aplicação utiliza Pillow (PIL) para manipulação de imagens internamente, mas converte para formatos compatíveis com PyQt6 para exibição na interface:

```python
# Converter de PIL para QPixmap
q_imagem = ImageQt.ImageQt(imagem_pil)
pixmap = QPixmap.fromImage(q_imagem)
```

## Considerações de Desempenho

O desempenho da aplicação depende de vários fatores:

1. **Tamanho da Imagem**: Imagens maiores requerem mais memória e processamento
2. **Modelo Escolhido**:
   - u2netp: Mais rápido, menor qualidade
   - isnet-general-use: Mais lento, melhor qualidade
3. **Alpha Matting**: Aumenta significativamente o tempo de processamento
4. **Hardware**: CPU multi-core e GPU aceleram o processamento

## Tratamento de Erros

A aplicação implementa tratamento de exceções em vários níveis:
- Validação de entradas do usuário
- Try/except em operações críticas
- Feedback visual para o usuário em caso de erro
- Logging de erros no console

## Extensibilidade

O código foi projetado para ser extensível:
- Novos modelos podem ser adicionados em `configuracoes.py`
- Novas ferramentas podem ser implementadas seguindo o padrão das janelas existentes
- O sistema de processamento em thread pode ser reaproveitado para novas funcionalidades
- A separação clara entre UI e lógica facilita a modificação independente

## Limitações Conhecidas

- O processamento de imagens muito grandes (>4000px) pode ser lento
- Modelos de IA ocupam espaço significativo em disco
- Algumas imagens complexas podem requerer ajustes manuais
- O Alpha Matting em modelos pesados pode ser muito lento em hardware modesto
