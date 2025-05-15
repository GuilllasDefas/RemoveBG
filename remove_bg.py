import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel, Canvas, Scrollbar, StringVar, Menu  # Adicionado StringVar e Menu
from PIL import Image, ImageTk, ImageOps, ImageDraw
from rembg import remove, new_session # Importar new_session
import io
import os
import threading
import math

# --- Classe Helper para Tooltips ---
# --- Classe Helper para Tooltips (Refinada) ---
class ToolTip:
    """ Cria um Tooltip (dica flutuante) para um widget tkinter/customtkinter
        com atraso para mostrar e cancelamento ao sair.
    """
    def __init__(self, widget, text, delay_ms=500): # Atraso padrão de 500ms
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.tooltip_window = None
        self.show_job_id = None  # Para guardar o ID do 'after' job

        self.widget.bind("<Enter>", self.schedule_show_tooltip)
        self.widget.bind("<Leave>", self.cancel_and_hide_tooltip)
        self.widget.bind("<ButtonPress>", self.cancel_and_hide_tooltip) # Esconde se clicar

    def schedule_show_tooltip(self, event=None):
        """Agenda a exibição da tooltip após um atraso."""
        self.cancel_tooltip() # Cancela qualquer tooltip/agendamento anterior
        # Agenda a chamada para _show_tooltip_after_delay
        self.show_job_id = self.widget.after(self.delay_ms, self._show_tooltip_after_delay)

    def _show_tooltip_after_delay(self):
        """Cria e mostra a janela da tooltip (chamado via 'after')."""
        if self.tooltip_window: # Se já existir por algum motivo, destrói
            self.hide_tooltip_window()

        # Pega a posição atual do widget na tela
        x, y, _, _ = self.widget.bbox("insert") # Pega bbox relativo ao widget
        # Calcula posição absoluta na tela
        x += self.widget.winfo_rootx() + 20 # Offset x
        y += self.widget.winfo_rooty() + 20 # Offset y

        # Cria a Toplevel (janela flutuante)
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) # Sem bordas/título
        self.tooltip_window.wm_geometry(f"+{x}+{y}") # Posiciona
        self.tooltip_window.attributes("-topmost", True) # Fica no topo

        # Cria o Label dentro da Toplevel
        label = ctk.CTkLabel(self.tooltip_window, text=self.text,
                             fg_color=("gray85", "gray20"),
                             corner_radius=5,
                             padx=8, pady=4,
                             wraplength=250,
                             justify="left")
        label.pack()

        # Resetar o job ID, pois a tooltip foi mostrada
        self.show_job_id = None

    def cancel_and_hide_tooltip(self, event=None):
        """Cancela o agendamento (se houver) e esconde a tooltip (se visível)."""
        self.cancel_tooltip()
        self.hide_tooltip_window()

    def cancel_tooltip(self):
        """Cancela o agendamento da exibição da tooltip."""
        if self.show_job_id:
            self.widget.after_cancel(self.show_job_id)
            self.show_job_id = None

    def hide_tooltip_window(self):
        """Destroi a janela da tooltip se ela existir."""
        if self.tooltip_window:
            try:
                if self.tooltip_window.winfo_exists():
                    self.tooltip_window.destroy()
            except Exception as e:
                 # Pode dar erro se a janela já foi destruída ou durante o fechamento
                 # print(f"Pequeno erro ao destruir tooltip: {e}") # Opcional: para debug
                 pass
            finally:
                 self.tooltip_window = None

# --- Configuração do tema ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BackgroundRemoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Remover Fundo v0.8 - Beta")
        self.geometry("1150x850") # Ligeiramente mais largo para o novo menu
        self.resizable(True, True)

        # Modelos disponíveis no rembg (adicione outros se instalados)
        self.available_models = ["u2net", "u2netp", "u2net_human_seg", "silueta", "isnet-general-use", "isnet-anime"]
        # Variável para guardar o modelo selecionado
        self.selected_model_var = StringVar(value=self.available_models[0]) # Padrão: u2net

        # Sessão rembg reutilizável (será atualizada ao mudar modelo)
        self.rembg_session = new_session(self.selected_model_var.get())

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.about_button = ctk.CTkButton(self.header_frame, text="Sobre", command=self.show_about, width=80)
        self.about_button.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.header_label = ctk.CTkLabel(self.header_frame, text="Removedor de Fundos v0.8"
        " - Beta",
                                         font=ctk.CTkFont(size=36, weight="bold"))
        self.header_label.grid(row=0, column=1, padx=10, sticky="ew")

        # --- Menu Superior ---
        self.menu_bar = Menu(self)  # Use tkinter.Menu
        self.config(menu=self.menu_bar)

        # Menu Arquivo
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Selecionar Imagem", command=self.select_image)
        self.file_menu.add_command(label="Salvar Resultado", command=lambda: self.save_image())
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Sair", command=self.quit)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.file_menu)

        # Menu Ferramentas
        self.tools_menu = Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label="Processar Pasta", command=lambda: self.process_folder())
        self.tools_menu.add_command(label="Aplicar Ajustes", command=lambda: self.process_image())
        self.tools_menu.add_command(label="Cortar Imagem", command=lambda: self.open_crop_tool())
        self.tools_menu.add_command(label="Borracha", command=lambda: self.open_eraser_tool())
        self.tools_menu.add_command(label="Recorte em Massa", command=lambda: self.mass_crop_images())
        self.menu_bar.add_cascade(label="Ferramentas", menu=self.tools_menu)

        # Menu Ajuda
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Sobre", command=lambda: self.show_about())
        self.menu_bar.add_cascade(label="Ajuda", menu=self.help_menu)

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_columnconfigure(2, weight=0, minsize=220) # Coluna de controles um pouco maior
        self.main_frame.grid_rowconfigure(1, weight=1)

        # --- Coluna de Imagem Original ---
        self.original_frame = ctk.CTkFrame(self.main_frame)
        self.original_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.original_frame.grid_rowconfigure(1, weight=1)
        self.original_frame.grid_columnconfigure(0, weight=1)
        self.original_text = ctk.CTkLabel(self.original_frame, text="Imagem Original (Preview)")
        self.original_text.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        self.original_image_canvas = ctk.CTkCanvas(self.original_frame, bg=self.cget('bg'), highlightthickness=0)
        self.original_image_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.original_canvas_image_id = None
        self.view_original_button = ctk.CTkButton(self.original_frame, text="Ver Original", command=lambda: self.show_full_image('original'), state="disabled")
        self.view_original_button.grid(row=2, column=0, padx=10, pady=5, sticky="s")

        # --- Coluna de Imagem Resultante ---
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.result_frame.grid_rowconfigure(1, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_text = ctk.CTkLabel(self.result_frame, text="Resultado (Preview)")
        self.result_text.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        self.result_image_canvas = ctk.CTkCanvas(self.result_frame, bg=self.cget('bg'), highlightthickness=0)
        self.result_image_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.result_canvas_image_id = None
        self.view_result_button = ctk.CTkButton(self.result_frame, text="Ver Resultado", command=lambda: self.show_full_image('result'), state="disabled")
        self.view_result_button.grid(row=2, column=0, padx=10, pady=5, sticky="s")

        # --- Coluna de Controles de Ajuste Fino ---
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.grid(row=0, column=2, rowspan=2, padx=(5, 10), pady=10, sticky="ns")

        settings_title = ctk.CTkLabel(self.settings_frame, text="Ajustes e Modelo", font=ctk.CTkFont(weight="bold"))
        settings_title.pack(pady=(10, 15), padx=10)

        # --- Seleção de Modelo ---
        model_label = ctk.CTkLabel(self.settings_frame, text="Modelo de IA:")
        model_label.pack(pady=(5, 0), padx=10, anchor="w")
        self.model_optionmenu = ctk.CTkOptionMenu(self.settings_frame,
                                                  variable=self.selected_model_var,
                                                  values=self.available_models,
                                                  command=self.on_model_change) # Chama a função ao mudar
        self.model_optionmenu.pack(pady=(0, 10), padx=10, fill="x")
        ToolTip(model_label, "Escolha o modelo de Inteligência Artificial para remover o fundo.\n"
                            "- u2net: Padrão, bom para uso geral.\n"
                            "- u2netp: Mais rápido, qualidade pode variar.\n"
                            "- u2net_human_seg: Otimizado para pessoas.\n"
                            "- silueta: Alternativa geral.\n"
                            "- isnet-*: Modelos mais recentes, boa qualidade (podem ser mais lentos).\n"
                            "Experimente modelos diferentes para melhores resultados!")
        ToolTip(self.model_optionmenu, "Escolha o modelo de IA (veja dica acima).")

        # --- Controles Alpha Matting ---
        self.alpha_matting_var = ctk.BooleanVar(value=True)
        self.alpha_matting_check = ctk.CTkCheckBox(self.settings_frame, text="Alpha Matting", variable=self.alpha_matting_var, command=self.on_settings_change)
        self.alpha_matting_check.pack(pady=5, padx=10, anchor="w")
        ToolTip(self.alpha_matting_check, "Técnica adicional para refinar bordas suaves (como cabelo ou pelos).\n"
                                        "Pode aumentar o tempo de processamento.\n"
                                        "Desative se o resultado parecer estranho ou muito lento.")

        # --- Limiar Objeto ---
        fg_label = ctk.CTkLabel(self.settings_frame, text="Limiar Objeto (0-255)")
        fg_label.pack(pady=(10, 0), padx=10, anchor="w")
        self.fg_thresh_var = ctk.IntVar(value=240)
        self.fg_thresh_slider = ctk.CTkSlider(self.settings_frame, from_=0, to=255, number_of_steps=255, variable=self.fg_thresh_var, command=lambda v: self.update_slider_label(v, self.fg_thresh_label, "Limiar Objeto"))
        self.fg_thresh_slider.pack(pady=5, padx=10, fill="x")
        self.fg_thresh_label = ctk.CTkLabel(self.settings_frame, text=f"Limiar Objeto: {self.fg_thresh_var.get()}")
        self.fg_thresh_label.pack(pady=(0,10), padx=10, anchor="w")
        ToolTip(fg_label, "Define o quão 'opaco' um pixel precisa ser para ser considerado parte do objeto principal.\n"
                         "Valores MAIORES: Tende a incluir mais áreas semi-transparentes no objeto.\n"
                         "Valores MENORES: Tende a tornar as bordas do objeto mais 'duras' e definidas.\n"
                         "(Funciona melhor com Alpha Matting ativado)")
        ToolTip(self.fg_thresh_slider, "Ajuste o limiar do objeto (veja dica acima).")

        # --- Limiar Fundo ---
        bg_label = ctk.CTkLabel(self.settings_frame, text="Limiar Fundo (0-255)")
        bg_label.pack(pady=(10, 0), padx=10, anchor="w")
        self.bg_thresh_var = ctk.IntVar(value=10)
        self.bg_thresh_slider = ctk.CTkSlider(self.settings_frame, from_=0, to=255, number_of_steps=255, variable=self.bg_thresh_var, command=lambda v: self.update_slider_label(v, self.bg_thresh_label, "Limiar Fundo"))
        self.bg_thresh_slider.pack(pady=5, padx=10, fill="x")
        self.bg_thresh_label = ctk.CTkLabel(self.settings_frame, text=f"Limiar Fundo: {self.bg_thresh_var.get()}")
        self.bg_thresh_label.pack(pady=(0,10), padx=10, anchor="w")
        ToolTip(bg_label, "Define o quão 'transparente' um pixel precisa ser para ser considerado parte do fundo.\n"
                       "Valores MAIORES: Tende a remover mais áreas, potencialmente 'comendo' bordas do objeto.\n"
                       "Valores MENORES: Tende a preservar mais detalhes nas bordas, mas pode deixar 'fantasmas' do fundo.\n"
                       "(Funciona melhor com Alpha Matting ativado)")
        ToolTip(self.bg_thresh_slider, "Ajuste o limiar do fundo (veja dica acima).")

        # --- Erosão Máscara ---
        erode_label = ctk.CTkLabel(self.settings_frame, text="Erosão Máscara (0-50)")
        erode_label.pack(pady=(10, 0), padx=10, anchor="w")
        self.erode_size_var = ctk.IntVar(value=10)
        self.erode_size_slider = ctk.CTkSlider(self.settings_frame, from_=0, to=50, number_of_steps=50, variable=self.erode_size_var, command=lambda v: self.update_slider_label(v, self.erode_size_label, "Erosão Máscara"))
        self.erode_size_slider.pack(pady=5, padx=10, fill="x")
        self.erode_size_label = ctk.CTkLabel(self.settings_frame, text=f"Erosão Máscara: {self.erode_size_var.get()}")
        self.erode_size_label.pack(pady=(0,10), padx=10, anchor="w")
        ToolTip(erode_label, "Reduz o tamanho da máscara final (recorte) em alguns pixels.\n"
                          "Útil para remover pequenas bordas ou 'halos' que sobraram do fundo.\n"
                          "Valores maiores 'encolhem' mais o objeto principal.\n"
                          "(Funciona melhor com Alpha Matting ativado)")
        ToolTip(self.erode_size_slider, "Ajuste a erosão da máscara (veja dica acima).")

        # --- Botão Restaurar Padrões ---
        self.restore_defaults_button = ctk.CTkButton(self.settings_frame, text="Restaurar Padrões", command=self.reset_defaults)
        self.restore_defaults_button.pack(pady=5, padx=10, fill="x")  # Botão restaurado aqui
        ToolTip(self.restore_defaults_button, "Restaura os valores para configurações recomendadas.")

        # --- Barra de Status e Progresso ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(self.status_frame, text="Pronto", anchor="w")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, orientation="horizontal", mode="determinate")
        self.progress_bar.set(0)

        # --- Variáveis de Estado ---
        self.full_input_image = None
        self.full_result_image = None
        self.tk_input_preview = None
        self.tk_result_preview = None
        self.current_file_path = None
        self.processing_active = False

        # Bind para redimensionar previews
        self.original_image_canvas.bind("<Configure>", self.resize_previews)
        self.result_image_canvas.bind("<Configure>", self.resize_previews)

        # Inicializa as configurações padrão
        self.reset_defaults()

        # Atualizar estados dos menus (mover para o final do __init__)
        self.update_menu_states()

    def update_menu_states(self):
        """Atualiza os estados dos itens do menu com base no estado atual da aplicação."""
        self.file_menu.entryconfig(1, state="normal" if self.full_result_image else "disabled")  # "Salvar Resultado"
        self.tools_menu.entryconfig(1, state="normal" if self.full_input_image else "disabled")  # "Aplicar Ajustes"
        self.tools_menu.entryconfig(2, state="normal" if self.full_input_image else "disabled")  # "Cortar Imagem"
        self.tools_menu.entryconfig(3, state="normal" if self.full_input_image else "disabled")  # "Borracha"

    def show_about(self):
        info_text = ("Remover Fundo v0.7.1\n\n"
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
        messagebox.showinfo("Sobre", info_text)

    def on_model_change(self, selected_model):
        """Chamado quando o usuário seleciona um novo modelo."""
        print(f"Modelo selecionado: {selected_model}")
        try:
            # Cria uma nova sessão para o modelo selecionado
            self.rembg_session = new_session(selected_model)
            print("Sessão rembg atualizada.")
            # Habilita o botão de reprocessar se uma imagem estiver carregada
            self.on_settings_change()
        except Exception as e:
            messagebox.showerror("Erro de Modelo", f"Não foi possível carregar o modelo '{selected_model}':\n{e}\n\nVerifique se o rembg e suas dependências estão instalados corretamente ou se o modelo é válido.")
            self.selected_model_var.set(self.available_models[0]) # Volta ao padrão
            self.rembg_session = new_session(self.available_models[0])

    def update_slider_label(self, value, label_widget, prefix):
        """Atualiza o texto do label de um slider e habilita reprocessamento."""
        label_widget.configure(text=f"{prefix}: {int(value)}")
        self.on_settings_change() # Qualquer mudança nos sliders deve permitir reprocessar

    def on_settings_change(self, *args):
        """Chamado quando qualquer controle de ajuste (slider, checkbox, modelo) muda."""
        if self.full_input_image and not self.processing_active:
             self.update_menu_states()

    def select_image(self):
        if self.processing_active:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return
        file_path = filedialog.askopenfilename(title="Selecione a Imagem",
                                               filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]) # Adicionado webp
        if file_path:
            try:
                self.status_label.configure(text="Carregando imagem...")
                self.update()

                image = Image.open(file_path)
                image = ImageOps.exif_transpose(image)
                if image.mode != "RGBA":
                    image = image.convert("RGBA")

                self.full_input_image = image
                self.current_file_path = file_path
                self.full_result_image = None

                if self.original_canvas_image_id:
                    self.original_image_canvas.delete(self.original_canvas_image_id)
                if self.result_canvas_image_id:
                    self.result_image_canvas.delete(self.result_canvas_image_id)
                    self.result_canvas_image_id = None

                self.display_image_on_canvas(self.original_image_canvas, self.full_input_image, 'input')

                self.view_original_button.configure(state="normal")
                self.view_result_button.configure(state="disabled")
                self.status_label.configure(text=f"Imagem carregada: {os.path.basename(file_path)}")
                self.update_menu_states()

            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao abrir a imagem:\n{e}")
                self.status_label.configure(text="Erro ao carregar imagem!")
                self.reset_ui_state()

    def resize_previews(self, event=None):
        if self.winfo_exists(): # Evita erro se a janela for fechada durante o processo
            if self.full_input_image:
                self.display_image_on_canvas(self.original_image_canvas, self.full_input_image, 'input')
            if self.full_result_image:
                self.display_image_on_canvas(self.result_image_canvas, self.full_result_image, 'result')

    def display_image_on_canvas(self, canvas, pil_image, image_type):
        try:
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                if self.winfo_exists():
                    self.after(50, lambda: self.display_image_on_canvas(canvas, pil_image, image_type))
                return

            preview_image = self.create_preview(pil_image, canvas_width, canvas_height)
            tk_image = ImageTk.PhotoImage(preview_image)

            if image_type == 'input':
                self.tk_input_preview = tk_image
                if self.original_canvas_image_id:
                    canvas.delete(self.original_canvas_image_id)
                self.original_canvas_image_id = canvas.create_image(canvas_width / 2, canvas_height / 2, anchor='center', image=tk_image)

            elif image_type == 'result':
                self.tk_result_preview = tk_image
                if self.result_canvas_image_id:
                    canvas.delete(self.result_canvas_image_id)
                self.result_canvas_image_id = canvas.create_image(canvas_width / 2, canvas_height / 2, anchor='center', image=tk_image)

        except Exception as e:
             print(f"Erro ao exibir imagem no canvas ({image_type}): {e}")

    def open_crop_tool(self):
        """Abre uma janela para recortar a imagem original."""
        if not self.full_input_image:
            messagebox.showwarning("Atenção", "Nenhuma imagem carregada para recorte!")
            return

        crop_top = ctk.CTkToplevel(self)
        crop_top.title("Ferramenta de Recorte")
        crop_top.geometry("800x600")
        crop_top.grab_set()

        # Canvas com suporte a scroll
        canvas_frame = ctk.CTkFrame(crop_top)
        canvas_frame.pack(fill="both", expand=True)

        canvas = Canvas(canvas_frame, bg='white', scrollregion=(0, 0, self.full_input_image.width, self.full_input_image.height))
        canvas.grid(row=0, column=0, sticky="nsew")

        h_scroll = Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")

        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Configuração do layout do frame
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Exibe a imagem no canvas
        tk_image = ImageTk.PhotoImage(self.full_input_image)
        canvas.create_image(0, 0, anchor='nw', image=tk_image)
        canvas.image = tk_image

        # Variáveis para armazenar posição e retângulo de seleção
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect = None
        current_zoom = 1.0  # Zoom inicial

        def on_mouse_down(event):
            self.crop_start_x = canvas.canvasx(event.x)
            self.crop_start_y = canvas.canvasy(event.y)
            if self.crop_rect:
                canvas.delete(self.crop_rect)
            self.crop_rect = canvas.create_rectangle(self.crop_start_x, self.crop_start_y,
                                                     self.crop_start_x, self.crop_start_y,
                                                     outline="red", width=2)

        def on_mouse_move(event):
            if self.crop_rect:
                curX, curY = canvas.canvasx(event.x), canvas.canvasy(event.y)
                canvas.coords(self.crop_rect, self.crop_start_x, self.crop_start_y, curX, curY)

        def on_crop_confirm():
            if self.crop_rect:
                x1, y1, x2, y2 = map(int, canvas.coords(self.crop_rect))
                if x2 - x1 > 0 and y2 - y1 > 0:
                    x1 = int(x1 / current_zoom)
                    y1 = int(y1 / current_zoom)
                    x2 = int(x2 / current_zoom)
                    y2 = int(y2 / current_zoom)
                    cropped = self.full_input_image.crop((x1, y1, x2, y2))
                    self.full_input_image = cropped
                    self.display_image_on_canvas(self.original_image_canvas, self.full_input_image, 'input')
                    self.update_menu_states()
            crop_top.destroy()

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)

        def zoom(factor):
            nonlocal current_zoom, tk_image
            new_zoom = current_zoom * factor
            if new_zoom < 0.1 or new_zoom > 10.0:
                return
            current_zoom = new_zoom
            width = int(self.full_input_image.width * current_zoom)
            height = int(self.full_input_image.height * current_zoom)
            resized_image = self.full_input_image.resize((width, height), Image.Resampling.NEAREST)
            tk_image = ImageTk.PhotoImage(resized_image)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor='nw', image=tk_image)
            canvas.image = tk_image
            canvas.config(scrollregion=(0, 0, width, height))

        canvas.bind("<MouseWheel>", lambda event: zoom(1.1 if event.delta > 0 else 0.9))

        zoom_frame = ctk.CTkFrame(crop_top)
        zoom_frame.pack(pady=5)

        zoom_in_btn = ctk.CTkButton(zoom_frame, text="Zoom +", command=lambda: zoom(1.2))
        zoom_in_btn.pack(side="left", padx=5)
        zoom_out_btn = ctk.CTkButton(zoom_frame, text="Zoom -", command=lambda: zoom(0.8))
        zoom_out_btn.pack(side="left", padx=5)
        zoom_reset_btn = ctk.CTkButton(zoom_frame, text="Reset", command=lambda: zoom(1.0 / current_zoom))
        zoom_reset_btn.pack(side="left", padx=5)

        btn_frame = ctk.CTkFrame(crop_top)
        btn_frame.pack(pady=5)
        confirm_btn = ctk.CTkButton(btn_frame, text="Recortar", command=on_crop_confirm)
        confirm_btn.pack(side="left", padx=10)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=crop_top.destroy)
        cancel_btn.pack(side="left", padx=10)

    def open_eraser_tool(self):
        """Abre uma janela para apagar áreas da imagem com uma borracha."""
        if not self.full_input_image:
            messagebox.showwarning("Atenção", "Nenhuma imagem carregada para edição!")
            return

        eraser_top = ctk.CTkToplevel(self)
        eraser_top.title("Ferramenta de Borracha")
        eraser_top.geometry("800x600")
        eraser_top.grab_set()

        canvas_frame = ctk.CTkFrame(eraser_top)
        canvas_frame.pack(fill="both", expand=True)

        canvas = Canvas(canvas_frame, bg='white', scrollregion=(0, 0, self.full_input_image.width, self.full_input_image.height))
        canvas.grid(row=0, column=0, sticky="nsew")

        h_scroll = Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")

        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        editable_image = self.full_input_image.copy()
        tk_image = ImageTk.PhotoImage(editable_image)
        canvas_image = canvas.create_image(0, 0, anchor='nw', image=tk_image)
        canvas.image = tk_image

        brush_size = [20]  # Usamos uma lista para permitir mutabilidade
        current_zoom = 1.0
        cursor_circle = None  # Referência ao círculo que representa a borracha

        def erase(event):
            """Apaga a área onde o mouse é clicado ou arrastado, deixando-a transparente."""
            x = int(canvas.canvasx(event.x) / current_zoom)
            y = int(canvas.canvasy(event.y) / current_zoom)
            draw = ImageDraw.Draw(editable_image)
            draw.ellipse((x - brush_size[0], y - brush_size[0], x + brush_size[0], y + brush_size[0]), fill=(0, 0, 0, 0))
            update_canvas()

        def update_canvas():
            """Atualiza a imagem exibida no canvas."""
            resized_image = editable_image.resize(
                (int(editable_image.width * current_zoom), int(editable_image.height * current_zoom)),
                Image.Resampling.NEAREST
            )
            tk_resized_image = ImageTk.PhotoImage(resized_image)
            canvas.itemconfig(canvas_image, image=tk_resized_image)
            canvas.image = tk_resized_image

        def zoom(factor):
            """Aplica zoom na imagem."""
            nonlocal current_zoom
            new_zoom = current_zoom * factor
            if 0.1 <= new_zoom <= 10.0:
                current_zoom = new_zoom
                update_canvas()

        def save_changes():
            """Salva as alterações feitas na imagem original."""
            self.full_input_image = editable_image
            self.display_image_on_canvas(self.original_image_canvas, self.full_input_image, 'input')
            self.update_menu_states()
            eraser_top.destroy()

        def update_brush_size(value):
            """Atualiza o tamanho da borracha com base no slider."""
            brush_size[0] = int(value)

        def show_cursor(event):
            """Exibe o cursor da borracha no canvas."""
            nonlocal cursor_circle
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            if cursor_circle:
                canvas.delete(cursor_circle)
            cursor_circle = canvas.create_oval(
                x - brush_size[0] * current_zoom, y - brush_size[0] * current_zoom,
                x + brush_size[0] * current_zoom, y + brush_size[0] * current_zoom,
                outline="red", width=2, fill="gray", stipple="gray50"
            )

        def hide_cursor(event):
            """Remove o cursor da borracha ao sair do canvas."""
            nonlocal cursor_circle
            if cursor_circle:
                canvas.delete(cursor_circle)
                cursor_circle = None

        canvas.bind("<B1-Motion>", erase)
        canvas.bind("<ButtonPress-1>", erase)
        canvas.bind("<Motion>", show_cursor)
        canvas.bind("<Leave>", hide_cursor)
        canvas.bind("<MouseWheel>", lambda event: zoom(1.1 if event.delta > 0 else 0.9))

        controls_frame = ctk.CTkFrame(eraser_top)
        controls_frame.pack(pady=5)

        ctk.CTkLabel(controls_frame, text="Tamanho da Borracha:").pack(side="left", padx=5)
        brush_size_slider = ctk.CTkSlider(controls_frame, from_=5, to=100, number_of_steps=95, command=update_brush_size)
        brush_size_slider.set(brush_size[0])
        brush_size_slider.pack(side="left", padx=5)

        zoom_in_btn = ctk.CTkButton(controls_frame, text="Zoom +", command=lambda: zoom(1.2))
        zoom_in_btn.pack(side="left", padx=5)
        zoom_out_btn = ctk.CTkButton(controls_frame, text="Zoom -", command=lambda: zoom(0.8))
        zoom_out_btn.pack(side="left", padx=5)
        save_btn = ctk.CTkButton(controls_frame, text="Salvar Alterações", command=save_changes)
        save_btn.pack(side="left", padx=5)
        cancel_btn = ctk.CTkButton(controls_frame, text="Cancelar", command=eraser_top.destroy)
        cancel_btn.pack(side="left", padx=5)

    def create_preview(self, image, max_width, max_height):
        img_w, img_h = image.size
        if img_w == 0 or img_h == 0 or max_width <= 0 or max_height <= 0: return Image.new('RGBA', (1, 1), (0,0,0,0))

        ratio = min(max_width / img_w, max_height / img_h)
        if ratio < 1.0:
            new_size = (max(1, int(img_w * ratio)), max(1, int(img_h * ratio)))
            try:
                return image.resize(new_size, Image.Resampling.LANCZOS)
            except Exception as e:
                 print(f"Erro ao redimensionar preview: {e}")
                 return image
        return image

    def process_image(self):
        if not self.full_input_image:
            messagebox.showwarning("Atenção", "Selecione uma imagem primeiro!")
            return
        if self.processing_active:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return

        current_session = self.rembg_session

        def process():
            self.processing_active = True
            self.set_ui_processing(True)
            self.after(0, lambda: self.status_label.configure(text=f"Processando com modelo '{self.selected_model_var.get()}'..."))
            self.after(0, self.update)

            try:
                buf = io.BytesIO()
                self.full_input_image.save(buf, format="PNG")
                img_bytes = buf.getvalue()

                use_alpha_matting = self.alpha_matting_var.get()
                fg_threshold = self.fg_thresh_var.get()
                bg_threshold = self.bg_thresh_var.get()
                erode_size = self.erode_size_var.get()

                result_bytes = remove(
                    img_bytes,
                    session=current_session,
                    alpha_matting=use_alpha_matting,
                    alpha_matting_foreground_threshold=fg_threshold,
                    alpha_matting_background_threshold=bg_threshold,
                    alpha_matting_erode_size=erode_size
                )

                result_image = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
                self.full_result_image = result_image

                self.after(0, self.update_ui_after_processing)

            except Exception as e:
                error_message = f"Falha ao remover o fundo:\n{e}"
                self.after(0, lambda: messagebox.showerror("Erro de Processamento", error_message))
                self.after(0, lambda: self.status_label.configure(text="Erro no processamento!"))
            finally:
                self.processing_active = False
                self.after(0, lambda: self.set_ui_processing(False))

        threading.Thread(target=process, daemon=True).start()

    def update_ui_after_processing(self):
        if self.full_result_image:
            self.display_image_on_canvas(self.result_image_canvas, self.full_result_image, 'result')
            self.status_label.configure(text="Processamento concluído!")
        else:
             self.status_label.configure(text="Falha ao gerar resultado.")
        self.update_menu_states()

    def set_ui_processing(self, is_processing):
        """Atualiza o estado da interface durante o processamento."""
        state = "disabled" if is_processing else "normal"
        self.menu_bar.entryconfig("Arquivo", state=state)
        self.menu_bar.entryconfig("Ferramentas", state=state)
        self.menu_bar.entryconfig("Ajuda", state=state)

    def reset_ui_state(self):
         self.full_input_image = None
         self.full_result_image = None
         self.current_file_path = None
         if self.original_canvas_image_id:
             self.original_image_canvas.delete(self.original_canvas_image_id)
             self.original_canvas_image_id = None
         if self.result_canvas_image_id:
             self.result_image_canvas.delete(self.result_canvas_image_id)
             self.result_canvas_image_id = None
         self.tk_input_preview = None
         self.tk_result_preview = None
         self.set_ui_processing(False)
         self.status_label.configure(text="Pronto")
         self.update_menu_states()

    def save_image(self):
        """Salva a imagem processada ou a imagem editada pela ferramenta de borracha."""
        if self.full_result_image:
            image_to_save = self.full_result_image
        elif self.full_input_image:
            image_to_save = self.full_input_image
        else:
            messagebox.showwarning("Atenção", "Não há imagem processada ou editada para salvar!")
            return

        if self.processing_active:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return

        original_filename = os.path.basename(self.current_file_path or "imagem")
        name, _ = os.path.splitext(original_filename)
        default_filename = f"{name}_editado.png"

        file_path = filedialog.asksaveasfilename(title="Salvar Imagem",
                                                 initialfile=default_filename,
                                                 defaultextension=".png",
                                                 filetypes=[("PNG Files", "*.png")])
        if file_path:
            try:
                self.status_label.configure(text="Salvando imagem...")
                self.update()
                image_to_save.save(file_path)
                self.status_label.configure(text="Imagem salva com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar a imagem:\n{e}")
                self.status_label.configure(text="Erro ao salvar!")

    def reset_defaults(self):
        default_model = "isnet-general-use"
        self.selected_model_var.set(default_model)
        self.model_optionmenu.set(default_model)
        try:
            self.rembg_session = new_session(default_model)
            print("Sessão rembg restaurada para o padrão:", default_model)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao restaurar o modelo padrão:\n{e}")
    
        self.alpha_matting_var.set(True)
        self.fg_thresh_var.set(250)
        self.bg_thresh_var.set(10)
        self.erode_size_var.set(5)
    
        self.fg_thresh_label.configure(text=f"Limiar Objeto: {self.fg_thresh_var.get()}")
        self.bg_thresh_label.configure(text=f"Limiar Fundo: {self.bg_thresh_var.get()}")
        self.erode_size_label.configure(text=f"Erosão Máscara: {self.erode_size_var.get()}")
    
        if self.full_input_image and not self.processing_active:
            self.update_menu_states()
    
        self.status_label.configure(text="Valores restaurados para os padrões.")

    def process_folder(self):
        if self.processing_active:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual terminar.")
            return

        folder_path = filedialog.askdirectory(title="Selecione a Pasta com Imagens")
        if not folder_path: return
        output_folder = filedialog.askdirectory(title="Selecione a Pasta de Destino")
        if not output_folder: return
        if folder_path == output_folder:
             messagebox.showerror("Erro", "A pasta de origem e destino não podem ser a mesma.")
             return

        supported_ext = ('.png', '.jpg', '.jpeg', '.webp')
        try:
            all_files = os.listdir(folder_path)
        except FileNotFoundError:
             messagebox.showerror("Erro", f"Pasta de origem não encontrada:\n{folder_path}")
             return
        except Exception as e:
             messagebox.showerror("Erro", f"Não foi possível listar arquivos na pasta de origem:\n{e}")
             return

        image_files = [f for f in all_files
                       if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(supported_ext)]

        if not image_files:
            messagebox.showinfo("Informação", "Nenhuma imagem compatível encontrada na pasta selecionada.")
            return

        total_files = len(image_files)

        current_session = self.rembg_session
        use_alpha_matting = self.alpha_matting_var.get()
        fg_threshold = self.fg_thresh_var.get()
        bg_threshold = self.bg_thresh_var.get()
        erode_size = self.erode_size_var.get()
        selected_model_name = self.selected_model_var.get()

        self.set_ui_processing(True)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0,5), sticky="ew")
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Iniciando lote ({selected_model_name}): {total_files} imagens...")
        self.update()

        def process_batch():
            processed_count = 0
            errors = []

            for i, filename in enumerate(image_files):
                input_path = os.path.join(folder_path, filename)
                output_filename = f"{os.path.splitext(filename)[0]}_{selected_model_name}_no_bg.png"
                output_path = os.path.join(output_folder, output_filename)

                progress = (i + 1) / total_files
                status_text = f"Lote ({selected_model_name}) {i+1}/{total_files}: {filename}"
                self.after(0, self.update_batch_progress, progress, status_text)

                try:
                    with Image.open(input_path) as img:
                        img = ImageOps.exif_transpose(img)
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        self.full_input_image = img
                        self.after(0, lambda: self.display_image_on_canvas(self.original_image_canvas, img, 'input'))

                    with open(input_path, 'rb') as f_in:
                        img_bytes = f_in.read()

                    result_bytes = remove(
                        img_bytes,
                        session=current_session,
                        alpha_matting=use_alpha_matting,
                        alpha_matting_foreground_threshold=fg_threshold,
                        alpha_matting_background_threshold=bg_threshold,
                        alpha_matting_erode_size=erode_size
                    )

                    result_image = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
                    self.full_result_image = result_image
                    self.after(0, lambda: self.display_image_on_canvas(self.result_image_canvas, result_image, 'result'))

                    with open(output_path, 'wb') as f_out:
                        f_out.write(result_bytes)

                    processed_count += 1
                except Exception as e:
                    errors.append(f"'{filename}': {e}")
                    print(f"Erro ao processar {filename}: {e}")

            self.after(0, self.finalize_batch_processing, processed_count, total_files, errors, selected_model_name)

        self.processing_active = True
        threading.Thread(target=process_batch, daemon=True).start()

    def update_batch_progress(self, progress_value, status_text):
        if self.winfo_exists():
            self.progress_bar.set(progress_value)
            self.status_label.configure(text=status_text)

    def finalize_batch_processing(self, processed_count, total_files, errors, model_name):
        if not self.winfo_exists(): return

        self.processing_active = False
        self.set_ui_processing(False)
        self.progress_bar.grid_remove()
        self.progress_bar.set(0)

        final_message = f"Processamento em lote ({model_name}) concluído.\n"
        final_message += f"{processed_count}/{total_files} imagem(ns) processada(s) com sucesso!"

        status_text = f"Lote ({model_name}) finalizado: {processed_count} sucesso(s), {len(errors)} erro(s)."

        if errors:
            final_message += f"\n\nOcorreram {len(errors)} erro(s):\n"
            final_message += "\n".join(f"- {err}" for err in errors[:5])
            if len(errors) > 5:
                final_message += "\n- ... (veja o console/log para mais detalhes)"
            messagebox.showwarning("Lote Concluído com Erros", final_message)
        else:
            messagebox.showinfo("Lote Concluído", final_message)

        self.status_label.configure(text=status_text)

    def show_full_image(self, image_type):
        if self.processing_active: return

        image_to_show = None
        title = ""
        if image_type == 'original' and self.full_input_image:
            image_to_show = self.full_input_image
            title = f"Original - {os.path.basename(self.current_file_path or '')}"
        elif image_type == 'result' and self.full_result_image:
            image_to_show = self.full_result_image
            title = f"Resultado ({self.selected_model_var.get()}) - {os.path.basename(self.current_file_path or '')}"
        else:
            return

        try:
            top = ctk.CTkToplevel(self)
            top.title(title)
            top.geometry("800x600")
            top.grab_set()

            frame = ctk.CTkFrame(top)
            frame.pack(fill="both", expand=True)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            canvas = Canvas(frame, bd=0, highlightthickness=0, background=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"]))

            v_scroll = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
            h_scroll = ctk.CTkScrollbar(frame, orientation="horizontal", command=canvas.xview)
            v_scroll.grid(row=0, column=1, sticky="ns")
            h_scroll.grid(row=1, column=0, sticky="ew")

            canvas.grid(row=0, column=0, sticky="nsew")
            canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

            full_tk_image = ImageTk.PhotoImage(image_to_show)
            canvas.create_image(0, 0, anchor='nw', image=full_tk_image)
            canvas.image = full_tk_image
            canvas.config(scrollregion=canvas.bbox("all"))

            zoom_frame = ctk.CTkFrame(top)
            zoom_frame.pack(pady=5)
            current_zoom = 1.0

            def zoom(factor):
                nonlocal current_zoom, full_tk_image, image_to_show
                new_zoom = current_zoom * factor
                if new_zoom < 0.1 or new_zoom > 10.0:
                    return

                current_zoom = new_zoom
                width = int(image_to_show.width * current_zoom)
                height = int(image_to_show.height * current_zoom)

                if width < 1 or height < 1:
                     current_zoom /= factor
                     return

                try:
                    resample_method = Image.Resampling.NEAREST if factor != 1.0 else Image.Resampling.LANCZOS
                    resized_img = image_to_show.resize((width, height), resample_method)
                    full_tk_image = ImageTk.PhotoImage(resized_img)
                    canvas.delete("all")
                    canvas.create_image(0, 0, anchor='nw', image=full_tk_image)
                    canvas.image = full_tk_image
                    canvas.config(scrollregion=canvas.bbox("all"))
                    zoom_label.configure(text=f"Zoom: {current_zoom:.1f}x")
                except Exception as e:
                     print(f"Erro no zoom: {e}")

            zoom_in_btn = ctk.CTkButton(zoom_frame, text="+", width=40, command=lambda: zoom(1.2))
            zoom_in_btn.pack(side="left", padx=5)
            zoom_out_btn = ctk.CTkButton(zoom_frame, text="-", width=40, command=lambda: zoom(0.8))
            zoom_out_btn.pack(side="left", padx=5)
            zoom_reset_btn = ctk.CTkButton(zoom_frame, text="1:1", width=40, command=lambda: zoom(1.0/current_zoom))
            zoom_reset_btn.pack(side="left", padx=5)
            zoom_label = ctk.CTkLabel(zoom_frame, text=f"Zoom: {current_zoom:.1f}x")
            zoom_label.pack(side="left", padx=5)

            canvas.bind("<MouseWheel>", lambda event: zoom(1.1 if event.delta > 0 else 0.9))
            canvas.bind("<Button-4>", lambda event: zoom(1.1))
            canvas.bind("<Button-5>", lambda event: zoom(0.9))

            canvas.bind("<ButtonPress-2>", lambda event: canvas.scan_mark(event.x, event.y))
            canvas.bind("<B2-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))

            top.after(100, lambda: canvas.focus_set())

        except Exception as e:
            messagebox.showerror("Erro de Visualização", f"Não foi possível exibir a imagem em tamanho real:\n{e}")

    def mass_crop_images(self):
        """Permite recortar várias imagens com base em uma área de recorte definida em uma imagem modelo."""
        folder_path = filedialog.askdirectory(title="Selecione a Pasta com Imagens")
        if not folder_path:
            return

        # Selecionar imagem modelo
        model_image_path = filedialog.askopenfilename(title="Selecione a Imagem Modelo",
                                                       filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")])
        if not model_image_path:
            return

        try:
            model_image = Image.open(model_image_path)
            model_image = ImageOps.exif_transpose(model_image)
            if model_image.mode != "RGBA":
                model_image = model_image.convert("RGBA")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir a imagem modelo:\n{e}")
            return

        # Abrir ferramenta de recorte para definir a área
        crop_top = ctk.CTkToplevel(self)
        crop_top.title("Definir Área de Recorte")
        crop_top.geometry("800x600")
        crop_top.grab_set()

        canvas = Canvas(crop_top, bg='white', scrollregion=(0, 0, model_image.width, model_image.height))
        canvas.pack(fill="both", expand=True)

        tk_image = ImageTk.PhotoImage(model_image)
        canvas.create_image(0, 0, anchor='nw', image=tk_image)
        canvas.image = tk_image

        crop_start_x = crop_start_y = crop_rect = None

        def on_mouse_down(event):
            nonlocal crop_start_x, crop_start_y, crop_rect
            crop_start_x, crop_start_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
            if crop_rect:
                canvas.delete(crop_rect)
            crop_rect = canvas.create_rectangle(crop_start_x, crop_start_y, crop_start_x, crop_start_y, outline="red", width=2)

        def on_mouse_move(event):
            if crop_rect:
                cur_x, cur_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
                canvas.coords(crop_rect, crop_start_x, crop_start_y, cur_x, cur_y)

        def on_crop_confirm():
            if crop_rect:
                x1, y1, x2, y2 = map(int, canvas.coords(crop_rect))
                if x2 - x1 > 0 and y2 - y1 > 0:
                    crop_top.destroy()
                    self.apply_crop_to_folder(folder_path, (x1, y1, x2, y2))

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)

        confirm_btn = ctk.CTkButton(crop_top, text="Confirmar Recorte", command=on_crop_confirm)
        confirm_btn.pack(pady=10)

    def apply_crop_to_folder(self, folder_path, crop_box):
        """Aplica o recorte definido a todas as imagens da pasta com indicador de progresso."""
        output_folder = os.path.join(folder_path, "crop output")
        os.makedirs(output_folder, exist_ok=True)

        supported_ext = ('.png', '.jpg', '.jpeg', '.webp')
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(supported_ext)]

        if not image_files:
            messagebox.showinfo("Informação", "Nenhuma imagem compatível encontrada na pasta selecionada.")
            return

        total_files = len(image_files)
        processed_count = 0
        errors = []

        self.set_ui_processing(True)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Iniciando recorte em massa: {total_files} imagens...")
        self.update()

        def process_crops():
            nonlocal processed_count
            for i, filename in enumerate(image_files):
                input_path = os.path.join(folder_path, filename)
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}-crop.png")

                progress = (i + 1) / total_files
                status_text = f"Recorte em massa {i + 1}/{total_files}: {filename}"
                self.after(0, self.update_batch_progress, progress, status_text)

                try:
                    with Image.open(input_path) as img:
                        img = ImageOps.exif_transpose(img)
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        cropped_img = img.crop(crop_box)
                        cropped_img.save(output_path)
                        processed_count += 1
                except Exception as e:
                    errors.append(f"{filename}: {e}")

            self.after(0, self.finalize_crop_processing, processed_count, total_files, errors)

        threading.Thread(target=process_crops, daemon=True).start()

    def finalize_crop_processing(self, processed_count, total_files, errors):
        """Finaliza o recorte em massa e exibe o resultado."""
        self.processing_active = False
        self.set_ui_processing(False)
        self.progress_bar.grid_remove()
        self.progress_bar.set(0)

        final_message = f"Recorte em massa concluído.\n{processed_count}/{total_files} imagem(ns) processada(s) com sucesso."
        if errors:
            final_message += f"\n\nOcorreram {len(errors)} erro(s):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                final_message += "\n... (veja o console para mais detalhes)"
            messagebox.showwarning("Concluído com Erros", final_message)
        else:
            messagebox.showinfo("Concluído", final_message)

        self.status_label.configure(text="Recorte em massa concluído.")

if __name__ == "__main__":
    app = BackgroundRemoverApp()
    app.mainloop()