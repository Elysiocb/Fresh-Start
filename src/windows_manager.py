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
    def winget_search(self, searched_item: str, search_filter: str= '--id') -> None:
        self.searched_item = searched_item.strip() #remove stupid spaces
        self.search_filter = search_filter

        cmd = ['winget', 'search', self.search_filter, self.searched_item, '--source', 'winget']
        # cmd = ['winget', 'search', searched_item, '--source', 'winget']
        
        try:
            resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if resultado.returncode != 0:
                return None

            # O segredo: Pegar as linhas e ignorar o cabeçalho (geralmente as 2 primeiras)
            linhas = resultado.stdout.strip().split('\n')
            apps_encontrados = []

            for linha in linhas:
                # Pula linhas que claramente são cabeçalhos ou separadores
                if "Nome" in linha or "Name" in linha or "----" in linha or not linha:
                    continue
                
                # O winget separa as colunas com pelo menos 2 espaços
                # Usamos regex para quebrar a linha onde houver 2 ou mais espaços
                partes = re.split(r'\s{2,}', linha.strip())

                if len(partes) >= 3:
                    apps_encontrados.append({
                        'Application': partes[0],
                        'Id': partes[1],
                        'Version': partes[2]
                    })
            
            print(apps_encontrados)
            return apps_encontrados

        except FileNotFoundError:
            print("Erro: Winget não está instalado ou não foi encontrado no PATH.")
            return []

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
        pass