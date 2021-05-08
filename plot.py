import tkinter as tk
from tkinter.messagebox import askokcancel

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import threading
import queue

import fake_sensor


class Plot:
    def __init__(self, master=None):
        # Frequency for the fake data generation
        self._selected_frequency = 10  # Hz

        # Window that will host the plot
        self._top_level = tk.Toplevel(master=master)
        self._top_level.title("Real Time Plot")
        self._top_level.resizable(False, False)
        self._top_level.geometry("{0}x{1}+0+0".format(
            self._top_level.winfo_screenwidth() - 3, self._top_level.winfo_screenheight() - 3))
        self._top_level.protocol("WM_DELETE_WINDOW", self._handle_close)

        # Let's configure the matplotlib Figure & Axis & Line
        self._figure = Figure(figsize=(20, 9), dpi=100)
        self._axis = self._figure.add_subplot(1, 1, 1)
        self._axis.set_title("Data")
        self._line = self._axis.plot([], [])[0]

        # This is the widget that wrap the matplotlib plot
        self._canvas = FigureCanvasTkAgg(self._figure, self._top_level)
        self._canvas.get_tk_widget().pack(expand=1, fill=tk.BOTH)

        # y coordinate of the current points
        self._ys = []
        # x coordinate of the current points
        self._xs = []
        # n° of points to visualize
        self._n_of_points = 30

        # Some threading stuff
        self._queue = queue.Queue()
        self._run_signal = threading.Event()
        self._run_signal.set()
        self._thread = threading.Thread(
            daemon=False,
            target=fake_sensor.fake_sensor,
            args=(self._selected_frequency, self._queue, self._run_signal)
        )

        # References to handle better the tkinter 'after' function
        self._after_job_data = None
        self._after_job_thread = None

        # Keep track of the status of the window
        self._is_closed = False

    def _handle_close(self):
        if askokcancel("QUIT", "Do you really wish to quit?"):
            self._close()

    def _close(self):
        # Clear the signal
        self._run_signal.clear()
        if self._thread.is_alive():
            # Thread has not finished yet
            self._after_job_thread = self._top_level.after(50, self._close)
        else:
            # Thread has finished
            self._top_level.destroy()
            self._is_closed = True
            self._top_level.after_cancel(self._after_job_thread)
            # Help the garbage collector
            self._after_job_thread = None

    def update_data(self):
        if not self._is_closed:
            try:
                data = self._queue.get(block=False)
                # Add new reads in our data
                self._xs.append(data[0])
                self._ys.append(data[1])

                # Get the last 'n_of_points'
                if len(self._xs) > self._n_of_points:
                    self._xs = self._xs[-self._n_of_points:]
                    self._ys = self._ys[-self._n_of_points:]

                # Computing maximum and minimum of our ys data
                min_y = min(self._ys)
                max_y = max(self._ys)

                # Adjust the two axes
                self._axis.set_ylim(min_y - 2, max_y + 2)
                self._axis.set_xlim(self._xs[0], self._xs[-1])

                # Update the data
                self._line.set_data(self._xs, self._ys)

                # Update the canvas
                self._canvas.draw()
            except queue.Empty:
                pass

            self._after_job_data = self._top_level.after(10, self.update_data)
        else:
            # Cancel the after job
            self._top_level.after_cancel(self._after_job_data)
            self._after_job_data = None

    def start(self):
        # Start the thread
        self._thread.start()

        # Postpone 'update_data' execution
        self._after_job_data = self._top_level.after(10, self.update_data)
