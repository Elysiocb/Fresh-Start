import threading
import tkinter as tk
from tkinter import ttk #why do i need to import ttk when i already imported tk??? short anwser: the "Treeview" needs it somehow.

class Interface(tk.Tk): #tk.Tk is the main window class in tkinter, we are inheriting from it to create our own interface class
    def __init__(self, engine): #require an "engine" parameter, which will be used to interact with the backend logic of the application
        self.engine = engine

        super().__init__()
        
        self.title("Fresh Install")
        self.geometry("500x350")
        #self.resizable(False, False)
        self.visual()

    def visual(self):
        self.upperFrame = tk.Frame(self)
        self.upperFrame.pack(side="top", fill="x")
        self.upperFrame.config(background="#8cd64f")

        self.install = tk.Button(self.upperFrame, text="Install",command=self.engine.winget_install)
        self.install.pack(side="left", padx=10, pady=10)
        self.install.config(relief="raised", )

        self.update = tk.Button(self.upperFrame, text="Update",command=self.engine.winget_update)
        self.update.pack(side="left", padx=10, pady=10)

        self.searchEntry = tk.Entry(self.upperFrame)
        self.searchEntry.pack(side="left", padx=10, pady=10)

        self.search = tk.Button(self.upperFrame, text="Search", command=lambda: self.engine.winget_search(self.searchEntry.get()))
        self.search.pack(side="left", padx=10, pady=10)

        self.configuration = tk.Button(self.upperFrame, text="Configuration",command=self.engine.configuration)
        self.configuration.pack(side="right", padx=10, pady=10)

        self.TableFrame = tk.Frame(self)
        self.TableFrame.pack(side="bottom", fill="both", expand=True)
        self.TableFrame.config(background="#326510")

        self.tree = ttk.Treeview(self.TableFrame, columns=("Application", "Id","Version","Status","Checkbox"), show="headings")
        self.tree.heading("Application", text="Application")
        self.tree.heading("Id", text="Id")
        self.tree.heading("Version", text="Version")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Checkbox", text="")


        # Configuração da largura das colunas para caberem na tela de 500px
        self.tree.column("Application", width=150, stretch=True)
        self.tree.column("Id", width=150, stretch=True)
        self.tree.column("Version", width=80, stretch=True, anchor="ne")
        self.tree.column("Status", width=80, stretch=True)
        self.tree.column("Checkbox", width=60, stretch=False)

        #app, id, version, status, checkbox
        dados = [("Firefox", "Mozilla.Firefox", "102.0.0", "Installed", False), ("Vscode", "Microsoft.VisualStudioCode", "1.79.0", "Installed", False),("Minecraft", "Mojang.Minecraft", "1.19.0", "Installed", False)]
        for item in dados:
            self.tree.insert("", "end", values=item)

        self.tree.pack(fill="both", expand=True,padx=10, pady=10)

    #FUCTION TO HANDLE ALL KINDS OF MODIFICATION IN THE TREEVIEW
    def update_table(self):
        pass