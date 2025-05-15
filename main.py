import customtkinter as ctk
from app.gui.app_principal import AplicativoRemoveFundo

def main():
    # Configuração do tema
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = AplicativoRemoveFundo()
    app.mainloop()

if __name__ == "__main__":
    main()
