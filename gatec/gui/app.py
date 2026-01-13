import tkinter as tk
import ttkbootstrap as ttk
from gatec.gui.frames import HomeScreen, InputScreen, ResultScreen, HistoryScreen

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename='flatly')
        self.title("Total Efficiency Computation")
        self.system_font = "Roboto"
        
        # Maximize window
        self.state('zoomed')

        # Contenedor principal para las pantallas
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize current frame tracking
        self.current_frame = None

        # Initialize frames
        self.frames = {}
        for FrameClass in (HomeScreen, InputScreen, ResultScreen, HistoryScreen):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass] = frame  # Store with class as key, not class name
            frame.grid(row=0, column=0, sticky="nsew")

        # Show home screen
        self.show_frame(HomeScreen)

    def show_frame(self, frame_class):
        """Display a specific frame"""
        # Call lifecycle methods
        if self.current_frame:
            self.current_frame.on_hide()
            
        frame = self.frames[frame_class]
        
        # Reset input screen if we're navigating to it
        if frame_class == InputScreen:
            frame.reset_form()
            
        frame.tkraise()
        frame.on_show()
        self.current_frame = frame
        
        return frame
