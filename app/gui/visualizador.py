import customtkinter as ctk
from tkinter import Canvas
from PIL import Image, ImageTk

class VisualizadorImagem(ctk.CTkToplevel):
    def __init__(self, master, imagem, titulo):
        super().__init__(master)
        self.title(titulo)
        self.geometry("800x600")
        self.grab_set()
        
        self.imagem_original = imagem
        self.zoom_atual = 1.0
        
        # Frame principal
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Canvas com scrollbars
        self.canvas = Canvas(
            self.frame, 
            bd=0, 
            highlightthickness=0, 
            background=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        )
        
        self.rolagem_v = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.canvas.yview)
        self.rolagem_h = ctk.CTkScrollbar(self.frame, orientation="horizontal", command=self.canvas.xview)
        
        self.rolagem_v.grid(row=0, column=1, sticky="ns")
        self.rolagem_h.grid(row=1, column=0, sticky="ew")
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.configure(yscrollcommand=self.rolagem_v.set, xscrollcommand=self.rolagem_h.set)
        
        # Exibir imagem inicial
        self.atualizar_canvas()
        
        # Frame de controles de zoom
        self.frame_zoom = ctk.CTkFrame(self)
        self.frame_zoom.pack(pady=5)
        
        self.botao_zoom_mais = ctk.CTkButton(self.frame_zoom, text="+", width=40, 
                                           command=lambda: self.zoom(1.2))
        self.botao_zoom_mais.pack(side="left", padx=5)
        
        self.botao_zoom_menos = ctk.CTkButton(self.frame_zoom, text="-", width=40, 
                                            command=lambda: self.zoom(0.8))
        self.botao_zoom_menos.pack(side="left", padx=5)
        
        self.botao_zoom_reset = ctk.CTkButton(self.frame_zoom, text="1:1", width=40, 
                                            command=lambda: self.zoom(1.0/self.zoom_atual))
        self.botao_zoom_reset.pack(side="left", padx=5)
        
        self.rotulo_zoom = ctk.CTkLabel(self.frame_zoom, text=f"Zoom: {self.zoom_atual:.1f}x")
        self.rotulo_zoom.pack(side="left", padx=5)
        
        # Eventos do mouse
        self.canvas.bind("<MouseWheel>", self.ao_rolar_mouse)
        self.canvas.bind("<Button-4>", lambda e: self.zoom(1.1))
        self.canvas.bind("<Button-5>", lambda e: self.zoom(0.9))
        
        # Navegação com botão do meio do mouse
        self.canvas.bind("<ButtonPress-2>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B2-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        
        self.after(100, lambda: self.canvas.focus_set())
    
    def atualizar_canvas(self):
        """Atualiza a imagem no canvas com o zoom atual"""
        try:
            largura = int(self.imagem_original.width * self.zoom_atual)
            altura = int(self.imagem_original.height * self.zoom_atual)
            
            if largura < 1 or altura < 1:
                return
                
            metodo_redimensionamento = Image.Resampling.NEAREST
            if self.zoom_atual == 1.0:
                metodo_redimensionamento = Image.Resampling.LANCZOS
                
            imagem_redimensionada = self.imagem_original.resize(
                (largura, altura), 
                metodo_redimensionamento
            )
            
            self.tk_imagem = ImageTk.PhotoImage(imagem_redimensionada)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor='nw', image=self.tk_imagem)
            self.canvas.image = self.tk_imagem
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            if hasattr(self, 'rotulo_zoom'):
                self.rotulo_zoom.configure(text=f"Zoom: {self.zoom_atual:.1f}x")
                
        except Exception as e:
            print(f"Erro ao atualizar canvas: {e}")
    
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
