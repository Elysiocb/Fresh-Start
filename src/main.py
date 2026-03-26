#MODULES
import windows_manager as windows_manager #the heart of the program, the "engine" you might say
import interface #the face of the program, the "inter'FACE'" hehe WOW IM SUCH A GENIUS

#FUNCTION
def main() -> None:

    win_mod = windows_manager.Winget() #create an instance of the wingetModule class, which will be used to interact with the backend logic of the application
    app_interface = interface.Interface(win_mod) #create an instance of the Interface class, passing the wingetModule instance as a parameter to interact with the backend logic of the application

    app_interface.mainloop() #start the main loop of the interface, which will keep the application running and responsive to user interactions

#ENTRY POINT
if __name__ == "__main__":
    main()