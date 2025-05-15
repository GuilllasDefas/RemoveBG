import customtkinter as ctk
from tkinter import Canvas, Scrollbar
from PIL import Image, ImageTk

class JanelaRecorte(ctk.CTkToplevel):
    def __init__(self, master, imagem, callback_concluido):
        super().__init__(master)
        self.title("Ferramenta de Recorte")
        self.geometry("800x600")
        self.grab_set()
        
        self.imagem_original = imagem
        self.callback_concluido = callback_concluido
        self.inicio_x = None
        self.inicio_y = None
        self.retangulo_recorte = None
        self.zoom_atual = 1.0
        
        # Frame do canvas
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
        
        # Exibe a imagem no canvas
        self.exibir_imagem()
        
        # Eventos do mouse para selecionar área de recorte
        self.canvas.bind("<ButtonPress-1>", self.ao_pressionar_mouse)
        self.canvas.bind("<B1-Motion>", self.ao_mover_mouse)
        self.canvas.bind("<MouseWheel>", self.ao_rolar_mouse)
        
        # Frame de controles de zoom
        self.frame_zoom = ctk.CTkFrame(self)
        self.frame_zoom.pack(pady=5)
        
        self.botao_zoom_mais = ctk.CTkButton(self.frame_zoom, text="Zoom +", 
                                            command=lambda: self.zoom(1.2))
        self.botao_zoom_mais.pack(side="left", padx=5)
        
        self.botao_zoom_menos = ctk.CTkButton(self.frame_zoom, text="Zoom -", 
                                             command=lambda: self.zoom(0.8))
        self.botao_zoom_menos.pack(side="left", padx=5)
        
        self.botao_zoom_reset = ctk.CTkButton(self.frame_zoom, text="Reset", 
                                             command=lambda: self.zoom(1.0/self.zoom_atual))
        self.botao_zoom_reset.pack(side="left", padx=5)
        
        # Frame de botões de ação
        self.frame_botoes = ctk.CTkFrame(self)
        self.frame_botoes.pack(pady=5)
        
        self.botao_recortar = ctk.CTkButton(self.frame_botoes, text="Recortar", 
                                           command=self.confirmar_recorte)
        self.botao_recortar.pack(side="left", padx=10)
        
        self.botao_cancelar = ctk.CTkButton(self.frame_botoes, text="Cancelar", 
                                          command=self.destroy)
        self.botao_cancelar.pack(side="left", padx=10)
        
    def exibir_imagem(self):
        """Exibe a imagem no canvas com o zoom atual"""
        largura = int(self.imagem_original.width * self.zoom_atual)
        altura = int(self.imagem_original.height * self.zoom_atual)
        
        imagem_redimensionada = self.imagem_original.resize((largura, altura), 
                                                           Image.Resampling.NEAREST)
        self.tk_imagem = ImageTk.PhotoImage(imagem_redimensionada)
        
        # Limpa o canvas e adiciona a nova imagem
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_imagem)
        self.canvas.image = self.tk_imagem
        
        # Ajusta a área de rolagem
        self.canvas.config(scrollregion=(0, 0, largura, altura))
    
    def ao_pressionar_mouse(self, evento):
        """Inicia o desenho do retângulo de seleção"""
        self.inicio_x = self.canvas.canvasx(evento.x)
        self.inicio_y = self.canvas.canvasy(evento.y)
        
        if self.retangulo_recorte:
            self.canvas.delete(self.retangulo_recorte)
            
        self.retangulo_recorte = self.canvas.create_rectangle(
            self.inicio_x, self.inicio_y, self.inicio_x, self.inicio_y,
            outline="red", width=2
        )
    
    def ao_mover_mouse(self, evento):
        """Atualiza o retângulo de seleção enquanto o mouse se move"""
        if self.retangulo_recorte:
            atual_x = self.canvas.canvasx(evento.x)
            atual_y = self.canvas.canvasy(evento.y)
            self.canvas.coords(self.retangulo_recorte, 
                              self.inicio_x, self.inicio_y, atual_x, atual_y)
    
    def ao_rolar_mouse(self, evento):
        """Aplica zoom quando o usuário usa a roda do mouse"""
        if evento.delta > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)
    
    def zoom(self, fator):
        """Aplica zoom na imagem"""
        novo_zoom = self.zoom_atual * fator
        
        # Limita o zoom entre 0.1x e 10x
        if 0.1 <= novo_zoom <= 10.0:
            self.zoom_atual = novo_zoom
            self.exibir_imagem()
    
    def confirmar_recorte(self):
        """Confirma o recorte e chama o callback com a imagem recortada"""
        if not self.retangulo_recorte:
            self.destroy()
            return
            
        # Obter coordenadas do retângulo
        x1, y1, x2, y2 = map(int, self.canvas.coords(self.retangulo_recorte))
        
        # Garantir que x1 < x2 e y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
            
        # Verificar se a área selecionada é válida
        if x2 - x1 <= 0 or y2 - y1 <= 0:
            self.destroy()
            return
            
        # Converter coordenadas de acordo com o zoom
        x1 = int(x1 / self.zoom_atual)
        y1 = int(y1 / self.zoom_atual)
        x2 = int(x2 / self.zoom_atual)
        y2 = int(y2 / self.zoom_atual)
        
        # Recortar a imagem
        imagem_recortada = self.imagem_original.crop((x1, y1, x2, y2))
        
        # Chamar o callback com a imagem recortada
        if self.callback_concluido:
            self.callback_concluido(imagem_recortada)
            
        self.destroy()
