import threading
import tkinter as tk
from tkinter import ttk #why do i need to import ttk when i already imported tk??? short anwser: the "Treeview" needs it somehow.

import system_utils as sys_utils

class Interface(tk.Tk): #tk.Tk is the main window class in tkinter, we are inheriting from it to create our own interface class
    def __init__(self, engine): #require an "engine" parameter, which will be used to interact with the backend logic of the application
        self.engine = engine
        self.checked_items = {} # Stores the checked state of items: {app_id: True/False}
        self.program_just_started = True # Flag to indicate if the program has just started

        super().__init__() #call the constructor of the parent class (tk.Tk) to initialize the main window
        
        self.title("Fresh Install")
        self.geometry("600x350")
        #self.resizable(False, False)
        self.visual()

    def visual(self):
        self.upperFrame = tk.Frame(self)
        self.upperFrame.pack(side="top", fill="x")
        self.upperFrame.config(background="#8cd64f")

        self.install = tk.Button(self.upperFrame, text="Install",command=self._on_install_button_click)
        self.install.pack(side="left", padx=10, pady=10)
        self.install.config(relief="raised", )

        self.update = tk.Button(self.upperFrame, text="Update",command=self.engine.winget_update)
        self.update.pack(side="left", padx=10, pady=10)

        self.search = tk.Button(self.upperFrame, text="Search", command= lambda: self.Search_Window(self))
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
        self.tree.column("Checkbox", width=10, stretch=True)

        self.tree.pack(fill="both", expand=True,padx=10, pady=10)
        self.tree.bind("<Double-1>", self._on_double_click) # Bind double-click event ?????????????????????

        self.update_table()
    
    def _on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # Get current values of the clicked item
        current_values = self.tree.item(item_id, 'values')
        if not current_values or len(current_values) < 5: # Ensure there are enough columns
            return

        app_id = current_values[1] # Assuming 'Id' is the second column (index 1)

        # Toggle the checked state
        is_checked = self.checked_items.get(app_id, False)
        self.checked_items[app_id] = not is_checked

        # Update the Treeview item's checkbox column
        new_checkbox_text = "✓" if self.checked_items[app_id] else ""
        
        # Create a mutable list from current_values to modify the checkbox state
        updated_values = list(current_values)
        updated_values[4] = new_checkbox_text # Assuming 'Checkbox' is the fifth column (index 4)
        self.tree.item(item_id, values=updated_values)

    def _on_install_button_click(self):
        # Get selected app_ids
        apps_to_install = [app_id for app_id, is_checked in self.checked_items.items() if is_checked]

        if not apps_to_install:
            print("Nenhum aplicativo selecionado para instalação.")
            return

        self.install.config(state=tk.DISABLED)
        self.update.config(state=tk.DISABLED) # Also disable update button during install
        self.search.config(state=tk.DISABLED) # Disable search button too

        install_thread = threading.Thread(target=self._run_install_in_thread, args=(apps_to_install,))
        install_thread.start()

    def _run_install_in_thread(self, apps_to_install):
        try:
            for app_id in apps_to_install:
                # Find the item_id in the Treeview for the current app_id
                item_id_to_update = None
                for item_id in self.tree.get_children():
                    values = self.tree.item(item_id, 'values')
                    if values and values[1] == app_id: # Assuming 'Id' is at index 1
                        item_id_to_update = item_id
                        break
                
                if item_id_to_update:
                    # Update status in Treeview for the app being installed
                    current_values = list(self.tree.item(item_id_to_update, 'values'))
                    current_values[3] = "Instalando..." # Update status column
                    self.tree.item(item_id_to_update, values=current_values)
                    self.update_idletasks() # Force UI update
                
                self.engine.winget_command("install", app_id)
                
                if item_id_to_update:
                    # Update status in Treeview after installation
                    current_values = list(self.tree.item(item_id_to_update, 'values'))
                    current_values[3] = "Instalado" # Update status column
                    self.tree.item(item_id_to_update, values=current_values)
                    self.update_idletasks() # Force UI update

        except Exception as e:
            print(f"Erro durante a instalação: {e}")
        finally:
            self.after(0, self._after_install_update_ui)

    def _after_install_update_ui(self):
        self.install.config(state=tk.NORMAL)
        self.update.config(state=tk.NORMAL)
        self.search.config(state=tk.NORMAL)
        # Optionally, clear checked items after installation and refresh table
        # self.checked_items = {}
        # self.update_table()

    # FUNCTION TO HANDLE ALL KINDS OF MODIFICATION IN THE TREEVIEW
    def update_table(self, window=None): #TODO find the correct type of this window paramenter...
        if window == None:
            window = self

        # clean old data "applist.json" from previous uses of the program
        try:
            self.engine.remove_json('assets/applist.json')
        except Exception as e:
            raise e
        finally:
            self.program_just_started = False

        window.tree.delete(*window.tree.get_children())

        data = self.engine.get_json('assets/applist.json') # data is a list of dicts from json
        
        # Create a temporary set of app_ids from the new data
        current_app_ids = {item_data.get('Id') for item_data in data if item_data.get('Id')}
        
        # Clean up checked_items for apps no longer in the list
        # This is important if a search removes items that were previously checked
        window.checked_items = {app_id: state for app_id, state in window.checked_items.items() if app_id in current_app_ids}

        for item_data in data:
            application = item_data.get('Application', 'N/A')
            app_id = item_data.get('Id', 'N/A')
            version = item_data.get('Version', 'N/A')
            status = "Não Instalado" # Status padrão, ou pode ser determinado dinamicamente

            # Get the checked state for this app_id, default to False if not found
            is_checked = window.checked_items.get(app_id, False)
            checkbox_text = "✓" if is_checked else ""

            window.tree.insert("", "end", values=(application, app_id, version, status, checkbox_text))

    class Search_Window(tk.Toplevel):
        def __init__(self, parent_window):
            super().__init__() #call the constructor of the parent class (tk.Toplevel) to initialize the new window
            self.parent_window = parent_window
            
            self.checked_items = {}

            self.title("Search")
            self.geometry("500x350")

            self._visual()

        def _visual(self):
            self.frame = tk.Frame(self)
            self.frame.pack(side="top", fill="x")
            self.frame.config(background="#8cd64f")

            self.search_entry = tk.Entry(self.frame) # O Entry é filho do search_frame (que é filho da Search_Window)
            self.search_entry.pack(side="left", expand=True, fill="x", padx=10, pady=10)
            self.search_entry.bind("<Return>", lambda event: self._on_search_button_click()) # Permite buscar com Enter

            self.search = tk.Button(self.frame, text="Search", command=self._on_search_button_click)
            self.search.pack(side="right", padx=10, pady=10)

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
            self.tree.column("Checkbox", width=10, stretch=True)

            self.tree.pack(fill="both", expand=True,padx=10, pady=10)
        
        def _on_search_button_click(self):
            search_term = self.search_entry.get()
            if not search_term.strip(): # Verifica se o termo de busca não está vazio ou contém apenas espaços
                print("O termo de busca não pode ser vazio.")
                # Opcional: exibir uma mensagem de erro para o usuário
                return

            # Desabilita o botão de busca para evitar cliques múltiplos durante a busca
            self.search.config(state=tk.DISABLED)
            self.search.config(text="Searching...") # Opcional: Muda o texto do botão para indicar que a busca está em andamento

            # Executa a operação de busca em uma thread separada
            search_thread = threading.Thread(target=self._run_winget_search_in_thread, args=(search_term,))
            search_thread.start()

        def _run_winget_search_in_thread(self, search_term):
            try:
                self.parent_window.engine.winget_search(search_term)
            except Exception as e:
                print(f"Erro durante a busca do winget: {e}")
            finally:
                # Agenda a atualização da UI (reabilitar botão e atualizar tabela) na thread principal
                #self.after(0, self._after_search_update_ui)

                self.search.config(state=tk.NORMAL) # Reabilita o botão de busca
                self.search.config(text="Search") # Restaura o texto original do botão

                self.parent_window.update_table(self) # Atualiza a tabela com os novos resultados da busca