# Manual do Usuário - RemoveBG

Este manual apresenta instruções detalhadas para o uso eficiente do RemoveBG para remoção de fundos de imagens.

## Interface Principal

![Interface Principal](diagrama_interface.png)

A interface do RemoveBG é dividida em três áreas principais:

1. **Painel Esquerdo**: Exibe a imagem original
2. **Painel Central**: Exibe a imagem processada (sem fundo)
3. **Painel Direito**: Controles de ajuste e configurações

### Barra de Menu

- **Arquivo**
  - **Selecionar Imagem**: Abre o seletor de arquivos para escolher uma imagem
  - **Salvar Resultado**: Salva a imagem processada
  - **Sair**: Fecha o aplicativo

- **Ferramentas**
  - **Processar Pasta**: Inicia o processamento em lote
  - **Cortar Imagem**: Abre a ferramenta de recorte
  - **Borracha**: Abre a ferramenta de borracha
  - **Recorte em Massa**: Aplica o mesmo recorte em várias imagens

- **Ajuda**
  - **Sobre**: Exibe informações sobre o aplicativo

## Fluxo de Trabalho Básico

### 1. Selecionar uma Imagem

- Clique em **Arquivo > Selecionar Imagem** ou use o atalho correspondente
- Escolha uma imagem nos formatos suportados (PNG, JPG, JPEG, WEBP)
- A imagem selecionada será exibida no painel esquerdo

### 2. Configurar os Ajustes

No painel direito, ajuste as configurações conforme necessário:

- **Modelo de IA**: Escolha o modelo adequado para seu tipo de imagem
- **Alpha Matting**: Ative para melhores resultados em bordas complexas (cabelo, pelos)
- **Limiar Objeto**: Ajuste para controlar quais pixels são considerados parte do objeto
- **Limiar Fundo**: Ajuste para controlar quais pixels são considerados parte do fundo
- **Erosão Máscara**: Ajuste para refinar as bordas da imagem recortada

### 3. Processar a Imagem

- Clique no botão principal **Remover Fundo** no painel lateral direito
- Aguarde o processamento (o tempo varia conforme o tamanho da imagem e o modelo escolhido)
- O resultado será exibido no painel central

### 4. Salvar o Resultado

- Clique em **Arquivo > Salvar Resultado**
- Escolha o local e nome do arquivo para salvar
- A imagem será salva em formato PNG com transparência

## Ferramentas Avançadas

### Recorte de Imagem

1. Selecione **Ferramentas > Cortar Imagem**
2. Na janela de recorte:
   - Clique e arraste para selecionar a área desejada
   - Use os controles de zoom se necessário
   - Clique em "Recortar" para confirmar ou "Cancelar" para sair

### Ferramenta de Borracha

1. Selecione **Ferramentas > Borracha**
2. Na janela da ferramenta de borracha:
   - Ajuste o tamanho da borracha com o controle deslizante
   - Clique e arraste sobre áreas que deseja apagar
   - Use os controles de zoom se necessário
   - Clique em "Salvar Alterações" para confirmar ou "Cancelar" para sair

### Processamento em Lote

1. Selecione **Ferramentas > Processar Pasta**
2. Escolha a pasta de origem com as imagens
3. Escolha a pasta de destino para os resultados
4. O processamento iniciará automaticamente com as configurações atuais
5. Uma barra de progresso mostrará o andamento do processo
6. Ao finalizar, será exibido um resumo do processamento

### Recorte em Massa

1. Selecione **Ferramentas > Recorte em Massa**
2. Escolha a pasta contendo as imagens a serem recortadas
3. Selecione uma imagem modelo para definir a área de recorte
4. Na janela de recorte, selecione a área desejada
5. Clique em "Recortar" para aplicar o mesmo recorte a todas as imagens
6. As imagens recortadas serão salvas na pasta "recorte_output" dentro da pasta de origem

## Visualização de Imagens

- Use os botões **Ver Original** e **Ver Resultado** para abrir as imagens em modo de visualização completa
- Na janela de visualização:
  - Use os botões de zoom para aproximar ou afastar
  - Use a roda do mouse para zoom rápido
  - Arraste a imagem para navegar quando ampliada

## Dicas e Truques

### Escolha do Modelo

- **u2net**: Boa escolha para uso geral
- **u2netp**: Mais rápido, mas pode ter qualidade inferior
- **u2net_human_seg**: Excelente para fotos de pessoas
- **silueta**: Alternativa para uso geral
- **isnet-general-use**: Alta qualidade para a maioria das imagens
- **isnet-anime**: Otimizado para ilustrações e anime

### Alpha Matting

- Ative para cabelos, pelos e bordas detalhadas
- Desative para objetos com bordas bem definidas ou para processamento mais rápido

### Ajuste de Limiares

- **Limiar Objeto Alto + Limiar Fundo Baixo**: Mantém mais detalhes, mas pode deixar resíduos
- **Limiar Objeto Baixo + Limiar Fundo Alto**: Recorte mais "limpo", mas pode perder detalhes

### Erosão da Máscara

- Valores baixos (1-5): Mantém mais detalhes das bordas
- Valores altos (10+): Remove "halos" e artefatos do fundo, mas pode "comer" parte do objeto

## Solução de Problemas

### O aplicativo está lento

- Use modelos mais leves como "u2netp"
- Desative Alpha Matting
- Reduza a resolução da imagem antes de processar

### Resultados com "halos" ou resíduos de fundo

- Aumente o valor de Erosão da Máscara
- Diminua o Limiar de Objeto
- Aumente o Limiar de Fundo

### Detalhes finos (cabelo, pelos) estão sendo perdidos

- Ative Alpha Matting
- Aumente o Limiar de Objeto
- Diminua o Limiar de Fundo
- Diminua a Erosão da Máscara

### Erro ao carregar modelos

- Verifique sua conexão com a internet
- Na primeira execução, os modelos são baixados automaticamente
- Os modelos são armazenados na pasta ".rembg_cache"

## Próximos Passos

Para informações mais técnicas sobre o funcionamento interno do aplicativo, consulte a [Documentação Técnica](documentacao_tecnica.md).
