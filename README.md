![Logo](/resources/banner.png)

# Description

**Widgets Project Extension** is an executable that complements wallpapers of Wallpaper Engine and that allows you to access more options like, system information shortcuts and to-do notes. These widgets update in real time and are highly configurable through an intuitive panel.

- if you have any question you can join our [Discord](https://discord.com/invite/63EUyQBZPm)
- Buy me a coffe [**Paypal❤️**](https://www.paypal.com/donate/?hosted_button_id=UBDDRKEZ4XABE)
- Some Wallpapers wich use this extension: [Widgets Project Wallpaper](https://steamcommunity.com/sharedfiles/filedetails/?id=3137947556), [Noise Widgets](https://steamcommunity.com/sharedfiles/filedetails/?id=3584432338)


# Features

- **CPU and RAM Monitoring**: Displays real-time CPU and RAM usage.
- **Battery Charge**: Displays current Battery Charge percent.
- **ToDo Notes**: Manage your notes directly from the Extension.
- **Shortcuts**: Create and display your own shortcuts inside the wallpaper.
- **Search Bar**: Just a search bar for find information.
- **Easy Configuration**: Customize the project settings through a user-friendly graphical interface.


# Preview
<img src="/resources/notes.gif" alt="Notes Example" width="500"/>
<img src="/resources/shortcuts.gif" alt="shortcuts example" width="500"/>



# How It Works
- **On the Script Side**: It retrieves system information using the `psutil` library, such as CPU usage, RAM usage, and battery charge. It also manages a to-do list and can display custom notes or other relevant data that the user wants to track. Using `Flask` as a local server, the script sends this information via localhost, allowing the wallpaper to fetch and display it in real-time.

- **On the Wallpaper Side**:  The wallpaper uses javaScripts `fetch` to periodically request the system information from the LocalHost. This enables the wallpaper to dynamically update and display CPU, memory, battery usage, and any user-defined notes or to-do items, providing a real-time system monitor right on the desktop.


# Use the Extension in Your Own Wallpaper

This is a simple example about how you can use the Extension in your own web wallpapers
<details>
<summary>Request ToDo Notes</summary>

1. Execute the Extension
2. Create a new Note
3. Execute the js in web Wallpaper or .html file to request the information

```js
const content = await fetch("http://127.0.0.1:5000/notes"); // request list of notes
todoNotes = await content.json();

if (Array.isArray(todoNotes)) {
    notes.forEach((note, index) => {
      if (note.text.trim() !== "") {
        
        console.log(`Note Content: ${note.text}`);
        console.log(`Note CheckBox: ${note.checked}`);
        console.log(`Note Index: ${note.index}`); // taked from forEch

      }
    });
}
```

</details>

<details>
<summary>Request Pc Usage</summary>

1. Execute the Extension
2. Execute the js in web Wallpaper to request the information
 
```js

async function refreshInfo() {
    try {
        // reques values
        const content = await fetch("http://127.0.0.1:5000/usage");
        usage = await content.json();
        
        // define individual values
        var cpuUsage = usage[0];
        var ramUsage = usage[1];
        var batteryUsage = usage[2];
        var startupTime = `up ${usage[3]} hours, ${usage[4]} minutes`;

        // show in console
        console.log("Cpu Usage: " + cpuUsage + "%");
        console.log("Ram Usage: " + ramUsage + "%");
        console.log("Battery: " + batteryUsage  + "%");
        console.log("StartUp Time: " + startupTime);

        // the app have gpu usage (GPUUsage = usage[5];) but its temporaly disabled for incompatibilitys with the ui
    }


    const interval = 5000; // 5 seconds
    setInterval(function(){refreshInfo();}, interval);// refresh usage every <interval> seconds
}

```

</details>

<br>

# More info about Methods

### Request Basic Values
| Interactions |  Format | Parameter | Description | Example |
| :------ | :------ | :-------- | :----- | :---------- |
| /usage  | array  | Get | Return Pc Usage  | ```[cpu, ram, battery, upTime hours, upTime minutes, gpu]```
| /notes  | json  | Get | Return list of ToDo-Notes  | ```[{"text": "content", "checked": false}]```
| /shortcuts  | json  | Get | Return List of Shortcuts  | ```[{svg icon, name, directory, color}]```

### ShortCuts
Additionally, I use some methods to make the app (web UI) interact with the .py script, or to make the wallpaper interact directly with the script.
| Interactions| Parameter | json key |  Description | Example |
| :------ | :------------ | :------- | :----------- | :---------- |
| /shortcutAdd | Post | name, content, color, icon |  **Add** new shortcut from webui | fetch json -> name:yourname, content: yourDirectory, color: #ffffff, icon: svg
| /deleteShortcut | Post | data |  **Delete** shortcut from shortcut index (json key: data) | fetch -> data: index
| /updateShortcutsOrder | Post | order |  Change Shortcut **position**; Drag shortcut from webui and return new position so the py can change the order | order: [ShortcutName, OtherShortcut]

### ToDo Notes
| Interactions | json key |  Description 
| :----------- |:-------- | :----------- |
| /notesAdd | data = ```your note content here``` |**Add** new note to ToDo List 
| /deleteNote | data = index  |**Delete** note using index 
| /changeCheckbox | data = index | Change Note **Status** for oposite (Checked/unCheck) 
| /updateNotesOrder| order = [note1, note2] | Change notes **position** (same as shortcuts)

### Open stuff
This is a method used to comunicate the wallpaper with the script so we can Open **Shorctus**, **Links** or the **App** Directly from the wallpaper **(^o^)7**
| Interactions | json key | Description |
| :------ | :------------ | :---------- |
| /openStuff  | data = Desktop  | open desktop folder (this is a default form the program)
| /openStuff  | data = ```your directory here```  | open folder directory or executable
| /openStuff  | data = ```link here```  | open link only if start with `https://` or `http://`
| /openStuff | data =  homeMenu | Open UI in Home Menu
| /openStuff | data = myNotesList | Open UI in TodoList Menu
| /openStuff | data = shortcutList |  Open UI in Shortcut List
| /openStuff | data = ```searchEngine``` | Open compact Web Browser


### Others
There are also other methods like ```/updateSetting``` wich is used in the WebUi to interact wit the settings to switch values like **Execute app on Pc startup** or open the setting menu<br>
```/SearchEngine``` wich **define new Search Engine** for the Compact browser widget (update settings).<br>
```/exist``` wich i use to check if the app is already running and thats it.