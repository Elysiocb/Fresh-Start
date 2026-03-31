import subprocess
import re

import system_utils

class Winget(system_utils.SystemUtils): #inherit from SystemUtils to have access to its methods hehehe
    def __init__(self):
        pass #idk why not

    #WINGET COMMAND DIRECTLY ON CMD
    def winget_command(self, command: str, app_id: str) -> None:
        
        full_command = [
            "winget", command, "--id", app_id, 
            "--silent", "--accept-source-agreements", "--accept-package-agreements"
        ]
        print(f"--Installing {app_id}--")
        
        result = subprocess.run(full_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Installed with success: {app_id}")
        else:
            error_msg = result.stdout if result.stdout else result.stderr #Sometimes winget outputs errors to stdout, sometimes to stderr, so we check both
            print(f"Error installing {app_id}: {error_msg[:200].strip()}...")

    #INSTALL WINGET
    def winget_install(self, data: dict= None) -> None:

        data = self.get_json()

        # Iterate over the apps defined in the JSON and process them
        for app_id, app_data in data.get("apps", {}).items():
            self.winget_command("install", app_id)

            # Check if we need to clean shortcuts based on config of each app
            config = app_data.get("config", {})

            remove_desktop = config.get("desktop_shortcut") is False
            remove_start_menu = config.get("start_menu") is False
            
            if remove_desktop or remove_start_menu:
                self.remove_shortcuts(app_id, remove_desktop, remove_start_menu)

        print("\nAll done!")

    #FUNCTION THAT WILL SEARCH AND GIVE A BUNCH OF IDS TO CHOOSE FROM WHEN TYPING AN APPLICATION
    def winget_search(self, searched_item: str, search_filter: str = '--id') -> None:
        self.searched_item = searched_item.strip() #remove stupid spaces. SERIOUSLY? IS THAT YOUR BEST COMMENT IDEA?
        self.search_filter = search_filter

        if self.searched_item == '':
            raise ValueError("Cannot search for an empty string.")

        cmd = ['winget', 'search', self.search_filter, self.searched_item, '--source', 'winget']
        # cmd = ['winget', 'search', searched_item, '--source', 'winget']

        try:
            resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            # print(f"Winget stdout:\n{resultado.stdout}") # Debug: Mostra a saída bruta do winget
            # print(f"Winget stderr:\n{resultado.stderr}") # Debug: Mostra erros, se houver

            if resultado.returncode != 0:
                print(resultado.returncode) #that's stupid, but idc
                return None

            # O segredo: Pegar as linhas e ignorar o cabeçalho (geralmente as 2 primeiras)
            linhas = resultado.stdout.strip().split('\n')
            apps_encontrados = []

            # Initialize these to prevent UnboundLocalError if the else branch is taken
            start_of_column_name = None
            start_of_column_id = None
            start_of_column_version = None
            # and these..
            column_name_value = ""
            column_id_value = ""
            column_version_value = ""

            for linha in linhas:
                # Pula linhas que claramente são cabeçalhos ou separadores
                if not linha or "----" in linha.strip():
                    continue
                
                if "Nome" in linha or "Name" in linha.strip():
                    
                    start_of_column_name = len(linha[:linha.index("Name")]) if "Name" in linha else len(linha[:linha.index("Nome")])
                    start_of_column_id = len(linha[:linha.index("ID")])
                    start_of_column_version = len(linha[:linha.index("Version")]) if "Version" in linha else len(linha[:linha.index("Versão")])

                    print(start_of_column_name, start_of_column_id, start_of_column_version) # Mostra as posições de início de cada coluna
                    continue
                
                # O winget separa as colunas com pelo menos 2 espaços
                # Usamos regex para quebrar a linha onde houver 2 ou mais espaços
                partes = re.split(r'\s{2,}', linha.strip())
                print(f"Line split into parts: {partes}") # Debug: Mostra as partes de cada linha

                if len(partes) >= 3:
                    apps_encontrados.append({
                        'Application': partes[0],
                        'Id': partes[1],
                        'Version': partes[2]
                    })
                else:
                    if not start_of_column_name and not start_of_column_id and not start_of_column_version:
                        continue #somehow there's a chance these variables won't be defined so we check it to prevent surprises

                    #trying to remediate cases where the split doesn't work as expected, by using the known positions of the columns
                    column_name_value = linha[start_of_column_name:start_of_column_id].strip()
                    column_id_value = linha[start_of_column_id:start_of_column_version].strip()
                    column_version_value = linha[start_of_column_version:].strip()
                    # print(column_name_value, column_id_value, column_version_value) # Debug: Mostra os valores extraídos usando as posições das colunas

                    apps_encontrados.append({
                        'Application': column_name_value,
                        'Id': column_id_value,
                        'Version': column_version_value
                    })
                        
                    # print(f"Skipping line (not enough parts): '{linha}' -> {partes}") # Debug: Indica linhas com poucas partes
            
            #print(apps_encontrados)
            # return apps_encontrados
            self.set_json(apps_encontrados)

        except FileNotFoundError as e:
            print("Erro: Winget não está instalado ou não foi encontrado no PATH.")
            raise e

    #UPDATE WINGET

    ##########################
    ####WORK IN PROGRESS######
    ##########################
    def winget_update(self) -> None:
        print("Updating winget...")
        subprocess.run([
            "winget", "upgrade", "--all", "--silent", "--accept-source-agreements"
        ])

    #FUNCTION TO SWITCH "DESKTOP SHORTCUT" AND "STARTMENU SHORTCUT"
    def configuration(self) -> None:
        raise NotImplementedError