import customtkinter as ctk

class DicaFlutuante:
    """ Cria uma dica flutuante (tooltip) para um widget tkinter/customtkinter
        com atraso para mostrar e cancelamento ao sair.
    """
    def __init__(self, widget, texto, atraso_ms=500): # Atraso padrão de 500ms
        self.widget = widget
        self.texto = texto
        self.atraso_ms = atraso_ms
        self.janela_dica = None
        self.id_agendamento = None  # Para guardar o ID do 'after' job

        self.widget.bind("<Enter>", self.agendar_mostrar_dica)
        self.widget.bind("<Leave>", self.cancelar_e_esconder_dica)
        self.widget.bind("<ButtonPress>", self.cancelar_e_esconder_dica) # Esconde se clicar

    def agendar_mostrar_dica(self, evento=None):
        """Agenda a exibição da dica após um atraso."""
        self.cancelar_dica() # Cancela qualquer dica/agendamento anterior
        # Agenda a chamada para _mostrar_dica_apos_atraso
        self.id_agendamento = self.widget.after(self.atraso_ms, self._mostrar_dica_apos_atraso)

    def _mostrar_dica_apos_atraso(self):
        """Cria e mostra a janela da dica (chamado via 'after')."""
        if self.janela_dica: # Se já existir por algum motivo, destrói
            self.esconder_janela_dica()

        # Pega a posição atual do widget na tela
        x, y, _, _ = self.widget.bbox("insert") # Pega bbox relativo ao widget
        # Calcula posição absoluta na tela
        x += self.widget.winfo_rootx() + 20 # Offset x
        y += self.widget.winfo_rooty() + 20 # Offset y

        # Cria a Toplevel (janela flutuante)
        self.janela_dica = ctk.CTkToplevel(self.widget)
        self.janela_dica.wm_overrideredirect(True) # Sem bordas/título
        self.janela_dica.wm_geometry(f"+{x}+{y}") # Posiciona
        self.janela_dica.attributes("-topmost", True) # Fica no topo

        # Cria o Label dentro da Toplevel
        label = ctk.CTkLabel(self.janela_dica, text=self.texto,
                            fg_color=("gray85", "gray20"),
                            corner_radius=5,
                            padx=8, pady=4,
                            wraplength=250,
                            justify="left")
        label.pack()

        # Resetar o job ID, pois a dica foi mostrada
        self.id_agendamento = None

    def cancelar_e_esconder_dica(self, evento=None):
        """Cancela o agendamento (se houver) e esconde a dica (se visível)."""
        self.cancelar_dica()
        self.esconder_janela_dica()

    def cancelar_dica(self):
        """Cancela o agendamento da exibição da dica."""
        if self.id_agendamento:
            self.widget.after_cancel(self.id_agendamento)
            self.id_agendamento = None

    def esconder_janela_dica(self):
        """Destroi a janela da dica se ela existir."""
        if self.janela_dica:
            try:
                if self.janela_dica.winfo_exists():
                    self.janela_dica.destroy()
            except Exception as e:
                # Pode dar erro se a janela já foi destruída ou durante o fechamento
                pass
            finally:
                self.janela_dica = None
