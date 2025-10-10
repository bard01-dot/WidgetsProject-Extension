# Widgets Project Extension
import psutil
import threading
import time
import requests
import json
import os
import pystray
import ctypes
from pystray import Icon, MenuItem as item, Menu
from PIL import Image, ImageDraw
import winreg
import sys
import logging
import GPUtil

import subprocess
import shutil
import webbrowser

from flask import Flask, request, render_template
from flask_cors import CORS





""" 
ChangeLog

[ 2.0.2 ]==========================================
- new todo-list

[ 2.0.3 ]==========================================
- fixed todo-list Style
- small changes on buttons hovers colors
- added debug button to change console visibility and check possible errors
- added open Folder button to open Wallpaper directory
- new checkbox style for settings
- avoid exiting the Settings menu when defining settings for the first time to prevent errors.

[ 2.0.4 ]==========================================
- fixed possible error at Open wallpaper directory
- updated wp-extension tutorial video on readme
- added tutorial button at define settings for first time

[ 2.0.5 ]==========================================
- app run over flask local server so now it dont require add wallpaper folder for work
- todo-notes saved on settings.json
- weather is now integrated inside the wallpaper
- added battery display in usage

[ 2.0.6 ]==========================================
- Added some prints in __main__ to more easily monitor possible errors
- Removed LocalHost request prints 
- small style changes in menu
- added version on window title
- added Search browser function
- added Shortcuts menu

[ 2.0.7 ]==========================================
- Fixed startup option

[ 2.0.8 ]==========================================
- Shortcuts now support executable files (images/.exe/etc)
- Fixed resources not found at startup (use load_icons function while images resource not found)

[ 2.0.9 ]==========================================
- Fixed possible error at check latest version

[ 2.0.10 ]==========================================
- Added GPU usage

[ 2.0.11 ]==========================================
- Fixed possible error at return GPU usage

[ 2.0.12 ]==========================================
- Prevent the extension from opening repeatedly. The checkExist() module now checks
  to see if the application is already running and displays the menu when necessary.
- small changes on preload console message

[ 2.0.13 ]==========================================
- new web ui
- fixed frozen ui in windows 11
- new integrations inside the wallpaper (logs and update checkbox without open menu, etc)
- removed GPU usage (incompatibilities with hide console)
- resources integrated inside the .exe
- new icons for shortcut
- added option for drag and modify tasks/shortcuts positions
- fixed error at check latest version
"""
#os.chdir("C:/") # test startup resource not found

# -----------------------
# define var
running = True # thread monitor cpu

global start_on_startup, settings, PcUsage, start_time, color_shortcut, logs, isLatestVersion
start_on_startup = False 
tasks = [] 
shortcuts = [] 
version = "2.0.13"
PcUsage = [0, 0]
color_shortcut = "#AB886D"
logs = ""
isLatestVersion = False

global consoleVisibility, broweserSearch
consoleVisibility = False
broweserSearch = "https://www.google.com/search?q="  # some examples:  https://duckduckgo.com/?&q= | https://www.bing.com/search?q= | https://search.yahoo.com/search?p= | https://search.aol.com/aol/search?q=

# default settings for json
settings = {
    "start_on_startup": start_on_startup,
    "browser": broweserSearch,
    "todo_list": tasks,
    "shortcuts_list": shortcuts
}

# GeneralFunctions ########################################################################
def openLink(link):# Open stuff
    if link.startswith(("https://", "http://")):  # open links
        os.system(f'start "" "{link}"')
    elif os.path.isdir(link):  # open directorys
        os.startfile(os.path.realpath(link))
    elif os.path.isfile(link):  # open files
        os.startfile(link)
    else:
        print(f"Error at open: {link}.")
      
class style():# class styles for console message with colors 
    RED = '\033[31m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'
    DIV = '\033[100m \033[90m'

def console_visibility(var): # change consolve visibility
    global consoleVisibility

    if(var == 3):# get oposite
        if(consoleVisibility) == 1: var = 2
        else: var = 1

    consoleVisibility = var

    if(var == 1):
        show = 5#Show Console
    else:
        show = 0#Hide Console

    hwnd = ctypes.windll.kernel32.GetConsoleWindow() 
    if hwnd != 0:
        ctypes.windll.user32.ShowWindow(hwnd, show)  # SW_SHOW = 5

def print_Error(e):# show error with format
    #console_visibility(1)
    os.system(f"title Widgets Project v{version} && cls")
    print(style.RED + "\n *" + style.ENDC +" An error occurred " + style.RED + f"\n ------------------------------------" + style.ENDC);
    
    print("")
    print(style.DIV + "|                                                                            |"+ style.ENDC)
    print("")
    print(f"{e}")
    print("")
    print(style.DIV + "|                                                                            |"+ style.ENDC)
    print("\n - Report error on Discord: " + style.OKBLUE + " https://discord.com/invite/63EUyQBZPm"+ style.ENDC)
    print("")
    
    
    #logs += f"<li class='task' style='background-color: #4a4a4a2e;'> Report this error on discord: https://discord.com/invite/63EUyQBZPm </li>"

    #input("Press Enter to exit...")
    

def exit_app():# exit function
    os._exit(0)

def getCurrentVersion():# return current version for notify updates
    url = "https://raw.githubusercontent.com/NicouHc/WidgetsProject-Extension/main/resources/version.txt"
    try:
        content = requests.get(url).text
    except:
        content = version
        pass

    global isLatestVersion
    isLatestVersion = version == content
    
    
    global logs
    if( isLatestVersion == False):
        logs += f"""<li class='task' style='color: white;padding: 10px;text-align: center;display:flex;background-color: #715a5a18'>
                <svg viewBox="0 0 48 48" style="width: 20px; fill: white">
                        <path d="M0 0h48v48H0z" fill="none"></path>
                        <path d="M46 24l-4.88-5.56.68-7.37-7.22-1.63-3.78-6.36L24 6l-6.8-2.92-3.78 6.36-7.22 1.63.68 7.37L2 24l4.88 5.56-.68 7.37 7.22 1.63 3.78 6.36L24 42l6.8 2.92 3.78-6.36 7.22-1.63-.68-7.37L46 24zM26 34h-4v-4h4v4zm0-8h-4V14h4v12z"></path>
                </svg>
                <a style="margin-left:6px"> New version is available </a>
                </li>"""

def obtain_current_dir():# define current path
    if getattr(sys, 'frozen', False):
        # if the file is .exe
        return os.path.dirname(sys.argv[0])
    else:
        # if file is .py script
        return os.path.dirname(os.path.abspath(__file__))

def defineStartupTime():# define the PC startup time 
    def Get_Pid():
        # note: use the sihost process start time to define when the pc startup because psutil.boot_time() display the time wrong 
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'sihost.exe':
                return proc.info['pid']

    global start_time
    start_time = psutil.Process(Get_Pid()).create_time()

def checkExist(): # check if Extension Already running
    try:
        response = requests.get('http://127.0.0.1:5000/exist', timeout=3)
        if response.status_code == 200:
            print("Extension Already running, Closing Process")
            exit_app()
      
    except requests.exceptions.RequestException as e:
        #print("Error:", e)
        pass

def printLogs(text, error):# save web logs
    global logs

    if (error == True):
        logs += f"""
        <li class='task' style='color: white;padding: 10px;text-align: center;background-color: #715a5a18;'>
        <a style="margin-left:6px">Error Found</a></li>
        <li class='task' style='background-color: #715a5a18;'> {text} </li>"""
    else:
        logs += f"<li class='task'>▸ {text}</li>"

def updateOrder(setting, data):  # change task/shortcut order
    global tasks, shortcuts
    data = request.get_json()

    if not data or 'order' not in data:
        print("> no-data to order")
        return "0"

    # Seleccionar lista y campo clave
    if setting == "shortcuts":
        tofind = shortcuts
        key = "name"
    else:
        tofind = tasks
        key = "text"

    new_order = data['order']

    # Reordenar elementos según la lista 'order'
    new_items = [t for text in new_order for t in tofind if t.get(key) == text]
    
    # Reemplazar la lista global
    if setting == "shortcuts":
        shortcuts = new_items
    else:
        tasks = new_items

    save_settings()
    return "1"



# Notes Functions #########################################################################
def add_task(task_text):  # add new task
    global tasks
    task_text = task_text.strip()
    
    if not task_text: # if empty -> dont add text
        return 
    
    # verify repeated notes
    if any(t['text'].strip().lower() == task_text.lower() for t in tasks):
        printLogs("ToDo-Notes | Cannot create Tasks with repeated name: " + task_text, True)
        return

    tasks.append({'text': task_text, 'checked': False})
    save_settings()

def delete_task(index):# delete task
    global tasks
    del tasks[index]
    save_settings()

def toggle_task(index):# update checked status
    global tasks
    print(index);
    tasks[index]['checked'] = not tasks[index]['checked']
    
    save_settings()




# shortcuts Functions #####################################################################
def add_shortcut(icon, directory, shortcut_name, color):
    global shortcuts
    if directory and shortcut_name and icon:
        
        # verify repeated notes
        if any(t['name'].strip().lower() == shortcut_name.lower() for t in shortcuts):
            printLogs("Shortcuts | Cannot create Shortcuts with repeated name: " + shortcut_name, True)
            return

        directory = directory.replace("\\", "/")
        shortcuts.append({'icon': icon, 'name': f"{shortcut_name}", 'directory': f'{directory}', 'color':  f'{color}'})

        save_settings()

def delete_shortcut(index):# delete task
    global shortcuts
    del shortcuts[index]
    save_settings()




# Update Info functions ###################################################################
def obtener_info(intervalo=1): # obtain pc performance %
    def startup():
        global start_time
        current_time = time.time()
        # Calcular el tiempo transcurrido desde el arranque
        elapsed_time = current_time - start_time
        # Convertir a horas y minutos
        mins, sec = divmod(elapsed_time, 60)
        hour, mins = divmod(mins, 60)
        return hour, mins

    while running:
        uso_cpu = psutil.cpu_percent(interval=intervalo)
        uso_ram = psutil.virtual_memory().percent
        
        battery = psutil.sensors_battery()
        upTime = startup()

        if battery:
            battery = battery.percent
        else:
            battery = -1
        
        # Obtener información de la GPU usando GPUtil
        """
        gpus = GPUtil.getGPUs()
        if gpus:
            # En este ejemplo, se usa la primera GPU detectada
            gpu = gpus[0]
            gpu_usage = gpu.load * 100  # porcentaje de uso
            gpu_mem_usage = (gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal else 0

            # test force NaN
            #gpu_usage = float('nan')
            
            #Prevent Nan Values
            if gpu_usage != gpu_usage:
                gpu_usage = 0
            if gpu_mem_usage != gpu_mem_usage:
                gpu_mem_usage = 0

            gpu_info = f"{gpu_usage:.1f}"
            # {gpu_mem_usage:.1f}% memory
        else:
            gpu_info = "0"
        """

        gpu_info = 0

        # Generar el arreglo de información
        global PcUsage
        PcUsage = f"[{uso_cpu}, {uso_ram}, {battery}, {upTime[0]}, {upTime[1]}, {gpu_info}]"
        time.sleep(1)  # zzz




# Settings Functions ######################################################################
def load_settings(file_path):#  load json settings
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            global start_on_startup, tasks, settings, broweserSearch, shortcuts

            settings = json.load(file)
            start_on_startup = settings.get('start_on_startup', False)
            tasks = settings.get('todo_list', [])
            shortcuts = settings.get('shortcuts_list', [])
            broweserSearch = settings.get('browser', "https://www.google.com/search?q=")
            return settings
    else:
        return None

def save_settings():# save json 

    global currentPath
    global start_on_startup, settings, broweserSearch, shortcuts, tasks

    settings = {
        "start_on_startup": start_on_startup,
        "browser": broweserSearch,
        "todo_list": tasks,
        "shortcuts_list": shortcuts
    }

    with open(currentPath + '/settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

def set_startup(value):# define start program on pc startup
    script_path = currentPath + "\\" + os.path.basename(sys.argv[0]) # Obtain .exe path
    print(script_path)

    key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    regName = "WidgetsProjectExtension"  # define registry name

    try:
        # open registry key
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
        
        if value:
            # define value
            winreg.SetValueEx(reg_key, regName, 0, winreg.REG_SZ, script_path)
            print("[i] Program startup 1.")
        else:
            # try delete the registry 
            try:
                winreg.DeleteValue(reg_key, regName)
                print("[i] Program startup 0.")
            except:
                # key dont exist
                pass
            
        
        # close registry
        winreg.CloseKey(reg_key)
    except Exception as e:
        print_Error("Startup setting error - Reg key not found \n" + str(e))


# START ALL ################################################################################
def preLoad():#load settings before start the program
    global settings
    file_path = currentPath + '/settings.json'
    jsonSettings = load_settings(file_path)

    # if json dont exist create file with default settings 
    if not jsonSettings:
        save_settings() 
    
def start_threads():# start cpu/ram/gpu threads
        global running
        
        cpuUsage = threading.Thread(target=obtener_info)
        
        if not cpuUsage.is_alive():
            running = True
            cpuUsage.start()
        else:
            pass
            
def create_placeholder_icon(size=64, color=(130, 90, 90)):
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, size - 8, size - 8), fill=color)
    return image

def tricon(): #tryicon
    menu = Menu(
        item('Home Menu', lambda: open_in_app_window("http://127.0.0.1:5000/", "homeMenu")),
        item('Exit', exit_app)
    )

    icon_image = create_placeholder_icon()
    icon = Icon("Widgets Project", icon_image, "Widgets Project", menu)
    
    start_threads()
    icon.run()




# flask ################################################################################
# Detect PyInstaller
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

template_folder = os.path.join(base_path, "templates")
static_folder = os.path.join(base_path, "static")

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)


# add shortcut
@app.route('/shortcutAdd', methods=['POST'])
def action_shortcut():
    content = request.get_json().get("data")
    name = request.get_json().get("name")
    color = request.get_json().get("color")
    icon = request.get_json().get("icon").replace("shortcut","")

    add_shortcut(icon, content, name, color)

    return("1")
# del shortcut
@app.route('/deleteShortcut', methods=['POST'])
def action_delete_shortcut():
    index = request.get_json().get("data")
    delete_shortcut(index)
    return("1")
# update shortcut order
@app.route('/updateShortcutsOrder', methods=['POST'])
def update_shortcut_order():
    data = request.get_json()
    updateOrder("shortcuts", data)
    return("1")



# add notes
@app.route('/notesAdd', methods=['POST'])
def action_notes():
    data = request.get_json().get("data")  # obtain folder to open
    add_task(data)
    return("1")
# del notes
@app.route('/deleteNote', methods=['POST'])
def action_delete_note():
    index = request.get_json().get("data")
    delete_task(index)
    return("1")
# checkbox notes
@app.route('/changeCheckbox', methods=['POST'])
def action_toggle_note():
    index = request.get_json().get("data")
    toggle_task(index)
    
    return("1")
#update notes order
@app.route('/updateNotesOrder', methods=['POST'])
def update_notes_order():
    data = request.get_json()
    updateOrder("tasks", data)
    return("1")



# update startup // open settings 
@app.route('/updateSetting', methods=['POST'])
def update_settings():
    index = request.get_json().get("data")

    if(index == "startup"):
        global start_on_startup
        start_on_startup = not start_on_startup
        set_startup(start_on_startup)
        save_settings() 

        printLogs(f"Start on Startup: {start_on_startup}", False)# print logs
        
    elif(index == "searchEngine"): # open search engine
        open_in_app_window("http://127.0.0.1:5000/", "settingsMenu")

    
    return("1")

# save search engine
@app.route('/SearchEngine', methods=['POST'])
def update_searchEngine():
    global broweserSearch
    data = request.get_json().get("data")  # obtain folder to open
    broweserSearch = data
    save_settings()

    printLogs(f"Search Engine Update: {broweserSearch}", False)# print logs

    return("1")



# open menu if already running
@app.route('/exist', methods=['GET'])
def exist():
    open_in_app_window("http://127.0.0.1:5000/", "homeMenu")
    return 'ok', 200

# display cpu ram usage
@app.route('/usage', methods=['GET'])
def get_usage():
    global PcUsage
    return PcUsage

# display notes
@app.route('/notes', methods=['GET'])
def get_notes():
    global tasks
    return json.dumps(tasks, ensure_ascii=False)

# display shortcuts
@app.route('/shortcuts', methods=['GET'])
def get_shortcuts():
    global shortcuts
    return json.dumps(shortcuts, ensure_ascii=False)

# display logs
@app.route('/logs', methods=['GET'])
def get_logs():
    global logs
    return json.dumps(logs, ensure_ascii=False)

# open folders/ ui specific menus
@app.route('/openStuff', methods=['POST'])
def open_stuff():
    data = request.get_json().get("data")  # obtain information
    
    # open menu 
    if(data == "Search"): #open mini browser
        open_in_app_window("http://127.0.0.1:5000/", "searchEngine")

    elif(data == "myNotesList"): # open note list
        open_in_app_window("http://127.0.0.1:5000/", "notesMenu")
        
    elif(data == "shortcutList"): # open note list
        open_in_app_window("http://127.0.0.1:5000/", "shortcutsMenu")

    elif(data == "homeMenu"): # open search engine
        open_in_app_window("http://127.0.0.1:5000/", "homeMenu")

    # open directorys 
    elif(data == "Desktop"):
        path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        openLink(path)

    elif(data == "Documents"):
        path = os.path.join(os.environ['USERPROFILE'], 'Documents')
        openLink(path)

    elif(data == "Downloads"):
        path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        openLink(path)
    
    elif(data == "Terminal"):
        os.system("start cmd")


    else:
        openLink(data)

    return("1")



# run localhost
def run_flask_app():
    app.run(host='127.0.0.1', port=5000)

# open index menu
@app.route('/')
def index():
    
    global start_on_startup, broweserSearch, isLatestVersion
    panel = request.args.get("panel", "defaultPanel")
    return render_template("index.html", panel=panel, startup=start_on_startup, browser=broweserSearch, update=isLatestVersion)

# open ui
def open_in_app_window(url, ventana):

    global start_on_startup, broweserSearch, isLatestVersion
    url_con_panel = f"{url}?panel={ventana}&startup={start_on_startup}&browser={broweserSearch}&update={isLatestVersion}"  # construye la URL con el panel

    browsers = [
        ("chrome", ["--app=" + url_con_panel]),
        (r"C:\Program Files\Google\Chrome\Application\chrome.exe", ["--app=" + url_con_panel]),
        (r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", ["--app=" + url_con_panel]),
        (r"C:\Program Files\Opera\launcher.exe", ["--app=" + url_con_panel]),
        ("msedge", ["--app=" + url_con_panel]),
        (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", ["--app=" + url_con_panel]),
    ]

    for browser, args in browsers:
        browser_path = shutil.which(browser) if "\\" not in browser else browser
        if browser_path and os.path.exists(browser_path):
            subprocess.Popen([browser_path] + args)
            return


    # fallback
    webbrowser.open(url_con_panel +  ",--disable-resize")

# exit via post
@app.route('/exit', methods=['POST'])
def exitapp():  # función para cerrar la app
    exit_app()
    return 1




# main ################################################################################
if __name__ == "__main__":
    try:
        
        os.system(f"title Widgets Project v{version} && cls")
        print(style.RED + f"\n - Widgets Project Extension v{version}\n ------------------------------------ \n" + style.ENDC)
        logs += f"""<li class='task' style='color: white;padding: 10px;text-align: center;'>
        <svg viewBox="0 0 24 24" style="fill: #715A5A; width:10px"><path d="M3 0v1.5H1.5V3H0v12h3v3h3v3h3v3h6v-3h3v-3h3v-3h3V3h-1.5V1.5H21V0h-3v1.5h-3V3h-1.5v3h-3V3H9V1.5H6V0z"/></svg>
        <a style="margin-left:6px">Widgets Project Extension <b style="color:#715A5A;margin-left:5px"> v{version}</b></a>
        </li>"""
       

        #print(style.RED + " * ▸" + style.ENDC + " Console Visibility")
        #logs += "<li class='task'> ▸ Console Visibility </li>"
        #console_visibility(2)
 
        # save execute time (to check if is updated in wpp)
        #logs +=  f"<li class='task'> ▸  {time.strftime('%H:%M:%S', time.localtime())} </li>"
        logs += f"""<li class='task' style='color: white;padding: 10px;text-align: center;display:flex;background-color:#715a5a18'>
            <svg viewBox="0 0 24 24" style="width: 18px; fill: white">
                <path d="M12,0C5.4,0,0,5.4,0,12c0,6.6,5.4,12,12,12s12-5.4,12-12C24,5.4,18.6,0,12,0z M12,21c-5,0-9-4-9-9c0-5,4-9,9-9s9,4,9,9    C21,17,17,21,12,21z"/><path d="M14,11.2V7c0-1.1-0.9-2-2-2s-2,0.9-2,2v5c0,0.5,0.2,1,0.6,1.4l3,3C14,16.8,14.5,17,15,17s1-0.2,1.4-0.6    c0.8-0.8,0.8-2,0-2.8L14,11.2z"/>
            </svg>
            <a style="margin-left:6px"> ▸  {time.strftime('%I:%M:%S %p', time.localtime())}  </a>
            </li>"""


        print(style.RED + " * ▸" + style.ENDC + " Check if extension is already running")
        logs += "<li class='task'> ▸ Check if Extension is already Running </li>"
        checkExist()


        print(style.RED + " * ▸" + style.ENDC +  " Current Path")
        logs += "<li class='task'> ▸ Define Current Path </li>"
        currentPath = obtain_current_dir()

        print(style.RED + " * ▸" + style.ENDC +  " Define Startup Time")
        logs += "<li class='task'> ▸ Define Startup Time </li>"
        defineStartupTime()

        print(style.RED + " * ▸" + style.ENDC +  " LocalHost sv")
        logs += "<li class='task'>  ▸ Starting LocalHost Server </li>"
        logger = logging.getLogger('werkzeug')
        logger.setLevel(logging.ERROR)  # prevent show  flask requests messages in debug console
        threading.Thread(target=run_flask_app).start() # start flask thread

        print(style.RED + " * ▸" + style.ENDC +  " .json settings")
        logs += "<li class='task'>  ▸ Loading .Json Settings </li>"
        preLoad()  # load settings

        print(style.RED + "\n * ▸" + style.ENDC +  " Check For Updates \n")
        logs += "<li class='task'>  ▸ Check For Updates </li>"
        getCurrentVersion()

        print(style.RED + "\n * ▸" + style.ENDC +  " tryicon menu\n")
        logs += "<li class='task'>  ▸ Starting Extension </li>"
        tricon()  # display tryicon menu

        

        #print_Error("test")
        
    except Exception as e: 
        print_Error(e) # print error console
        printLogs(e, True) # print logs in web logs
        time.sleep(5) # sleep 5s 
        exit_app() # exit app