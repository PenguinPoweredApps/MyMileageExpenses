# gui.py
# Author: Simon Wollerton, simon@penguinpowered.co.uk
""" This is the frontend script written in Python Tkinter to ease the operation of the main.py script."""

import main as main

from tkinter import *
from tkinter.ttk import *
from main import *


def run_ui():
    app_path = Path(__file__).parent
    assets_folder = app_path / Path("./assets")

    root = Tk()

    app_status_variable = StringVar()
    app_status_variable.set(main.app_status_update)

    def assetsfolder(path: str) -> Path:
        return assets_folder / Path(path)

    def update_app_run_status():
        app_status_variable.set(main.app_status_update)
        root.after(500, update_app_run_status)

    canvas = Canvas(
        root,
        bg="#fff",
        height=600,
        width=380,
        bd=1,
        highlightthickness=0,
    )
    canvas.place(x=0, y=0)

    # Title label
    title_label = Label(
        text="My Mileage Expenses",
        padding=10,
        background="#fff",
        foreground="#1e0252",
        font=("Arial", 20, "bold"),
    )
    title_label.pack()

    # Vendor label
    vendor_label = Label(
        text="by Penguin Powered Apps",
        padding=0,
        background="#fff",
        foreground="#1e0252",
        font=("Arial", 8),
    )
    vendor_label.pack()

    # Vendor label
    website_label = Label(
        text="https://www.penguinpowered.co.uk",
        padding=0,
        background="#fff",
        foreground="#1e0252",
        font=("Arial", 8),
    )
    website_label.pack()

    # Application status label
    app_status_label = Label(
        textvariable=app_status_variable,
        padding=40,
        background="#fff",
        foreground="#eb054d",
        font=("Arial", 10),
    )
    app_status_label.pack()

    # App Image
    travel = PhotoImage(file=assetsfolder("travel.png"))
    canvas.create_image(185, 285, image=travel)

    # Start button
    start_button = Button(
        text="START",
        command=lambda: [run_main_thread(), update_app_run_status()],
        cursor="hand2",
    )
    start_button.place(x=115, y=365, width=150, height=40)

    # Reminder label
    reminder_label = Label(
        text="Please remember to adjust any settings and data.",
        padding=22,
        background="#fff",
        foreground="#eb054d",
        font=("Arial", 10),
    )
    reminder_label.place(x=25, y=470)

    # Settings button
    settings_button = Button(
        text="SETTINGS", command=lambda: edit_settings(), cursor="hand2"
    )
    settings_button.place(x=21, y=550, width=90, height=30)

    # Data button
    databutton = Button(text="DATA", command=lambda: edit_data(), cursor="hand2")
    databutton.place(x=144, y=550, width=90, height=30)

    # Quit button
    quit_button = Button(text="QUIT", command=lambda: root.destroy(), cursor="hand2")
    quit_button.place(x=270, y=550, width=90, height=30)

    root.geometry("380x600+50+50")
    root.title("My Mileage Expenses")
    root.iconphoto(False, PhotoImage(file=assetsfolder("icon.png")))
    root.resizable(False, False)
    root.mainloop()


run_ui()
