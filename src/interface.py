import threading
import tkinter as tk
from tkinter import ttk #why do i need to import ttk when i already imported tk??? short anwser: the "Treeview" needs it somehow.

import system_utils as sys_utils

class Interface(tk.Tk): #tk.Tk is the main window class in tkinter, we are inheriting from it to create our own interface class
    def __init__(self, engine): #require an "engine" parameter, which will be used to interact with the backend logic of the application
        self.engine = engine

        super().__init__()
        
        self.title("Fresh Install")
        self.geometry("600x350")
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

        self.search = tk.Button(self.upperFrame, text="Search", command=self._on_search_button_click)
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

        # #app, id, version, status, checkbox
        # dados = [("Firefox", "Mozilla.Firefox", "102.0.0", "Installed", False), ("Vscode", "Microsoft.VisualStudioCode", "1.79.0", "Installed", False),("Minecraft", "Mojang.Minecraft", "1.19.0", "Installed", False)]
        # for item in dados:
        #     self.tree.insert("", "end", values=item)

        self.update_table()

        self.tree.pack(fill="both", expand=True,padx=10, pady=10)

    def _on_search_button_click(self):
        search_term = self.searchEntry.get()
        if not search_term.strip(): # Verifica se o termo de busca não está vazio ou contém apenas espaços
            print("O termo de busca não pode ser vazio.")
            # Opcional: exibir uma mensagem de erro para o usuário
            return

        # Desabilita o botão de busca para evitar cliques múltiplos durante a busca
        self.search.config(state=tk.DISABLED)
        # Opcional: Adicionar um indicador visual de "Buscando..."

        # Executa a operação de busca em uma thread separada
        search_thread = threading.Thread(target=self._run_winget_search_in_thread, args=(search_term,))
        search_thread.start()

    def _run_winget_search_in_thread(self, search_term):
        try:
            self.engine.winget_search(search_term)
        except Exception as e:
            print(f"Erro durante a busca do winget: {e}")
        finally:
            # Agenda a atualização da UI (reabilitar botão e atualizar tabela) na thread principal
            self.after(0, self._after_search_update_ui)

    def _after_search_update_ui(self):
        self.search.config(state=tk.NORMAL) # Reabilita o botão de busca
        # Opcional: Remover o indicador visual de "Buscando..."
        self.update_table() # Atualiza a tabela com os novos resultados da busca

    #FUCTION TO HANDLE ALL KINDS OF MODIFICATION IN THE TREEVIEW
    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        
        data = sys_utils.SystemUtils().get_json()

        for item in data:
            application = item.get('Application', 'N/A')
            app_id = item.get('Id', 'N/A')
            version = item.get('Version', 'N/A')
            status = "Não Instalado" # Status padrão, ou pode ser determinado dinamicamente
            checkbox_state = False # Estado padrão do checkbox (para lógica interna, não um checkbox visual na célula da Treeview)

            # Insere a linha na Treeview
            # O primeiro argumento é o item pai (string vazia para itens de nível superior)
            # O segundo argumento é o índice (e.g., "end" para adicionar ao final)
            # O argumento 'values' é uma tupla/lista correspondente às colunas definidas
            self.tree.insert("", "end", values=(application, app_id, version, status, checkbox_state))
