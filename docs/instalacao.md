# Guia de Instalação do RemoveBG

Este guia detalha o processo de instalação e configuração do RemoveBG em diferentes sistemas operacionais.

## Requisitos do Sistema

- **Sistema Operacional**: Windows, macOS ou Linux
- **Python**: Versão 3.8 ou superior
- **Espaço em Disco**: 
  - Aplicação: ~10MB
  - Modelos de IA: ~100-150MB por modelo (baixados automaticamente na primeira utilização)
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Processador**: Multi-core recomendado para melhor desempenho

## Instalação Passo a Passo

### Windows

1. **Instalar Python**:
   - Baixe o instalador do Python em [python.org](https://www.python.org/downloads/)
   - Durante a instalação, marque a opção "Add Python to PATH"
   - Verifique a instalação abrindo o Prompt de Comando e digitando:
     ```
     python --version
     ```

2. **Baixar o RemoveBG**:
   - Clone o repositório:
     ```
     git clone https://github.com/seu-usuario/RemoveBG.git
     ```
   - Ou baixe como ZIP e extraia

3. **Instalar Dependências**:
   - Navegue até a pasta do projeto:
     ```
     cd RemoveBG
     ```
   - Instale as dependências:
     ```
     pip install -r requirements.txt
     ```

4. **Executar o Aplicativo**:
   ```
   python main.py
   ```

### macOS

1. **Instalar Python**:
   - Baixe o instalador do Python em [python.org](https://www.python.org/downloads/)
   - Ou use o Homebrew:
     ```
     brew install python
     ```
   - Verifique a instalação:
     ```
     python3 --version
     ```

2. **Baixar o RemoveBG**:
   - Clone o repositório:
     ```
     git clone https://github.com/seu-usuario/RemoveBG.git
     ```
   - Ou baixe como ZIP e extraia

3. **Instalar Dependências**:
   - Navegue até a pasta do projeto:
     ```
     cd RemoveBG
     ```
   - Instale as dependências:
     ```
     pip3 install -r requirements.txt
     ```

4. **Executar o Aplicativo**:
   ```
   python3 main.py
   ```

### Linux

1. **Instalar Python**:
   - A maioria das distribuições já vem com Python instalado
   - Se necessário, instale:
     ```
     sudo apt update
     sudo apt install python3 python3-pip
     ```
   - Verifique a instalação:
     ```
     python3 --version
     ```

2. **Instalar Dependências do PyQt6**:
   ```
   sudo apt install python3-pyqt6
   ```

3. **Baixar o RemoveBG**:
   - Clone o repositório:
     ```
     git clone https://github.com/seu-usuario/RemoveBG.git
     ```
   - Ou baixe como ZIP e extraia

4. **Instalar Dependências Python**:
   - Navegue até a pasta do projeto:
     ```
     cd RemoveBG
     ```
   - Instale as dependências:
     ```
     pip3 install -r requirements.txt
     ```

5. **Executar o Aplicativo**:
   ```
   python3 main.py
   ```

## Ambiente Virtual (Recomendado)

É recomendado usar um ambiente virtual para isolar as dependências:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicativo
python main.py
```

## Possíveis Problemas e Soluções

### Erro ao instalar PyQt6

**Problema**: Falha na instalação do PyQt6 com erro de compilação.

**Solução**: 
- Windows: Instale as ferramentas de desenvolvimento C++ do Visual Studio
- Linux: Instale os pacotes de desenvolvimento Qt
  ```
  sudo apt install qtbase5-dev
  ```

### Erro ao baixar modelos de IA

**Problema**: Falha ao baixar os modelos automaticamente.

**Solução**:
1. Verifique sua conexão com a internet
2. Baixe manualmente os modelos do [repositório do rembg](https://github.com/danielgatis/rembg)
3. Coloque os modelos na pasta `.rembg_cache` no diretório do usuário

### ImportError: No module named 'PyQt6'

**Problema**: Módulo PyQt6 não encontrado mesmo após instalação.

**Solução**:
- Verifique se instalou as dependências no ambiente virtual ativo
- Reinstale com:
  ```
  pip install PyQt6
  ```

## Requisitos Recomendados para Melhor Desempenho

Para processar imagens em alta resolução ou lotes de imagens:
- RAM: 16GB+
- CPU: Processador quad-core ou superior
- GPU: Uma placa de vídeo dedicada pode acelerar o processamento em algumas configurações

## Próximos Passos

Após a instalação, consulte o [Manual do Usuário](manual_do_usuario.md) para aprender a utilizar o aplicativo.
