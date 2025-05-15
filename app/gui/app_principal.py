import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, Menu, Canvas, Scrollbar
from PIL import Image, ImageTk
import os
import threading
import io

from app.configuracoes import (
    VERSAO, TITULO_APP, MODELOS_DISPONIVEIS, MODELO_PADRAO,
    ALPHA_MATTING_PADRAO, LIMIAR_OBJETO_PADRAO, LIMIAR_FUNDO_PADRAO, 
    EROSAO_MASCARA_PADRAO, EXTENSOES_SUPORTADAS
)
from app.gui.componentes import DicaFlutuante
from app.gui.janela_recorte import JanelaRecorte
from app.gui.janela_borracha import JanelaBorracha
from app.gui.visualizador import VisualizadorImagem
from app.processadores.removedor_fundo import RemoveFundo
from app.processadores.processador_lote import ProcessadorLote
from app.processadores.editor_imagem import EditorImagem
from app.utils.imagem_utils import criar_preview, carregar_imagem

class AplicativoRemoveFundo(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(TITULO_APP)
        self.geometry("1150x850")
        self.resizable(True, True)

        # Variáveis para guardar o modelo selecionado
        self.modelo_selecionado_var = StringVar(value=MODELO_PADRAO)

        # Objeto removedor de fundo
        self.removedor = RemoveFundo(self.modelo_selecionado_var.get())

        # Configuração do layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cabeçalho ---
        self.criar_cabecalho()
        
        # --- Menu Superior ---
        self.criar_menu()

        # --- Frame Principal ---
        self.criar_frame_principal()

        # --- Barra de Status e Progresso ---
        self.criar_barra_status()

        # --- Variáveis de Estado ---
        self.imagem_entrada_completa = None
        self.imagem_resultado_completa = None
        self.tk_preview_entrada = None
        self.tk_preview_resultado = None
        self.caminho_arquivo_atual = None
        self.processamento_ativo = False
        self.id_imagem_canvas_original = None
        self.id_imagem_canvas_resultado = None

        # Vincular eventos de redimensionamento
        self.canvas_imagem_original.bind("<Configure>", self.redimensionar_previews)
        self.canvas_imagem_resultado.bind("<Configure>", self.redimensionar_previews)

        # Inicializar as configurações padrão
        self.restaurar_padroes()

        # Atualizar estados dos menus
        self.atualizar_estados_menu()
        
    def criar_cabecalho(self):
        """Cria o cabeçalho da aplicação"""
        self.frame_cabecalho = ctk.CTkFrame(self)
        self.frame_cabecalho.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.frame_cabecalho.grid_columnconfigure(1, weight=1)
        
        self.botao_sobre = ctk.CTkButton(self.frame_cabecalho, text="Sobre", command=self.mostrar_sobre, width=80)
        self.botao_sobre.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.rotulo_cabecalho = ctk.CTkLabel(self.frame_cabecalho, 
                                           text=f"Removedor de Fundos v{VERSAO} - Beta",
                                           font=ctk.CTkFont(size=36, weight="bold"))
        self.rotulo_cabecalho.grid(row=0, column=1, padx=10, sticky="ew")
        
    def criar_menu(self):
        """Cria o menu principal da aplicação"""
        self.barra_menu = Menu(self)
        self.config(menu=self.barra_menu)
        
        # Menu Arquivo
        self.menu_arquivo = Menu(self.barra_menu, tearoff=0)
        self.menu_arquivo.add_command(label="Selecionar Imagem", command=self.selecionar_imagem)
        self.menu_arquivo.add_command(label="Salvar Resultado", command=lambda: self.salvar_imagem())
        self.menu_arquivo.add_separator()
        self.menu_arquivo.add_command(label="Sair", command=self.quit)
        self.barra_menu.add_cascade(label="Arquivo", menu=self.menu_arquivo)
        
        # Menu Ferramentas
        self.menu_ferramentas = Menu(self.barra_menu, tearoff=0)
        self.menu_ferramentas.add_command(label="Processar Pasta", 
                                         command=lambda: self.processar_pasta())
        self.menu_ferramentas.add_command(label="Aplicar Ajustes", 
                                         command=lambda: self.processar_imagem())
        self.menu_ferramentas.add_command(label="Cortar Imagem", 
                                         command=lambda: self.abrir_ferramenta_recorte())
        self.menu_ferramentas.add_command(label="Borracha", 
                                         command=lambda: self.abrir_ferramenta_borracha())
        self.menu_ferramentas.add_command(label="Recorte em Massa", 
                                         command=lambda: self.recortar_imagens_em_massa())
        self.barra_menu.add_cascade(label="Ferramentas", menu=self.menu_ferramentas)
        
        # Menu Ajuda
        self.menu_ajuda = Menu(self.barra_menu, tearoff=0)
        self.menu_ajuda.add_command(label="Sobre", command=lambda: self.mostrar_sobre())
        self.barra_menu.add_cascade(label="Ajuda", menu=self.menu_ajuda)
        
    def criar_frame_principal(self):
        """Cria o frame principal da aplicação"""
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.frame_principal.grid_columnconfigure((0, 1), weight=1)
        self.frame_principal.grid_columnconfigure(2, weight=0, minsize=220)
        self.frame_principal.grid_rowconfigure(1, weight=1)
        
        self.criar_painel_original()
        self.criar_painel_resultado()
        self.criar_painel_ajustes()
        
    def criar_painel_original(self):
        """Cria o painel da imagem original"""
        self.frame_original = ctk.CTkFrame(self.frame_principal)
        self.frame_original.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.frame_original.grid_rowconfigure(1, weight=1)
        self.frame_original.grid_columnconfigure(0, weight=1)
        
        self.rotulo_original = ctk.CTkLabel(self.frame_original, text="Imagem Original (Preview)")
        self.rotulo_original.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        
        self.canvas_imagem_original = ctk.CTkCanvas(self.frame_original, 
                                                  bg=self.cget('bg'), 
                                                  highlightthickness=0)
        self.canvas_imagem_original.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.botao_ver_original = ctk.CTkButton(self.frame_original, 
                                              text="Ver Original", 
                                              command=lambda: self.mostrar_imagem_completa('original'), 
                                              state="disabled")
        self.botao_ver_original.grid(row=2, column=0, padx=10, pady=5, sticky="s")
        
    def criar_painel_resultado(self):
        """Cria o painel da imagem resultado"""
        self.frame_resultado = ctk.CTkFrame(self.frame_principal)
        self.frame_resultado.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.frame_resultado.grid_rowconfigure(1, weight=1)
        self.frame_resultado.grid_columnconfigure(0, weight=1)
        
        self.rotulo_resultado = ctk.CTkLabel(self.frame_resultado, text="Resultado (Preview)")
        self.rotulo_resultado.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        
        self.canvas_imagem_resultado = ctk.CTkCanvas(self.frame_resultado, 
                                                   bg=self.cget('bg'), 
                                                   highlightthickness=0)
        self.canvas_imagem_resultado.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.botao_ver_resultado = ctk.CTkButton(self.frame_resultado, 
                                              text="Ver Resultado", 
                                              command=lambda: self.mostrar_imagem_completa('resultado'), 
                                              state="disabled")
        self.botao_ver_resultado.grid(row=2, column=0, padx=10, pady=5, sticky="s")
        
    def criar_painel_ajustes(self):
        """Cria o painel de ajustes e controles"""
        self.frame_ajustes = ctk.CTkFrame(self.frame_principal)
        self.frame_ajustes.grid(row=0, column=2, rowspan=2, padx=(5, 10), pady=10, sticky="ns")
        
        rotulo_ajustes = ctk.CTkLabel(self.frame_ajustes, 
                                    text="Ajustes e Modelo", 
                                    font=ctk.CTkFont(weight="bold"))
        rotulo_ajustes.pack(pady=(10, 15), padx=10)
        
        # Seleção de Modelo
        rotulo_modelo = ctk.CTkLabel(self.frame_ajustes, text="Modelo de IA:")
        rotulo_modelo.pack(pady=(5, 0), padx=10, anchor="w")
        
        self.menu_modelo = ctk.CTkOptionMenu(self.frame_ajustes,
                                           variable=self.modelo_selecionado_var,
                                           values=MODELOS_DISPONIVEIS,
                                           command=self.ao_mudar_modelo)
        self.menu_modelo.pack(pady=(0, 10), padx=10, fill="x")
        
        DicaFlutuante(rotulo_modelo, 
                    "Escolha o modelo de Inteligência Artificial para remover o fundo.\n"
                    "- u2net: Padrão, bom para uso geral.\n"
                    "- u2netp: Mais rápido, qualidade pode variar.\n"
                    "- u2net_human_seg: Otimizado para pessoas.\n"
                    "- silueta: Alternativa geral.\n"
                    "- isnet-*: Modelos mais recentes, boa qualidade (podem ser mais lentos).\n"
                    "Experimente modelos diferentes para melhores resultados!")
        
        DicaFlutuante(self.menu_modelo, "Escolha o modelo de IA (veja dica acima).")
        
        # Controles Alpha Matting
        self.alpha_matting_var = ctk.BooleanVar(value=ALPHA_MATTING_PADRAO)
        self.check_alpha_matting = ctk.CTkCheckBox(self.frame_ajustes, 
                                                 text="Alpha Matting", 
                                                 variable=self.alpha_matting_var, 
                                                 command=self.ao_mudar_configuracoes)
        self.check_alpha_matting.pack(pady=5, padx=10, anchor="w")
        
        DicaFlutuante(self.check_alpha_matting, 
                    "Técnica adicional para refinar bordas suaves (como cabelo ou pelos).\n"
                    "Pode aumentar o tempo de processamento.\n"
                    "Desative se o resultado parecer estranho ou muito lento.")
        
        # Limiar Objeto
        rotulo_limiar_objeto = ctk.CTkLabel(self.frame_ajustes, text="Limiar Objeto (0-255)")
        rotulo_limiar_objeto.pack(pady=(10, 0), padx=10, anchor="w")
        
        self.limiar_objeto_var = ctk.IntVar(value=LIMIAR_OBJETO_PADRAO)
        self.slider_limiar_objeto = ctk.CTkSlider(self.frame_ajustes, 
                                                from_=0, 
                                                to=255, 
                                                number_of_steps=255, 
                                                variable=self.limiar_objeto_var, 
                                                command=lambda v: self.atualizar_rotulo_slider(v, 
                                                                                            self.rotulo_limiar_objeto, 
                                                                                            "Limiar Objeto"))
        self.slider_limiar_objeto.pack(pady=5, padx=10, fill="x")
        
        self.rotulo_limiar_objeto = ctk.CTkLabel(self.frame_ajustes, 
                                               text=f"Limiar Objeto: {self.limiar_objeto_var.get()}")
        self.rotulo_limiar_objeto.pack(pady=(0,10), padx=10, anchor="w")
        
        DicaFlutuante(rotulo_limiar_objeto, 
                    "Define o quão 'opaco' um pixel precisa ser para ser considerado parte do objeto principal.\n"
                    "Valores MAIORES: Tende a incluir mais áreas semi-transparentes no objeto.\n"
                    "Valores MENORES: Tende a tornar as bordas do objeto mais 'duras' e definidas.\n"
                    "(Funciona melhor com Alpha Matting ativado)")
        
        # Limiar Fundo
        rotulo_limiar_fundo = ctk.CTkLabel(self.frame_ajustes, text="Limiar Fundo (0-255)")
        rotulo_limiar_fundo.pack(pady=(10, 0), padx=10, anchor="w")
        
        self.limiar_fundo_var = ctk.IntVar(value=LIMIAR_FUNDO_PADRAO)
        self.slider_limiar_fundo = ctk.CTkSlider(self.frame_ajustes, 
                                               from_=0, 
                                               to=255, 
                                               number_of_steps=255, 
                                               variable=self.limiar_fundo_var, 
                                               command=lambda v: self.atualizar_rotulo_slider(v, 
                                                                                           self.rotulo_limiar_fundo, 
                                                                                           "Limiar Fundo"))
        self.slider_limiar_fundo.pack(pady=5, padx=10, fill="x")
        
        self.rotulo_limiar_fundo = ctk.CTkLabel(self.frame_ajustes, 
                                              text=f"Limiar Fundo: {self.limiar_fundo_var.get()}")
        self.rotulo_limiar_fundo.pack(pady=(0,10), padx=10, anchor="w")
        
        DicaFlutuante(rotulo_limiar_fundo, 
                    "Define o quão 'transparente' um pixel precisa ser para ser considerado parte do fundo.\n"
                    "Valores MAIORES: Tende a remover mais áreas, potencialmente 'comendo' bordas do objeto.\n"
                    "Valores MENORES: Tende a preservar mais detalhes nas bordas, mas pode deixar 'fantasmas' do fundo.\n"
                    "(Funciona melhor com Alpha Matting ativado)")
        
        # Erosão Máscara
        rotulo_erosao = ctk.CTkLabel(self.frame_ajustes, text="Erosão Máscara (0-50)")
        rotulo_erosao.pack(pady=(10, 0), padx=10, anchor="w")
        
        self.erosao_tamanho_var = ctk.IntVar(value=EROSAO_MASCARA_PADRAO)
        self.slider_erosao = ctk.CTkSlider(self.frame_ajustes, 
                                         from_=0, 
                                         to=50, 
                                         number_of_steps=50, 
                                         variable=self.erosao_tamanho_var, 
                                         command=lambda v: self.atualizar_rotulo_slider(v, 
                                                                                      self.rotulo_erosao, 
                                                                                      "Erosão Máscara"))
        self.slider_erosao.pack(pady=5, padx=10, fill="x")
        
        self.rotulo_erosao = ctk.CTkLabel(self.frame_ajustes, 
                                        text=f"Erosão Máscara: {self.erosao_tamanho_var.get()}")
        self.rotulo_erosao.pack(pady=(0,10), padx=10, anchor="w")
        
        DicaFlutuante(rotulo_erosao, 
                    "Reduz o tamanho da máscara final (recorte) em alguns pixels.\n"
                    "Útil para remover pequenas bordas ou 'halos' que sobraram do fundo.\n"
                    "Valores maiores 'encolhem' mais o objeto principal.\n"
                    "(Funciona melhor com Alpha Matting ativado)")
        
        # Botão Restaurar Padrões
        self.botao_restaurar_padroes = ctk.CTkButton(self.frame_ajustes, 
                                                   text="Restaurar Padrões", 
                                                   command=self.restaurar_padroes)
        self.botao_restaurar_padroes.pack(pady=5, padx=10, fill="x")
        
        DicaFlutuante(self.botao_restaurar_padroes, 
                    "Restaura os valores para configurações recomendadas.")
        
    def criar_barra_status(self):
        """Cria a barra de status e progresso"""
        self.frame_status = ctk.CTkFrame(self)
        self.frame_status.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.frame_status.grid_columnconfigure(0, weight=1)
        
        self.rotulo_status = ctk.CTkLabel(self.frame_status, text="Pronto", anchor="w")
        self.rotulo_status.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.barra_progresso = ctk.CTkProgressBar(self.frame_status, orientation="horizontal", mode="determinate")
        self.barra_progresso.set(0)
        # A barra de progresso só será exibida quando necessário
    
    def atualizar_estados_menu(self):
        """Atualiza os estados dos itens do menu com base no estado atual da aplicação"""
        tem_resultado = self.imagem_resultado_completa is not None
        tem_imagem = self.imagem_entrada_completa is not None
        
        self.menu_arquivo.entryconfig(1, state="normal" if tem_resultado else "disabled")  # "Salvar Resultado"
        self.menu_ferramentas.entryconfig(1, state="normal" if tem_imagem else "disabled")  # "Aplicar Ajustes"
        self.menu_ferramentas.entryconfig(2, state="normal" if tem_imagem else "disabled")  # "Cortar Imagem"
        self.menu_ferramentas.entryconfig(3, state="normal" if tem_imagem else "disabled")  # "Borracha"
    
    def mostrar_sobre(self):
        """Exibe informações sobre o aplicativo"""
        texto_info = (f"Remover Fundo v{VERSAO}\n\n"
                    "Criado por: Guilherme de Freitas Moreira\n"
                    "Adaptado e Melhorado por: Multiplas AI's\n\n"
                    "Funcionalidades:\n"
                    "- Remove fundo de imagens (PNG, JPG, JPEG, WEBP).\n"
                    "- Processamento em lote de pastas.\n"
                    "- Visualização de alta resolução com Zoom.\n"
                    "- Seleção de Modelo de IA (afeta qualidade e velocidade).\n"
                    "- Ajustes finos (Alpha Matting, Limiares, Erosão) para refinar o recorte.\n"
                    "- Barra de progresso para lotes.\n\n"
                    "Dica: Passe o mouse sobre os controles de ajuste para ver o que eles fazem! "
                    "Experimente diferentes modelos e ajustes para obter o melhor resultado."
                   )
        messagebox.showinfo("Sobre", texto_info)
    
    def ao_mudar_modelo(self, modelo_selecionado):
        """Chamado quando o usuário seleciona um novo modelo"""
        print(f"Modelo selecionado: {modelo_selecionado}")
        try:
            # Atualiza o modelo no removedor
            self.removedor.mudar_modelo(modelo_selecionado)
            print("Sessão rembg atualizada.")
            # Habilita o botão de reprocessar se uma imagem estiver carregada
            self.ao_mudar_configuracoes()
        except Exception as e:
            messagebox.showerror("Erro de Modelo", 
                               f"Não foi possível carregar o modelo '{modelo_selecionado}':\n{e}\n\n"
                               "Verifique se o rembg e suas dependências estão instalados corretamente "
                               "ou se o modelo é válido.")
            self.modelo_selecionado_var.set(MODELO_PADRAO)
            self.removedor.mudar_modelo(MODELO_PADRAO)
    
    def atualizar_rotulo_slider(self, valor, widget_rotulo, prefixo):
        """Atualiza o texto do rótulo de um slider e habilita reprocessamento"""
        widget_rotulo.configure(text=f"{prefixo}: {int(valor)}")
        self.ao_mudar_configuracoes()
    
    def ao_mudar_configuracoes(self, *args):
        """Chamado quando qualquer controle de ajuste (slider, checkbox, modelo) muda"""
        if self.imagem_entrada_completa and not self.processamento_ativo:
            self.atualizar_estados_menu()
    
    def selecionar_imagem(self):
        """Abre o diálogo para selecionar uma imagem"""
        if self.processamento_ativo:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return
            
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione a Imagem",
            filetypes=[("Arquivos de Imagem", " ".join(f"*{ext}" for ext in EXTENSOES_SUPORTADAS))]
        )
        
        if caminho_arquivo:
            try:
                self.rotulo_status.configure(text="Carregando imagem...")
                self.update()
                
                imagem = carregar_imagem(caminho_arquivo)
                self.imagem_entrada_completa = imagem
                self.caminho_arquivo_atual = caminho_arquivo
                self.imagem_resultado_completa = None
                
                if self.id_imagem_canvas_original:
                    self.canvas_imagem_original.delete(self.id_imagem_canvas_original)
                if self.id_imagem_canvas_resultado:
                    self.canvas_imagem_resultado.delete(self.id_imagem_canvas_resultado)
                    self.id_imagem_canvas_resultado = None
                
                self.exibir_imagem_no_canvas(self.canvas_imagem_original, self.imagem_entrada_completa, 'entrada')
                
                self.botao_ver_original.configure(state="normal")
                self.botao_ver_resultado.configure(state="disabled")
                self.rotulo_status.configure(text=f"Imagem carregada: {os.path.basename(caminho_arquivo)}")
                self.atualizar_estados_menu()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao abrir a imagem:\n{e}")
                self.rotulo_status.configure(text="Erro ao carregar imagem!")
                self.resetar_estado_interface()
    
    def redimensionar_previews(self, evento=None):
        """Redimensiona as imagens de preview quando a janela é redimensionada"""
        if self.winfo_exists():
            if self.imagem_entrada_completa:
                self.exibir_imagem_no_canvas(self.canvas_imagem_original, self.imagem_entrada_completa, 'entrada')
            if self.imagem_resultado_completa:
                self.exibir_imagem_no_canvas(self.canvas_imagem_resultado, self.imagem_resultado_completa, 'resultado')
    
    def exibir_imagem_no_canvas(self, canvas, imagem_pil, tipo_imagem):
        """Exibe uma imagem PIL no canvas especificado"""
        try:
            largura_canvas = canvas.winfo_width()
            altura_canvas = canvas.winfo_height()
            
            if largura_canvas <= 1 or altura_canvas <= 1:
                if self.winfo_exists():
                    self.after(50, lambda: self.exibir_imagem_no_canvas(canvas, imagem_pil, tipo_imagem))
                return
            
            imagem_preview = criar_preview(imagem_pil, largura_canvas, altura_canvas)
            imagem_tk = ImageTk.PhotoImage(imagem_preview)
            
            if tipo_imagem == 'entrada':
                self.tk_preview_entrada = imagem_tk
                if self.id_imagem_canvas_original:
                    canvas.delete(self.id_imagem_canvas_original)
                self.id_imagem_canvas_original = canvas.create_image(
                    largura_canvas / 2, altura_canvas / 2, 
                    anchor='center', image=imagem_tk
                )
                
            elif tipo_imagem == 'resultado':
                self.tk_preview_resultado = imagem_tk
                if self.id_imagem_canvas_resultado:
                    canvas.delete(self.id_imagem_canvas_resultado)
                self.id_imagem_canvas_resultado = canvas.create_image(
                    largura_canvas / 2, altura_canvas / 2, 
                    anchor='center', image=imagem_tk
                )
                
        except Exception as e:
            print(f"Erro ao exibir imagem no canvas ({tipo_imagem}): {e}")
    
    def abrir_ferramenta_recorte(self):
        """Abre a janela para recortar a imagem original"""
        if not self.imagem_entrada_completa:
            messagebox.showwarning("Atenção", "Nenhuma imagem carregada para recorte!")
            return
            
        JanelaRecorte(self, self.imagem_entrada_completa, self.aplicar_recorte)
    
    def aplicar_recorte(self, imagem_recortada):
        """Callback chamado quando o recorte é concluído"""
        self.imagem_entrada_completa = imagem_recortada
        self.exibir_imagem_no_canvas(self.canvas_imagem_original, self.imagem_entrada_completa, 'entrada')
        self.atualizar_estados_menu()
        self.imagem_resultado_completa = None
        if self.id_imagem_canvas_resultado:
            self.canvas_imagem_resultado.delete(self.id_imagem_canvas_resultado)
            self.id_imagem_canvas_resultado = None
            
        self.botao_ver_resultado.configure(state="disabled")
        self.rotulo_status.configure(text="Imagem recortada com sucesso.")
    
    def abrir_ferramenta_borracha(self):
        """Abre a janela para apagar áreas da imagem com uma borracha"""
        if not self.imagem_entrada_completa:
            messagebox.showwarning("Atenção", "Nenhuma imagem carregada para edição!")
            return
            
        JanelaBorracha(self, self.imagem_entrada_completa, self.aplicar_borracha)
    
    def aplicar_borracha(self, imagem_editada):
        """Callback chamado quando a edição com borracha é concluída"""
        self.imagem_entrada_completa = imagem_editada
        self.exibir_imagem_no_canvas(self.canvas_imagem_original, self.imagem_entrada_completa, 'entrada')
        self.atualizar_estados_menu()
        self.imagem_resultado_completa = None
        if self.id_imagem_canvas_resultado:
            self.canvas_imagem_resultado.delete(self.id_imagem_canvas_resultado)
            self.id_imagem_canvas_resultado = None
            
        self.botao_ver_resultado.configure(state="disabled")
        self.rotulo_status.configure(text="Imagem editada com sucesso.")
    
    def processar_imagem(self):
        """Processa a imagem para remover o fundo"""
        if not self.imagem_entrada_completa:
            messagebox.showwarning("Atenção", "Selecione uma imagem primeiro!")
            return
            
        if self.processamento_ativo:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return
            
        def executar_processamento():
            self.processamento_ativo = True
            self.definir_interface_processando(True)
            self.after(0, lambda: self.rotulo_status.configure(
                text=f"Processando com modelo '{self.modelo_selecionado_var.get()}'..."))
            self.after(0, self.update)
            
            try:
                # Obter valores de configuração
                usar_alpha_matting = self.alpha_matting_var.get()
                limiar_objeto = self.limiar_objeto_var.get()
                limiar_fundo = self.limiar_fundo_var.get()
                tamanho_erosao = self.erosao_tamanho_var.get()
                
                # Processar a imagem
                imagem_resultado = self.removedor.processar_imagem(
                    self.imagem_entrada_completa,
                    usar_alpha_matting,
                    limiar_objeto,
                    limiar_fundo,
                    tamanho_erosao
                )
                
                self.imagem_resultado_completa = imagem_resultado
                self.after(0, self.atualizar_interface_apos_processamento)
                
            except Exception as e:
                mensagem_erro = f"Falha ao remover o fundo:\n{e}"
                self.after(0, lambda: messagebox.showerror("Erro de Processamento", mensagem_erro))
                self.after(0, lambda: self.rotulo_status.configure(text="Erro no processamento!"))
            finally:
                self.processamento_ativo = False
                self.after(0, lambda: self.definir_interface_processando(False))
        
        threading.Thread(target=executar_processamento, daemon=True).start()
    
    def atualizar_interface_apos_processamento(self):
        """Atualiza a interface após o processamento ser concluído"""
        if self.imagem_resultado_completa:
            self.exibir_imagem_no_canvas(self.canvas_imagem_resultado, self.imagem_resultado_completa, 'resultado')
            self.rotulo_status.configure(text="Processamento concluído!")
            self.botao_ver_resultado.configure(state="normal")
        else:
            self.rotulo_status.configure(text="Falha ao gerar resultado.")
        self.atualizar_estados_menu()
    
    def definir_interface_processando(self, processando):
        """Atualiza o estado da interface durante o processamento"""
        estado = "disabled" if processando else "normal"
        self.barra_menu.entryconfig("Arquivo", state=estado)
        self.barra_menu.entryconfig("Ferramentas", state=estado)
        self.barra_menu.entryconfig("Ajuda", state=estado)
    
    def resetar_estado_interface(self):
        """Reseta o estado da interface"""
        self.imagem_entrada_completa = None
        self.imagem_resultado_completa = None
        self.caminho_arquivo_atual = None
        
        if self.id_imagem_canvas_original:
            self.canvas_imagem_original.delete(self.id_imagem_canvas_original)
            self.id_imagem_canvas_original = None
            
        if self.id_imagem_canvas_resultado:
            self.canvas_imagem_resultado.delete(self.id_imagem_canvas_resultado)
            self.id_imagem_canvas_resultado = None
            
        self.tk_preview_entrada = None
        self.tk_preview_resultado = None
        
        self.definir_interface_processando(False)
        self.rotulo_status.configure(text="Pronto")
        self.botao_ver_original.configure(state="disabled")
        self.botao_ver_resultado.configure(state="disabled")
        self.atualizar_estados_menu()
    
    def salvar_imagem(self):
        """Salva a imagem processada ou a imagem editada pela ferramenta de borracha"""
        if self.imagem_resultado_completa:
            imagem_para_salvar = self.imagem_resultado_completa
        elif self.imagem_entrada_completa:
            imagem_para_salvar = self.imagem_entrada_completa
        else:
            messagebox.showwarning("Atenção", "Não há imagem processada ou editada para salvar!")
            return
            
        if self.processamento_ativo:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return
            
        nome_arquivo_original = os.path.basename(self.caminho_arquivo_atual or "imagem")
        nome, _ = os.path.splitext(nome_arquivo_original)
        nome_padrao = f"{nome}_editado.png"
        
        caminho_arquivo = filedialog.asksaveasfilename(
            title="Salvar Imagem",
            initialfile=nome_padrao,
            defaultextension=".png",
            filetypes=[("Arquivos PNG", "*.png")]
        )
        
        if caminho_arquivo:
            try:
                self.rotulo_status.configure(text="Salvando imagem...")
                self.update()
                imagem_para_salvar.save(caminho_arquivo)
                self.rotulo_status.configure(text="Imagem salva com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar a imagem:\n{e}")
                self.rotulo_status.configure(text="Erro ao salvar!")
    
    def restaurar_padroes(self):
        """Restaura as configurações para os valores padrão"""
        # Modelo
        self.modelo_selecionado_var.set(MODELO_PADRAO)
        self.menu_modelo.set(MODELO_PADRAO)
        
        try:
            self.removedor.mudar_modelo(MODELO_PADRAO)
            print("Sessão rembg restaurada para o padrão:", MODELO_PADRAO)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao restaurar o modelo padrão:\n{e}")
        
        # Outros controles
        self.alpha_matting_var.set(ALPHA_MATTING_PADRAO)
        self.limiar_objeto_var.set(LIMIAR_OBJETO_PADRAO)
        self.limiar_fundo_var.set(LIMIAR_FUNDO_PADRAO)
        self.erosao_tamanho_var.set(EROSAO_MASCARA_PADRAO)
        
        # Atualizar rótulos
        self.rotulo_limiar_objeto.configure(text=f"Limiar Objeto: {self.limiar_objeto_var.get()}")
        self.rotulo_limiar_fundo.configure(text=f"Limiar Fundo: {self.limiar_fundo_var.get()}")
        self.rotulo_erosao.configure(text=f"Erosão Máscara: {self.erosao_tamanho_var.get()}")
        
        if self.imagem_entrada_completa and not self.processamento_ativo:
            self.atualizar_estados_menu()
        
        self.rotulo_status.configure(text="Valores restaurados para os padrões.")
    
    def processar_pasta(self):
        """Abre diálogos para processar todas as imagens em uma pasta"""
        if self.processamento_ativo:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return
            
        pasta_origem = filedialog.askdirectory(title="Selecione a Pasta com Imagens")
        if not pasta_origem: 
            return
            
        pasta_destino = filedialog.askdirectory(title="Selecione a Pasta de Destino")
        if not pasta_destino: 
            return
            
        if pasta_origem == pasta_destino:
            messagebox.showerror("Erro", "A pasta de origem e destino não podem ser a mesma.")
            return
        
        # Verificar se a pasta contém imagens válidas
        processador_lote = ProcessadorLote(self.removedor, pasta_origem, pasta_destino, 
                                         self.atualizar_progresso_lote)
        
        imagens = processador_lote.listar_imagens()
        if not imagens:
            messagebox.showinfo("Informação", "Nenhuma imagem compatível encontrada na pasta selecionada.")
            return
            
        total_arquivos = len(imagens)
        nome_modelo = self.modelo_selecionado_var.get()
        
        # Preparar interface para processamento
        self.definir_interface_processando(True)
        self.barra_progresso.grid(row=1, column=0, padx=10, pady=(0,5), sticky="ew")
        self.barra_progresso.set(0)
        self.rotulo_status.configure(text=f"Iniciando lote ({nome_modelo}): {total_arquivos} imagens...")
        self.update()
        
        def processar_lote():
            # Obter configurações atuais
            usar_alpha_matting = self.alpha_matting_var.get()
            limiar_objeto = self.limiar_objeto_var.get()
            limiar_fundo = self.limiar_fundo_var.get()
            tamanho_erosao = self.erosao_tamanho_var.get()
            
            # Executar processamento
            arquivos_processados, total, erros = processador_lote.processar(
                usar_alpha_matting, limiar_objeto, limiar_fundo, tamanho_erosao
            )
            
            # Atualizar interface após conclusão
            self.after(0, self.finalizar_processamento_lote, 
                    arquivos_processados, total, erros, nome_modelo)
        
        self.processamento_ativo = True
        threading.Thread(target=processar_lote, daemon=True).start()
    
    def atualizar_progresso_lote(self, valor_progresso, texto_status):
        """Atualiza a barra de progresso e o status durante processamento em lote"""
        if self.winfo_exists():
            self.barra_progresso.set(valor_progresso)
            self.rotulo_status.configure(text=texto_status)
    
    def finalizar_processamento_lote(self, processados, total, erros, nome_modelo):
        """Finaliza o processamento em lote e atualiza a interface"""
        if not self.winfo_exists(): 
            return
            
        self.processamento_ativo = False
        self.definir_interface_processando(False)
        self.barra_progresso.grid_remove()
        self.barra_progresso.set(0)
        
        mensagem_final = f"Processamento em lote ({nome_modelo}) concluído.\n"
        mensagem_final += f"{processados}/{total} imagem(ns) processada(s) com sucesso!"
        
        texto_status = f"Lote ({nome_modelo}) finalizado: {processados} sucesso(s), {len(erros)} erro(s)."
        
        if erros:
            mensagem_final += f"\n\nOcorreram {len(erros)} erro(s):\n"
            mensagem_final += "\n".join(f"- {err}" for err in erros[:5])
            
            if len(erros) > 5:
                mensagem_final += "\n- ... (veja o console/log para mais detalhes)"
                
            messagebox.showwarning("Lote Concluído com Erros", mensagem_final)
        else:
            messagebox.showinfo("Lote Concluído", mensagem_final)
            
        self.rotulo_status.configure(text=texto_status)
    
    def mostrar_imagem_completa(self, tipo_imagem):
        """Abre uma janela para exibir a imagem em tamanho completo"""
        if self.processamento_ativo: 
            return
            
        imagem_para_mostrar = None
        titulo = ""
        
        if tipo_imagem == 'original' and self.imagem_entrada_completa:
            imagem_para_mostrar = self.imagem_entrada_completa
            titulo = f"Original - {os.path.basename(self.caminho_arquivo_atual or '')}"
        elif tipo_imagem == 'resultado' and self.imagem_resultado_completa:
            imagem_para_mostrar = self.imagem_resultado_completa
            titulo = f"Resultado ({self.modelo_selecionado_var.get()}) - {os.path.basename(self.caminho_arquivo_atual or '')}"
        else:
            return
            
        try:
            # Criar a janela visualizadora
            VisualizadorImagem(self, imagem_para_mostrar, titulo)
        except Exception as e:
            messagebox.showerror("Erro de Visualização", 
                               f"Não foi possível exibir a imagem em tamanho real:\n{e}")
    
    def recortar_imagens_em_massa(self):
        """Permite recortar várias imagens com base em uma área de recorte definida em uma imagem modelo"""
        # Selecionar pasta de origem
        pasta_origem = filedialog.askdirectory(title="Selecione a Pasta com Imagens")
        if not pasta_origem:
            return
            
        # Selecionar imagem modelo
        modelo_caminho = filedialog.askopenfilename(
            title="Selecione a Imagem Modelo",
            filetypes=[("Arquivos de Imagem", " ".join(f"*{ext}" for ext in EXTENSOES_SUPORTADAS))]
        )
        
        if not modelo_caminho:
            return
            
        try:
            imagem_modelo = carregar_imagem(modelo_caminho)
            
            # Criar pasta de destino
            pasta_destino = os.path.join(pasta_origem, "recorte output")
            os.makedirs(pasta_destino, exist_ok=True)
            
            # Abre a janela de recorte
            JanelaRecorte(self, imagem_modelo, 
                        lambda imagem_recortada, caixa=None: self.iniciar_recorte_em_massa(pasta_origem, pasta_destino, caixa))
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir a imagem modelo:\n{e}")
    
    def iniciar_recorte_em_massa(self, pasta_origem, pasta_destino, caixa_recorte):
        """Inicia o processamento de recorte em massa"""
        total_arquivos = len([f for f in os.listdir(pasta_origem) 
                           if os.path.isfile(os.path.join(pasta_origem, f)) 
                           and f.lower().endswith(EXTENSOES_SUPORTADAS)])
        
        if total_arquivos == 0:
            messagebox.showinfo("Informação", "Nenhuma imagem compatível encontrada na pasta.")
            return
            
        # Preparar interface para processamento
        self.definir_interface_processando(True)
        self.barra_progresso.grid(row=1, column=0, padx=10, pady=(0,5), sticky="ew")
        self.barra_progresso.set(0)
        self.rotulo_status.configure(text=f"Iniciando recorte em massa: {total_arquivos} imagens...")
        self.update()
        
        def executar_recorte_massa():
            processados, total, erros = EditorImagem.recortar_em_massa(
                pasta_origem, pasta_destino, caixa_recorte
            )
            self.after(0, self.finalizar_recorte_massa, processados, total, erros)
            
        self.processamento_ativo = True
        threading.Thread(target=executar_recorte_massa, daemon=True).start()
    
    def finalizar_recorte_massa(self, processados, total, erros):
        """Finaliza o recorte em massa e exibe o resultado"""
        self.processamento_ativo = False
        self.definir_interface_processando(False)
        self.barra_progresso.grid_remove()
        self.barra_progresso.set(0)
        
        mensagem_final = f"Recorte em massa concluído.\n{processados}/{total} imagem(ns) processada(s) com sucesso."
        
        if erros:
            mensagem_final += f"\n\nOcorreram {len(erros)} erro(s):\n" + "\n".join(erros[:5])
            
            if len(erros) > 5:
                mensagem_final += "\n... (veja o console para mais detalhes)"
                
            messagebox.showwarning("Concluído com Erros", mensagem_final)
        else:
            messagebox.showinfo("Concluído", mensagem_final)
            
        self.rotulo_status.configure(text="Recorte em massa concluído.")
