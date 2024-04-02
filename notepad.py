## Libraries
# Main GUI Libraries
import tkinter as tk
from tkinter import messagebox

# Misc libraries for app functionality
import random as rand # randomly generates exit messages
from datetime import datetime # capture system local time and date
import re # validates filename when user attemps to save a file
import enchant # !! used for spell-checking text widget ONLY FOR TEXT WIDGET (not filename entry box)

# System associated libraries (i guess?)
import os # for deleting credentials text file on settings reset
from sys import exit # force close when needed

# Interface main setup
root = tk.Tk() # loads new window
root.title("PyJot") 
root.geometry("600x400")

# Undo/redo stacks for undoing/redoing actions (experimental, slightly buggy)
undoStack = []
redoStack = []

# Dictionary for pyenchant to look through for words
dictionary = enchant.Dict("en_US") # English dictionary for spell checking (the brits are crying rn and i love those tears)

# Visual variables (fonts)
MainFont = ("Rajdhani-Medium.ttf", 9)
TextFont = ("FiraCode-Regular.ttf", 9)

# Misc variables
pyjotver = "PyJot v1.0A" # Current app version


# Startup functions
def FetchUser(theme="", username="Guest", key=0):
    """
    Fetches username, theme, and saved filename + text entry from credentials text file. 
    Otherwise, writes username and theme from login screen to credential file and contines to app screen.
    """
    # Global declaration to access font colours 
    global BgColour, TextColour
    
    # Username stuff and handling
    if key == 1: # Login was confirmed 
        """ 
        Key is used to signal if we have an instant/delayed login. 
        A value of 1 here means this is the first login by the user (also after settings are reset)
        """
        with open("credentials.txt", "w") as file:
            if len(username) > 15: # Max limit before it clips into Text widget
                username = username[:15] # From beginning to 15th character
            file.write(f"{username}\n{theme}")
        
        # Setting up theme stuff
        if theme == "Dark":
            TextColour = "#ededed" # White
            BgColour = "#36393e" # Black/Blackish grey
        elif theme == "Light": # Light Mode
            TextColour = "#36393e"
            BgColour = "#ededed"
       
        root.configure(bg=BgColour) # Change background colour of window
        
        UpdateStatus("App Started")
        RootCreate(username, TextColour, BgColour) # passes username to RootCreate to display    

    else: # No login needed, using saved credentials
        with open("credentials.txt", "r") as file:
            userCredentials = file.readlines()
        with open("recentSaves.txt", "r") as f:
            savedContent = f.readlines()
        
        # Setting up theme stuff 
        # (userCredentials[1] specifies the 2nd line of credentials.txt, where readlines returns a list, where every index is one line (so line 2 = index 1))
        if userCredentials[1] == "Dark":
            TextColour = "#ededed" # White
            BgColour = "#36393e" # Black/Blackish grey
        elif userCredentials[1] == "Light": # Light Mode
            TextColour = "#36393e"
            BgColour = "#ededed"
        
        root.configure(bg=BgColour) # Change background colour of window
        
        UpdateStatus("App Started")
        try: # Saved entry might not exist all the time!
            RootCreate(userCredentials[0], TextColour, BgColour, savedContent[2], savedContent[1]) # passes username to RootCreate to display
        # savedContent[2] is the previously saved filename, savedContent[1] is the saved file entry
        except IndexError: 
            RootCreate(userCredentials[0], TextColour, BgColour) # Normal login with default parameters

def OnAppOpen():
    """
    Stores username of user and colour theme in credentials text file. Checks if new user is present, otherwise starts app with saved username.
    """

    # Checking if saved session exists, creates empty save file otherwise
    if os.path.exists("recentSaves.txt"):
        print("Found last saved session.")
    else:
        print("No recent saved session found. Empty save created.")
        f = open(f"recentSaves.txt", "x") # create a new file in local directory, can be opened in LoadFile
    
    # Trying to find credential file
    if os.path.exists("credentials.txt"):
        print("\nFound File.")
        FetchUser()
    else:
        print("File Not Found. Login started.")
        
        # variable held by radiobuttons to determine theme for app
        themeModeVar = tk.StringVar()

        WelcomeText = tk.Label(root, text=f"Welcome to {pyjotver}", font=("Rajdhani-Medium.ttf", 14), anchor="center", justify="center")
        WhoAmIText = tk.Label(root, text="What's your name?", font=MainFont, anchor="center", justify="center")
        ThemeModeText = tk.Label(root, text="What theme will you use?", font=MainFont, anchor="center", justify="center") 
        UsernameEntry = tk.Entry(root, justify="center", width=15)
        DarkModeRadioChoice = tk.Radiobutton(root, text="Dark Mode", width=37, justify="center", variable=themeModeVar, value="Dark")
        LightModeRadioChoice = tk.Radiobutton(root, text="Light Mode", width=30, justify="center", variable=themeModeVar, value="Light")
        ContinueButton = tk.Button(
            root, background="#d66363", text="Continue to PyJot", font=MainFont, command=lambda: [
            FetchUser(themeModeVar.get(),UsernameEntry.get(), 1), 
            WelcomeText.destroy(), 
            WhoAmIText.destroy(), UsernameEntry.destroy(), ThemeModeText.destroy(), 
            DarkModeRadioChoice.destroy(), LightModeRadioChoice.destroy(), ContinueButton.destroy()], 
            width=30
            ) # Proceeds with login handling, deletes all onscreen widgets

        WelcomeText.pack(pady=(100,0))
        WhoAmIText.pack(pady=(5,5))

        UsernameEntry.pack(pady=(0,5))
        UsernameEntry.insert(0, "Guest")
        UsernameEntry.configure(font=MainFont)

        ThemeModeText.pack(pady=(0,5))
        DarkModeRadioChoice.pack()
        LightModeRadioChoice.pack(pady=(0,15))

        ContinueButton.pack()

# App Closing functionality/handling
def ExitApp():
    """
    Prompts user if they want to exit the app via messagebox popup. Destroys interface on exit.
    """
    exitSentences = ["We'll miss you a bunch :(", "See you again soon (?)", "Are you sure you want to exit?", "You leaving already?"]
    if messagebox.askokcancel("Exit PyJot?", rand.choice(exitSentences) + "\n\nBe sure you have saved your current file before closing. Unsaved progress will be lost!!"):
        root.destroy()

def BeforeResetSettings():
    """
    Gateway to resetting user app settings. Prompts messagebox and handles following request.
    """
    if messagebox.askokcancel("Reset current app settings?", "This will reset your current credentials and close your current session. You'll need to reload your current file once you restart the app.\n\nDo you wish to proceed?"):
        root.destroy() # Kill main window 
        credentialPath = "credentials.txt" # will need to modify if we decide to move this stuff elsewhere
        if os.path.exists(credentialPath): # confirms that it can find the credentials file in the directory
            os.remove(credentialPath) # delete credential file
            exit("Settings deleted; closing...")
        else:
            exit("File does not exist; exiting...")

# Undo/Redo Functionality, Spell checking as well
def SpellCheck(textEntry):
    """
    Uses pyenchant to employ spell checking on Text Widget entry.
    """
    WordsInEntry = textEntry.split() # Isolates every words in entry
    MisspelledWordsInEntry = [word for word in WordsInEntry if not dictionary.check(word)] # List comprehension that creates a list of misspelt words; checks described dictionary using inputted word and confirms spelling

    if MisspelledWordsInEntry:
        messagebox.showwarning("You're illiterate >:c", f"Go back to Engrish class, you got these words wrong!\n\n{MisspelledWordsInEntry}")

def Undo(textEntry, textWidget):
    """
    Undos last saved stack input from Text widget.
    """
    if undoStack != []: # for some reason we somehow have empty stacks being used even when the IndexError should catch them, this works lmao
        try:
            print(undoStack, redoStack)
            redoStack.append(textEntry) # save current text to later redo if needed
            textWidget.delete("1.0", "end") # wipe widget of text
            textWidget.insert("1.0", undoStack.pop()) # same logic as below
            print(f"\nEntry undone: {undoStack}")
        except IndexError: # Occurs if the stack is empty
            messagebox.showerror("Undo Failed.", "Cannot undo on empty stack: No actions to undo!")
    else:
        messagebox.showerror("Undo Failed.", "Cannot undo on empty stack: No actions to undo!")

def Redo(textEntry, textWidget):
    """
    Redos last saved stack input from Text widget.
    """
    if redoStack != []: # See reason above in Undo function
        try:
            undoStack.append(textEntry) # save current text to later undo "redone" text
            textWidget.delete("1.0", "end") # wipe widget of text
            textWidget.insert("1.0", redoStack.pop()) # same logic as below
            print(f"\nEntry redone: {redoStack}")
        except IndexError: # Occurs if the stack is empty
            messagebox.showerror("Redo Failed", "Cannot redo on empty stack: No actions to redo!")
    else:
        messagebox.showerror("Redo Failed.", "Cannot undo on empty stack: No actions to redo!")

def SaveModifiedText(textEntry):
    """
    Saves previously done action to undoStack to allow undo functionality. undoStack also gets updates in Redo() to undo a redo attempt.
    """
    if textEntry and textEntry[-1] == undoStack:
        pass # Do no modification to undoStack
    else:
        undoStack.append(textEntry)


# File/App functionality
def UpdateStatus(action):
    """
    Record last action performed by user onscreen. Empty on startup.
    """
    Time = datetime.now()
    TimeOfAction = Time.strftime("%H:%M:%S")

    status = tk.Label(text=f"Last action performed: {action} @ {TimeOfAction}", font=MainFont, bg=BgColour, fg=TextColour)
    status.pack()
    status.place(y=10,x=110)

def SaveFile(entry,raw_filename):
    """
    Saves text entry to a new text file or preloaded text file (requires a file to have been loaded in workspace). Validates filename entry or uses default name.
    """
    if ((raw_filename == "Untitled file") or (len(raw_filename) == 0)): # either left alone of they deleted the entry
        filename = "Untitled"
    else:
        catch = re.search(r"(.+)(\..+)?$",raw_filename) # capture the filename itself and extension if there is one (optional)
        filename = catch.group(1)

    with open(f"{filename}.txt", "w") as file: # creates new file and writes to it the Text widget entry
        file.write(entry) # writes Text entry stuff to file that was given
        UpdateStatus("File Saved")
        # notify user onscreen
    
    # Save text entry and filename to recentSaves file to preload on next session
    with open("recentSaves.txt", "w") as file:
        file.write(f"\n{entry}\n{filename}") # Writes entry and filename on new lines

def LoadFile(raw_filename, textwidget):
    """
    Load a new file from the current directory (where executable is located).
    """
    if ((raw_filename == "Untitled file") or (len(raw_filename) == 0)): # either left alone of they deleted the entry
        filename = "Untitled.txt"
    else:
        catch = re.search(r"(.+)(\..+)?$",raw_filename) # capture the filename itself and extension if there is one (optional)
        filename = catch.group(1) + ".txt"
    
    try: # attempts to read called file and insert text into Text Widget, otherwise fails and updates status
        with open(filename, "r") as file:
            fileContent = file.read() 
            textwidget.delete("1.0", "end") # clear widget text
            textwidget.insert("1.0", fileContent) # insert all content from loaded file request
            UpdateStatus("File Loaded") # update after successful load 
    except FileNotFoundError:
        UpdateStatus("File Couldn't Be Found")
        messagebox.showerror("Could not load called file.", "The file you requested doesn't exist or has an incorrect path. Try again.")

def NewFile(raw_filename):
    """
    Create a new empty file of a specified name.
    """
    if ((raw_filename == "Untitled file") or (len(raw_filename) == 0)): # either left alone of they deleted the entry
        filename = "Untitled"
    else:
        catch = re.search(r"(.+)(\..+)?$",raw_filename) # capture the filename itself and extension if there is one (optional)
        filename = catch.group(1)
    f = open(f"{filename}.txt", "x") # create a new file in local directory, can be opened in LoadFile
    UpdateStatus("File Created")

# Main UI Handling/Creation Stuff
def RootCreate(UsernameEntry, text_colour, bg_colour, filename="Untitled File", SavedEntry=f"{pyjotver}: get jotting (hehe) :D"):
    """
    Creates and places all onscreen widgets on root startup.
    """

    print("Root created.") # Debug message

    # Handling events in window
    root.protocol("WM_DELETE_WINDOW", lambda: ExitApp()) # If the user ever tries closing the application, we attempt to prompt a save :), takes text entry to compare with credential file (last save done!)
    
    # Misc/Pretty things
    SystemDate = tk.Label(root, text= datetime.today().strftime("%Y-%m-%d"), font=MainFont, bg=bg_colour, fg= text_colour)
    Username = tk.Label(root, text=UsernameEntry, font=MainFont, bg=bg_colour, fg= text_colour)
    
    # Creating text entries
    text_interface = tk.Text(root, wrap="word") # Wrap allows word wrapping inside Text widget

    # Binding undo/redo events for later use
    text_interface.bind("<Control-z>", lambda event: Undo(text_interface.get(1.0, "end-1c"), text_interface)) # Undo text input in Text widget
    text_interface.bind("<Control-y>", lambda event: Redo(text_interface.get(1.0, "end-1c"), text_interface)) # Redo text input in Text widget
    text_interface.bind("<<Modified>>", lambda event: SaveModifiedText(text_interface.get(1.0, "end-1c"))) # See function docstring

    filename_entry = tk.Entry(root)

    # Creating buttons
    saveFile_button = tk.Button(root, text="SAVE FILE", font=MainFont, bg=bg_colour, fg= text_colour, command=lambda: [SaveFile(text_interface.get(1.0, "end-1c"), filename_entry.get())]) # get text entry from start to finish
    loadFile_button = tk.Button(root, text="LOAD FILE", font=MainFont, bg=bg_colour, fg= text_colour, command=lambda: [LoadFile(filename_entry.get(), text_interface)]) # temp command
    newFile_button = tk.Button(root, text="NEW FILE", font=MainFont, bg=bg_colour, fg= text_colour, command=lambda: [NewFile(filename_entry.get())]) # temp command
    
    help_button = tk.Button(root, text="Need Help?", font=MainFont, bg=bg_colour, fg= text_colour, command=lambda: messagebox.showinfo("Help has arrived :)", "The file entry box (Top Left of the GUI) is where you must specify your file path (if your current text file is in a different directory).\n\nWhatever file is typed in their (no need for file extensions!) will be what is either saved, loaded, or created (with that name in the local directory of this executable).\n\n\nIMPORTANT NOTE:\n\nUndo/redo is very experimental and bugs out occassionally (e.g. undo redoing text, inability to undo actions, etc).\n\nIt shouldn't totally ruin your notes, but don't expect it to precisely undo/redo actions :)"))
    resetSettings_button = tk.Button(root, text="Reset\nSettings?", font=MainFont, background="#d66363", command=lambda: BeforeResetSettings())
    spellcheck_button = tk.Button(root, text="Spell Check?", font=MainFont, bg=bg_colour, fg= text_colour, command=lambda: SpellCheck(text_interface.get(1.0, "end-1c")))
    exit_button = tk.Button(root, background="#d66363", text="EXIT", font=MainFont, command=ExitApp)
    
    # Packing Area
    text_interface.pack(fill="both",expand=True,padx=(110,20),pady=(50,13))
    text_interface.insert(1.0, SavedEntry)
    text_interface.configure(font=TextFont, bg=bg_colour, fg= text_colour)
        # Fill allows the widget to expand to fill the root window
        # Expand allows the widget to resize to the applications' window size (i.e. responsize UI ig)
        # The .insert method is just to add some text on startup on a fresh file

    filename_entry.pack()
    filename_entry.insert(0, filename) # default entry
    filename_entry.configure(font=TextFont, bg=bg_colour, fg= text_colour)

    SystemDate.pack()
    Username.pack()
    
    saveFile_button.pack()
    loadFile_button.pack()
    newFile_button.pack()
    help_button.pack()
    resetSettings_button.pack()
    spellcheck_button.pack()
    exit_button.pack()

    # Placement Area
    filename_entry.place(x=450,y=10, width=130) # perfect fit
    SystemDate.place(x=10,y=350)
    Username.place(x=10,y=370)
    saveFile_button.place(x=10,y=10,width=80)
    loadFile_button.place(x=10,y=50,width=80)
    newFile_button.place(x=10,y=90,width=80)
    help_button.place(x=10, y=265, width=80)
    resetSettings_button.place(x=10, y=305, width=80, height=40)
    spellcheck_button.place(x=10, y=130, width=80)
    exit_button.place(x=10,y=170, width=80)

# Function Calls
OnAppOpen() # Verifies user credentials on first startup

# Handle user interaction in event loop while root is open
root.mainloop()