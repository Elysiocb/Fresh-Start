import os
import json

class SystemUtils():
    def __init__(self):
        pass

    def get_json(self, json_path: str= 'applist.json') -> dict:
        self.__annotations__


        if not os.path.exists(json_path):
            print("Failed to find 'applist.json'.")
            return KeyError("'applist.json' not found.")#i dont really know what this does, i hope it raises an error message correctly

        try:
            with open(json_path, 'r', encoding='utf-8') as f: #with does automatic closing of the file, and utf-8 encoding to support special characters
                return json.load(f) #i think this is right... 

        except json.JSONDecodeError as e:
            print(f"Invalid JSON format in 'applist.json'\nDetails: {e}")
            return e #meh this ill do. maybe
        
    def json_json(self):
        # json.encoder
        pass

    def remove_shortcuts(self, app_id: str, remove_desktop: bool, remove_start_menu: bool) -> None:

        app_name_keyword = app_id.split('.')[-1].lower()#get the last part of the app_id as a keyword to identify shortcuts
        paths_to_check = []

        if remove_desktop:
            paths_to_check.extend([ #adds this paths to the list
                os.path.expanduser("~\\Desktop"), #User's desktop path
                os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), "Desktop") #Public desktop path
            ])

        if remove_start_menu:
            paths_to_check.extend([ #adds this paths to the list
                os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"), #User's start menu path
                os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs") #Public start menu path
            ])

        for base_path in paths_to_check:
            if not os.path.exists(base_path): #If the path doesn't exist, skip it
                continue

            for root, _, files in os.walk(base_path):
                for file in files:
                    if file.endswith(".lnk") and app_name_keyword in file.lower(): #Checks if the file is a shortcut and contains the app name keyword
                        file_path = os.path.join(root, file) #Full path to the shortcut
                        try:
                            os.remove(file_path) #Removes the shortcut
                            print(f"Shortcut removed: {file_path}")
                        except Exception as e: #error meh why not
                            print(f"Failed to remove shortcut {file_path}: {e}")