import os
import shutil
import time
import tkinter.filedialog as fd
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from collections import defaultdict
import subprocess
import tkinter as tk
import sys
from PIL import Image, ImageTk

#for making installer
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Check if Windows Recycle Bin is available
try:
    import winshell  # Windows-only module
    WINDOWS_RECYCLE_BIN = True
except ImportError:
    WINDOWS_RECYCLE_BIN = False  # If module is missing, assume no Recycle Bin

# Define Trash Folder for non-Windows or if Recycle Bin is not available
USER_TRASH_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "Trash")
if not WINDOWS_RECYCLE_BIN and not os.path.exists(USER_TRASH_FOLDER):
    os.makedirs(USER_TRASH_FOLDER)  # Create Trash folder

# Initialize app
set_appearance_mode("dark")
set_default_color_theme("blue")

app = CTk()
app.title("File Management System")
app.geometry("800x800")
app.iconbitmap(resource_path("images\\icon.ico"))

app.resizable(False, False)
app.attributes("-topmost", True)  
app.attributes("-fullscreen", False)  

# Assign separate hotkeys

image_path = resource_path("images\\image.jpg")  # Ensure this matches your file name
img = Image.open(image_path)
img = img.resize((800, 800), Image.LANCZOS)  # Resize to fit your right panel
img = ImageTk.PhotoImage(img)

# Create label for image
image_label = tk.Label(app, image=img, bg="black")
image_label.place(x=250, y=0)

# Sidebar Frame
sidebar = CTkFrame(app, width=300, corner_radius=0)
sidebar.pack(side="left", fill="y")

# Function to create section labels
def create_section_label(parent, text):
    label = CTkLabel(parent, text=text, font=("Arial", 14, "bold"), anchor="w")
    label.pack(fill="x", padx=10, pady=(15, 5))

# Function to create dividers
def divider():
    CTkLabel(sidebar, text="─" * 30, font=("Arial", 12, "bold"), anchor="center").pack(fill="x", padx=10, pady=5)

# Function to create buttons
def create_sidebar_button(parent, text, command=None):
    button = CTkButton(parent, text="   " + text, corner_radius=8, fg_color="gray30",
                       hover_color="gray40", text_color="white", command=command)
    button.pack(fill="x", padx=20, pady=3)

def show_message(title, message, icon):
    """Display a message box (error/success)."""
    CTkMessagebox(title=title, message=message, icon=icon)

def confirm_action(message):
    """Show a confirmation dialog and return user's choice."""
    confirm = CTkMessagebox(title="Confirmation", message=message, 
                            icon="warning", option_1="Yes", option_2="No")
    return confirm.get() == "Yes"

def upload_file():
    """Allow selecting multiple files."""
    selected_files = fd.askopenfilenames(title="Select files to upload")

    if not selected_files:
        show_message("Error", "No files selected!", "cancel")
        return

    show_message("Info", f"{len(selected_files)} file(s) selected successfully.\nNow you can perform file operations.", "check")

def move_file():
    """Move selected files to a chosen folder."""
    selected_files = fd.askopenfilenames(title="Select files to move")
    if not selected_files:
        show_message("Error", "No files selected!", "cancel")
        return

    destination_folder = fd.askdirectory(title="Select destination folder")
    if not destination_folder:
        show_message("Error", "No destination selected!", "cancel")
        return

    if confirm_action(f"Move {len(selected_files)} file(s) to {destination_folder}?"):
        success_count = 0
        for file_path in selected_files:
            try:
                shutil.move(file_path, destination_folder)
                success_count += 1
            except Exception as e:
                show_message("Error", f"Failed to move {file_path}:\n{e}", "cancel")

        show_message("Success", f"Moved {success_count} file(s) successfully!", "check")

def delete_file():
    """Move selected files to Trash instead of permanently deleting them."""
    selected_files = fd.askopenfilenames(title="Select files to delete")
    if not selected_files:
        show_message("Error", "No files selected!", "cancel")
        return

    if confirm_action(f"Move {len(selected_files)} file(s) to Trash?"):
        success_count = 0
        for file_path in selected_files:
            try:
                if WINDOWS_RECYCLE_BIN:
                    winshell.recycle_file(file_path)  # Move to Windows Recycle Bin
                else:
                    file_name = os.path.basename(file_path)
                    trash_path = os.path.join(USER_TRASH_FOLDER, file_name)

                    # Ensure unique name in Trash
                    count = 1
                    while os.path.exists(trash_path):
                        name, ext = os.path.splitext(file_name)
                        trash_path = os.path.join(USER_TRASH_FOLDER, f"{name}_{count}{ext}")
                        count += 1

                    shutil.move(file_path, trash_path)  # Move to Trash folder

                success_count += 1
            except Exception as e:
                show_message("Error", f"Failed to delete {file_path}:\n{e}", "cancel")

        show_message("Success", f"Moved {success_count} file(s) to Trash!", "check")

def rename_file():
    """Rename a selected file."""
    selected_file = fd.askopenfilename(title="Select a file to rename")
    if not selected_file:
        show_message("Error", "No file selected!", "cancel")
        return

    new_name = fd.asksaveasfilename(title="Enter new file name", initialdir=os.path.dirname(selected_file),
                                     initialfile=os.path.basename(selected_file), defaultextension="")
    if not new_name:
        show_message("Error", "No new name entered!", "cancel")
        return

    try:
        os.rename(selected_file, new_name)
        show_message("Success", "File renamed successfully!", "check")
    except Exception as e:
        show_message("Error", f"Failed to rename file: {e}", "cancel")

def restore_file():
    """Restore files from Trash to their original location."""
    if WINDOWS_RECYCLE_BIN:
        show_message("Info", "Windows Recycle Bin handles restoration manually.", "info")
        return

    trash_files = os.listdir(USER_TRASH_FOLDER)
    if not trash_files:
        show_message("Error", "Trash is empty!", "cancel")
        return

    selected_file = fd.askopenfilename(title="Select a file to restore", initialdir=USER_TRASH_FOLDER)
    if not selected_file:
        show_message("Error", "No file selected!", "cancel")
        return

    destination_folder = fd.askdirectory(title="Select restore location")
    if not destination_folder:
        show_message("Error", "No destination selected!", "cancel")
        return

    try:
        shutil.move(selected_file, destination_folder)
        show_message("Success", "File restored successfully!", "check")
    except Exception as e:
        show_message("Error", f"Failed to restore file: {e}", "cancel")

def clear_trash():
    """Permanently delete all files in Trash."""
    if WINDOWS_RECYCLE_BIN:
        show_message("Info", "Windows Recycle Bin handles emptying manually.", "info")
        return

    trash_files = os.listdir(USER_TRASH_FOLDER)
    if not trash_files:
        show_message("Error", "Trash is already empty!", "cancel")
        return

    if confirm_action("Are you sure you want to permanently delete all files in Trash?"):
        for file in trash_files:
            file_path = os.path.join(USER_TRASH_FOLDER, file)
            try:
                os.remove(file_path)
            except Exception as e:
                show_message("Error", f"Failed to delete {file}: {e}", "cancel")

        show_message("Success", "Trash emptied successfully!", "check")

def sort_by_name():
    """Sort files in a selected folder by name and display results in a scrollable window."""
    folder_path = fd.askdirectory(title="Select folder to sort")
    if not folder_path:
        show_message("Error", "No folder selected!", "cancel")
        return

    files = sorted(os.listdir(folder_path))  # Sort files alphabetically

    if not files:
        show_message("Info", "No files found in the selected folder.", "info")
        return

    # Create a new Toplevel window for displaying sorted files
    popup = CTkToplevel(app)
    popup.title("Sorted Files")
    popup.geometry("400x400")
    popup.attributes('-topmost', True)

    # Add a label
    CTkLabel(popup, text="Sorted Files:", font=("Arial", 14, "bold")).pack(pady=10)

    # Create a scrollable text box
    text_box = CTkTextbox(popup, wrap="none", height=300, width=350)
    text_box.pack(padx=10, pady=5, fill="both", expand=True)

    # Insert sorted filenames into the text box
    text_box.insert("1.0", "\n".join(files))
    text_box.configure(state="disabled")  # Make it read-only

    # Add a close button
    CTkButton(popup, text="Close", command=popup.destroy).pack(pady=10)

def sort_files_by_creation_date():
    """Sort files in a selected folder by creation date."""
    folder_path = fd.askdirectory(title="Select folder to sort")
    if not folder_path:
        show_message("Error", "No folder selected!", "cancel")
        return

    files = os.listdir(folder_path)
    if not files:
        show_message("Info", "No files found in the selected folder.", "info")
        return

    files_with_dates = []
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):  # Ensure it's a file, not a directory
            creation_time = os.path.getctime(file_path)
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(creation_time))
            files_with_dates.append((file, formatted_time))

    sorted_files = sorted(files_with_dates, key=lambda x: x[1])

    sorted_file_names = "\n".join([f"{file} - {date}" for file, date in sorted_files])
    show_message("Sorted Files", f"Files sorted by creation date:\n{sorted_file_names}", "check")

def sort_files_by_type():
    """Sort files in a selected folder by file type (extension)."""
    folder_path = fd.askdirectory(title="Select folder to sort")
    if not folder_path:
        show_message("Error", "No folder selected!", "cancel")
        return

    files = os.listdir(folder_path)
    if not files:
        show_message("Info", "No files found in the selected folder.", "info")
        return

    file_types = defaultdict(list)

    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):  # Ignore folders
            ext = os.path.splitext(file)[1] or "No Extension"
            file_types[ext].append(file)

    # Sort extensions and files alphabetically
    sorted_file_types = sorted(file_types.items())

    result_text = "\n".join([f"{ext}:\n  " + "\n  ".join(sorted(files)) for ext, files in sorted_file_types])

    show_message("Sorted Files", f"Files sorted by type:\n{result_text}", "check")

def create_folder():
    """Create a new folder in a selected directory."""
    selected_directory = fd.askdirectory(title="Select location to create folder")
    if not selected_directory:
        show_message("Error", "No location selected!", "cancel")
        return

    folder_name = fd.asksaveasfilename(title="Enter folder name", initialdir=selected_directory, defaultextension="")
    if not folder_name:
        show_message("Error", "No folder name entered!", "cancel")
        return

    folder_path = os.path.join(selected_directory, os.path.basename(folder_name))
    
    if os.path.exists(folder_path):
        show_message("Error", "Folder already exists!", "cancel")
    else:
        try:
            os.makedirs(folder_path)
            show_message("Success", "Folder created successfully!", "check")
        except Exception as e:
            show_message("Error", f"Failed to create folder: {e}", "cancel")

def rename_folder():
    """Rename a selected folder."""
    selected_folder = fd.askdirectory(title="Select a folder to rename")
    if not selected_folder:
        show_message("Error", "No folder selected!", "cancel")
        return

    parent_dir = os.path.dirname(selected_folder)
    old_folder_name = os.path.basename(selected_folder)

    new_folder_name = fd.asksaveasfilename(title="Enter new folder name", 
                                           initialdir=parent_dir, 
                                           initialfile=old_folder_name)
    
    if not new_folder_name:
        show_message("Error", "No new name entered!", "cancel")
        return

    new_folder_path = os.path.join(parent_dir, new_folder_name)

    try:
        os.rename(selected_folder, new_folder_path)
        show_message("Success", "Folder renamed successfully!", "check")
    except Exception as e:
        show_message("Error", f"Failed to rename folder: {e}", "cancel")

def search_files_folders():
    """Search for files and folders inside a selected directory."""
    global result_listbox, name_to_path  

    folder_path = fd.askdirectory(title="Select folder to search in")
    if not folder_path:
        show_message("Error", "No folder selected!", "cancel")
        return

    search_query = CTkInputDialog(title="Search", text="Enter search keyword:").get_input()
    if not search_query:
        show_message("Error", "No search keyword entered!", "cancel")
        return

    results = []
    for root, dirs, files in os.walk(folder_path):
        for name in dirs + files:
            if search_query.lower() in name.lower():
                results.append(os.path.join(root, name))

    if not results:
        show_message("Info", "No matching files or folders found.", "info")
        return

    popup = CTkToplevel(app)
    popup.title("Search Results")
    popup.geometry("500x400")
    popup.attributes('-topmost', True)

    CTkLabel(popup, text="Search Results:", font=("Arial", 14, "bold")).pack(pady=10)

    result_listbox = tk.Listbox(popup)  # Use Listbox instead of Textbox
    result_listbox.pack(padx=10, pady=5, fill="both", expand=True)

    name_to_path = {}
    for path in results:
        name = os.path.basename(path)
        name_to_path[name] = path
        result_listbox.insert("end", name)

    CTkButton(popup, text="Open Selected", command=open_selected).pack(pady=10)

def open_selected():
    """Open the selected file or folder."""
    try:
        selected_index = result_listbox.curselection()  # Get selected item
        if not selected_index:
            show_message("Error", "No file selected!", "cancel")
            return
        
        selected_text = result_listbox.get(selected_index)  # Get selected filename
        full_path = name_to_path.get(selected_text)
        if not full_path:
            show_message("Error", "Invalid file selected!", "cancel")
            return

        if os.path.isdir(full_path):  # Open Folder
            if os.name == "nt":  
                subprocess.run(["explorer", full_path], check=True)
            else:  
                subprocess.run(["xdg-open", full_path], check=True)
        else:  # Open File
            if os.name == "nt":
                os.startfile(full_path)
            else:
                subprocess.run(["xdg-open", full_path], check=True)

        show_message("Success", f"Opened: {full_path}", "check")
    except Exception as e:
        show_message("Error", f"Failed to open file/folder: {e}", "cancel")

# Add Sidebar Sections and Buttons
create_section_label(sidebar, "File Management App")
divider()

create_section_label(sidebar, "📁 File Operations")
create_sidebar_button(sidebar, "📤 Upload Files", upload_file)
create_sidebar_button(sidebar, "🔄 Move Files", move_file)
create_sidebar_button(sidebar, "🗑️ Delete Files (Move to Trash)", delete_file)
create_sidebar_button(sidebar, "♻️ Restore Files", restore_file)
create_sidebar_button(sidebar, "🚮 Empty Trash", clear_trash)
create_sidebar_button(sidebar, "✒️ Rename File", rename_file)
divider()

create_section_label(sidebar, "🔄️Sorting & Filtering")
create_sidebar_button(sidebar, "🔤 Sort by Name",sort_by_name)
create_sidebar_button(sidebar, "📅 Sort by Date",sort_files_by_creation_date)
create_sidebar_button(sidebar, "📁 Sort by Type",sort_files_by_type)
create_sidebar_button(sidebar, "🔍 Search Files/Folders",search_files_folders)
divider()

create_section_label(sidebar, "📂Folder Operations")
create_sidebar_button(sidebar, "📁 Create Folder",create_folder)
create_sidebar_button(sidebar, "📂 Rename Folder",rename_folder)

# Run app
app.mainloop()
