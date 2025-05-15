import customtkinter as ctk
from tkinter import Canvas, Scrollbar
from PIL import Image, ImageTk, ImageDraw

class JanelaBorracha(ctk.CTkToplevel):
    def __init__(self, master, imagem, callback_concluido):
        super().__init__(master)
        self.title("Ferramenta de Borracha")
        self.geometry("800x600")
        self.grab_set()
        
        self.imagem_original = imagem
        self.imagem_editavel = imagem.copy()
        self.callback_concluido = callback_concluido
        self.zoom_atual = 1.0
        self.tamanho_borracha = 20
        self.circulo_cursor = None
        
        # Frame principal do canvas
        self.frame_canvas = ctk.CTkFrame(self)
        self.frame_canvas.pack(fill="both", expand=True)
        
        # Canvas com scrollbars
        self.canvas = Canvas(self.frame_canvas, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.rolagem_h = Scrollbar(self.frame_canvas, orient="horizontal", command=self.canvas.xview)
        self.rolagem_h.grid(row=1, column=0, sticky="ew")
        
        self.rolagem_v = Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.rolagem_v.grid(row=0, column=1, sticky="ns")
        
        self.canvas.configure(xscrollcommand=self.rolagem_h.set, yscrollcommand=self.rolagem_v.set)
        
        # Configuração do layout
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)
        
        # Exibe a imagem inicial
        self.atualizar_canvas()
        
        # Eventos do mouse para a borracha
        self.canvas.bind("<B1-Motion>", self.apagar)
        self.canvas.bind("<ButtonPress-1>", self.apagar)
        self.canvas.bind("<Motion>", self.mostrar_cursor)
        self.canvas.bind("<Leave>", self.esconder_cursor)
        self.canvas.bind("<MouseWheel>", self.ao_rolar_mouse)
        
        # Frame de controles
        self.frame_controles = ctk.CTkFrame(self)
        self.frame_controles.pack(pady=5)
        
        # Slider para o tamanho da borracha
        ctk.CTkLabel(self.frame_controles, text="Tamanho da Borracha:").pack(side="left", padx=5)
        self.slider_tamanho = ctk.CTkSlider(
            self.frame_controles, 
            from_=5, 
            to=100, 
            number_of_steps=95, 
            command=self.atualizar_tamanho_borracha
        )
        self.slider_tamanho.set(self.tamanho_borracha)
        self.slider_tamanho.pack(side="left", padx=5)
        
        # Botões de zoom
        self.botao_zoom_mais = ctk.CTkButton(self.frame_controles, text="Zoom +", 
                                           command=lambda: self.zoom(1.2))
        self.botao_zoom_mais.pack(side="left", padx=5)
        
        self.botao_zoom_menos = ctk.CTkButton(self.frame_controles, text="Zoom -", 
                                            command=lambda: self.zoom(0.8))
        self.botao_zoom_menos.pack(side="left", padx=5)
        
        # Botões de ação
        self.botao_salvar = ctk.CTkButton(self.frame_controles, text="Salvar Alterações", 
                                        command=self.salvar_alteracoes)
        self.botao_salvar.pack(side="left", padx=5)
        
        self.botao_cancelar = ctk.CTkButton(self.frame_controles, text="Cancelar", 
                                          command=self.destroy)
        self.botao_cancelar.pack(side="left", padx=5)
    
    def atualizar_canvas(self):
        """Atualiza a imagem exibida no canvas com o zoom atual"""
        largura = int(self.imagem_editavel.width * self.zoom_atual)
        altura = int(self.imagem_editavel.height * self.zoom_atual)
        
        imagem_redimensionada = self.imagem_editavel.resize(
            (largura, altura), 
            Image.Resampling.NEAREST
        )
        
        self.tk_imagem = ImageTk.PhotoImage(imagem_redimensionada)
        
        if hasattr(self, 'id_imagem_canvas'):
            self.canvas.itemconfig(self.id_imagem_canvas, image=self.tk_imagem)
        else:
            self.id_imagem_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.tk_imagem)
            
        self.canvas.image = self.tk_imagem
        self.canvas.config(scrollregion=(0, 0, largura, altura))
    
    def apagar(self, evento):
        """Apaga a área onde o mouse é clicado ou arrastado"""
        x = int(self.canvas.canvasx(evento.x) / self.zoom_atual)
        y = int(self.canvas.canvasy(evento.y) / self.zoom_atual)
        
        desenho = ImageDraw.Draw(self.imagem_editavel)
        desenho.ellipse(
            (x - self.tamanho_borracha, y - self.tamanho_borracha, 
            x + self.tamanho_borracha, y + self.tamanho_borracha), 
            fill=(0, 0, 0, 0)
        )
        
        self.atualizar_canvas()
    
    def mostrar_cursor(self, evento):
        """Exibe o cursor da borracha no canvas"""
        x = self.canvas.canvasx(evento.x)
        y = self.canvas.canvasy(evento.y)
        
        if self.circulo_cursor:
            self.canvas.delete(self.circulo_cursor)
            
        self.circulo_cursor = self.canvas.create_oval(
            x - self.tamanho_borracha * self.zoom_atual, 
            y - self.tamanho_borracha * self.zoom_atual,
            x + self.tamanho_borracha * self.zoom_atual, 
            y + self.tamanho_borracha * self.zoom_atual,
            outline="red", width=2, fill="gray", stipple="gray50"
        )
    
    def esconder_cursor(self, evento=None):
        """Remove o cursor da borracha ao sair do canvas"""
        if self.circulo_cursor:
            self.canvas.delete(self.circulo_cursor)
            self.circulo_cursor = None
    
    def atualizar_tamanho_borracha(self, valor):
        """Atualiza o tamanho da borracha com base no slider"""
        self.tamanho_borracha = int(valor)
    
    def ao_rolar_mouse(self, evento):
        """Aplica zoom quando o usuário usa a roda do mouse"""
        if evento.delta > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)
    
    def zoom(self, fator):
        """Aplica zoom na imagem"""
        novo_zoom = self.zoom_atual * fator
        
        if 0.1 <= novo_zoom <= 10.0:
            self.zoom_atual = novo_zoom
            self.atualizar_canvas()
    
    def salvar_alteracoes(self):
        """Salva as alterações e fecha a janela"""
        if self.callback_concluido:
            self.callback_concluido(self.imagem_editavel)
        self.destroy()
