# RemoveBG - Removedor de Fundos de Imagens

![Versão](https://img.shields.io/badge/Versão-0.9.0-blue)

RemoveBG é uma aplicação desktop que permite remover o fundo de imagens de forma intuitiva e eficiente, utilizando inteligência artificial para obter resultados de alta qualidade.

## 🌟 Funcionalidades

- **Remoção de Fundo**: Remove o fundo de imagens utilizando modelos de IA
- **Múltiplos Modelos**: Suporte para diferentes modelos de IA (u2net, u2netp, u2net_human_seg, silueta, isnet-general-use, isnet-anime)
- **Processamento em Lote**: Processe múltiplas imagens de uma só vez
- **Ferramentas de Edição**:
  - Recorte de imagem
  - Ferramenta de borracha
  - Recorte em massa
- **Visualização Avançada**: Visualização com zoom e navegação intuitiva
- **Ajustes Finos**: Opções de configuração para resultados personalizados
- **Interface Amigável**: Interface gráfica simples e intuitiva

## 🔧 Requisitos

- Python 3.12+ (usei a versão 3.12.9)
- PyQt6
- Pillow (PIL)
- rembg

## 📥 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/RemoveBG.git
   cd RemoveBG
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   python main.py
   ```

Para instruções detalhadas, consulte o [Guia de Instalação](docs/instalacao.md).

## 📖 Como Usar

1. **Iniciar a aplicação**: Execute `python main.py`
2. **Selecionar Imagem**: Use o menu "Arquivo > Selecionar Imagem" ou o botão correspondente
3. **Escolher Modelo**: Selecione o modelo de IA desejado no painel lateral
4. **Ajustar Configurações**: Configure parâmetros como Alpha Matting, Limiar e Erosão
5. **Processar Imagem**: Clique em "Aplicar Ajustes" para remover o fundo
6. **Salvar Resultado**: Use o menu "Arquivo > Salvar Resultado"

Para um guia detalhado, consulte o [Manual do Usuário](docs/manual_do_usuario.md).

## 📝 Documentação

- [Guia de Instalação](docs/instalacao.md)
- [Manual do Usuário](docs/manual_do_usuario.md)
- [Documentação Técnica](docs/documentacao_tecnica.md)
- [Guia de Contribuição](docs/contribuicao.md)

## 🔄 Modelos Disponíveis

| Modelo | Descrição | Caso de Uso |
|--------|-----------|-------------|
| u2net | Modelo padrão | Uso geral |
| u2netp | Mais leve e rápido | Processamento rápido |
| u2net_human_seg | Otimizado para pessoas | Fotos de pessoas |
| silueta | Alternativo | Uso geral alternativo |
| isnet-general-use | Alta qualidade | Melhor qualidade geral |
| isnet-anime | Otimizado para anime | Imagens de anime e ilustrações |

## ⚠️ Limitações

- O processamento de imagens muito grandes pode ser lento
- Algumas imagens complexas podem requerer ajustes manuais para resultados ideais
- Os modelos de IA serão baixados na primeira utilização (~100-150MB cada)

## 🔮 Desenvolvimento Futuro

- Suporte para processamento de vídeos
- Ajuste de cores do fundo
- Substituição inteligente de fundos
- Melhorias na detecção de bordas

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Contato

Para dúvidas, sugestões ou contribuições, abra uma issue no GitHub ou entre em contato pelo email: seu-email@exemplo.com
