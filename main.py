import sys
import tkinter as tk

from plot import Plot


def click_callback():
    plot_screen = Plot(root)
    plot_screen.start()


# Init the root Tk application
root = tk.Tk()
root.title("Application")
# It makes the window not resizable under those dimensions
root.minsize(width=300, height=200)

start_button = tk.Button(root, text="START", command=click_callback)
start_button.pack(expand=1)

sys.exit(root.mainloop())
