import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style, Window, Button, Checkbutton, Entry, Frame, Label, LabelFrame, Combobox
from tkinter.messagebox import showerror
from tkinter import StringVar, BooleanVar, DoubleVar

class FrameManager(ttk.Frame):
    """Base class for all frames with common functionality"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")
        
    def on_show(self):
        """Called when frame is shown - override in subclasses"""
        pass
    
    def on_hide(self):
        """Called when frame is hidden - override in subclasses"""
        pass

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename='flatly')
        self.title("Total Efficiency Computation")
        # self.geometry(f"{int(self.winfo_screenwidth()*.7)}x{int(self.winfo_screenheight()*.8)}+0+0")
        # self.resizable(False, False)
        self.system_font = "Roboto"

        # Contenedor principal para las pantallas
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize current frame tracking
        self.current_frame = None

        # Initialize frames
        self.frames = {}
        for FrameClass in (HomeScreen, InputScreen, ResultScreen):
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
            
        frame = self.frames[frame_class]  # Use class directly as key
        frame.tkraise()
        frame.on_show()
        self.current_frame = frame
        
        return frame

class Card(ttk.Frame):
    def __init__(self, parent, controller, title, fuel, efficiency_drop, insight, width=None, height=None):
        super().__init__(parent, relief="solid", padding=(10,10))
        self.controller = controller

        # Create a frame for the two columns
        self.column_frame = ttk.Frame(self)
        self.column_frame.pack(fill="both", expand=True)

        # Column 1 - Set fixed width and allow text wrapping
        self.column1 = ttk.Frame(self.column_frame, width=self.winfo_screenwidth()*.245)
        self.column1.grid(row=0, column=0, sticky="nsew")
        self.column1.grid_propagate(False)  # Prevent frame from resizing based on content

        # Column 2 - Set fixed width and allow text wrapping
        self.column2 = ttk.Frame(self.column_frame, width=self.winfo_screenwidth()*.105)
        self.column2.grid(row=0, column=1, sticky="nsew")
        self.column2.grid_propagate(False)  # Prevent frame from resizing based on content

        # Add text to Column 1
        self.title_label = ttk.Label(self.column1, text=title,
                                    font=(self.controller.system_font, 14, "bold"),
                                    anchor="w", justify="left").pack(anchor="w")
        self.eff_drop_label = ttk.Label(self.column1, text=f"Total efficiency dropped: {efficiency_drop}",
                                    font=(self.controller.system_font, 10),
                                    anchor="w", justify="left").pack(anchor="w")
        self.insight_label = ttk.Label(self.column1, text=insight,
                                    font=(self.controller.system_font, 10), anchor="w", justify="left").pack(anchor="w")

        # Add fuel label to Column 2
        fuel_colors = {
            "Coal": "inverse-dark",
            "Natural gas": "inverse-success",
            "Hydrogen": "inverse-info",
            # Add more fuel types as needed
        }
        fuel_color = fuel_colors.get(fuel, "inverse-secondary")  # Default to gray if fuel type not found
        self.fuel_label = ttk.Label(self.column2, text=fuel,
                                    borderwidth=1, relief="solid",
                                    bootstyle=fuel_color,
                                    padding=(5,5),
                                    anchor='center'
                                    )
        self.fuel_label.pack(anchor="e", padx=5, pady=5, fill="both", expand=True)

        self.view_button = ttk.Button(self.column2, text="View", padding=1, cursor="hand2",
                                    width=1
                                    )
        self.view_button.pack(anchor="e", padx=5, pady=5, fill="both", expand=True)

        # Configure grid weights
        self.column_frame.grid_columnconfigure(0, weight=1)
        self.column_frame.grid_columnconfigure(1, weight=1)

class HomeScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Title
        self.title_label = ttk.Label(self, text="GATEC", font=(self.controller.system_font, 40, "bold", "italic")).pack(padx=20, pady=20)
        
        # Create a frame for the cards
        self.card_frame = ttk.Frame(self)
        self.card_frame.pack(fill="both", expand=True)

        # Create some predefined data for the cards
        card_data = [
            ("Ferry's Plant - United Kingdom", "Coal", "10%", "Good performance"),
            ("Aix-en-Provence Plant - France", "Hydrogen", "60%", "Terrible"),
            ("La Sagra Power Plant - Spain", "Natural gas", "5%", "Excellent"),
            ("Goose bay Plant - Canada", "Coal", "20%", "Needs improvement"),
            ("Additional Plant - Location", "Biomass", "30%", "Average performance"),
            ("Example Plant - Country", "Natural gas", "15%", "Good performance"),
            ("Additional Plant - Location", "Biomass", "30%", "Average performance"),
            ("Example Plant - Country", "Natural gas", "15%", "Good performance"),
            ("Additional Plant - Location", "Biomass", "30%", "Average performance"),
            ("Example Plant - Country", "Natural gas", "15%", "Good performance")
        ]

        # Limit to a maximum of 6 cards (2 columns, 3 rows)
        max_cards = 8
        card_data = card_data[:max_cards]

        # Create a card for each piece of data
        for index, (title, fuel, efficiency_drop, insight) in enumerate(card_data):
            card = Card(self.card_frame, title=title, fuel=fuel, efficiency_drop=efficiency_drop, insight=insight, controller=self.controller)
            
            # Determine the row and column
            row = index // 2  # This will place the first two cards in row 0, the next two in row 1, and so on.
            column = index % 2  # This will place the cards in columns 0 or 1.

            card.grid(row=row, column=column, padx=20, pady=15, sticky="nsew")

        # Make sure the window resizes correctly
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.card_frame.grid_columnconfigure(1, weight=1)

        # Configure the rows to expand
        # self.card_frame.grid_rowconfigure(0, weight=1)
        # self.card_frame.grid_rowconfigure(1, weight=1)
        # self.card_frame.grid_rowconfigure(2, weight=1)

        # Create the button to launch a new calculation
        self.launch = ttk.Button(self, text="New calculation", padding=(10,10), command=self.launch_calc)
        self.launch.pack(padx=20, pady=10, expand=True)

        # Make the parent window fill the entire available space
        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
    
    def launch_calc(self):
        self.controller.show_frame(InputScreen)

    def on_show(self):
        pass

    def on_hide(self):
        pass

class InputScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Predefined values dictionary
        self.predefined_values = {
            "Coal": {
                "extraction": 0.15,
                "processing": 0.08,
                "transportation": 0.12,
                "generation": 0.65,
                "emissions": 2.42,
                "ccs": {
                    "capture": 0.20,
                    "compression": 0.15,
                    "transportation": 0.10,
                    "storage": 0.05
                }
            },
            "Natural gas": {
                "extraction": 0.10,
                "processing": 0.12,
                "transportation": 0.15,
                "generation": 0.63,
                "emissions": 2.75,
                "ccs": {
                    "capture": 0.18,
                    "compression": 0.12,
                    "transportation": 0.08,
                    "storage": 0.04
                }
            },
            "Hydrogen": {
                "extraction": 0.20,
                "processing": 0.25,
                "transportation": 0.10,
                "generation": 0.45,
                "emissions": 0.0
            },
            "Diesel": {
                "extraction": 0.12,
                "processing": 0.15,
                "transportation": 0.08,
                "generation": 0.65,
                "emissions": 2.98,
                "ccs": {
                    "capture": 0.18,
                    "compression": 0.12,
                    "transportation": 0.08,
                    "storage": 0.04
                }
            }
        }

        # Variables for storing input values
        self.plant_efficiency = tk.DoubleVar()
        self.plant_location = StringVar()
        self.fuel_type = StringVar()
        self.extraction = tk.DoubleVar()
        self.processing = tk.DoubleVar()
        self.transportation = tk.DoubleVar()
        self.generation = tk.DoubleVar()
        self.ccs = BooleanVar()
        self.include_emissions = BooleanVar()
        self.emissions_value = tk.DoubleVar()
        self.sensitivity_value = tk.DoubleVar()
        
        # Variable to track if using predefined values
        self.use_predefined = BooleanVar(value=True)

        # Add CCS variables
        self.use_predefined_ccs = BooleanVar(value=True)
        self.ccs_capture = tk.DoubleVar()
        self.ccs_compression = tk.DoubleVar()
        self.ccs_transportation = tk.DoubleVar()
        self.ccs_storage = tk.DoubleVar()

        # Power Plant Information
        power_plant_frame = ttk.LabelFrame(self, text="Power Plant Information"
                            )
        power_plant_frame.pack(fill="x", padx=20, pady=10)
        # Create two column frames for power plant info
        left_column = tk.Frame(power_plant_frame)
        left_column.pack(side="left", fill="both", expand=True)
        right_column = tk.Frame(power_plant_frame)
        right_column.pack(side="left", fill="both", expand=True)

        # Left column - Efficiency
        frame1 = tk.Frame(left_column)
        frame1.pack(fill="x", padx=5, pady=10)
        ttk.Label(frame1, text="Current 'traditional' efficiency", width=25, anchor="w").pack(side="left")
        ttk.Entry(frame1, textvariable=self.plant_efficiency).pack(side="left", padx=20)

        # Right column - Location  
        frame2 = tk.Frame(right_column)
        frame2.pack(fill="x", padx=5, pady=10)
        ttk.Label(frame2, text="Location", width=25, anchor="w").pack(side="left")
        ttk.Entry(frame2, textvariable=self.plant_location).pack(side="left", padx=20)

        # Fuel Consumption (Preliminary Stages)
        fuel_prelim_frame = ttk.LabelFrame(self, text="Fuel Consumption (Preliminary Stages)")
        fuel_prelim_frame.pack(fill="x", padx=20, pady=5)
        
        # Fuel selection and predefined values toggle
        fuel_select_frame = tk.Frame(fuel_prelim_frame)
        fuel_select_frame.pack(fill="x", padx=5)
        
        tk.Label(fuel_select_frame, text="Select Fuel").pack(side="left")
        fuel_options = list(self.predefined_values.keys())
        fuel_dropdown = ttk.Combobox(fuel_select_frame,
                                    values=fuel_options,
                                    textvariable=self.fuel_type,
                                    bootstyle='primary')
        fuel_dropdown.pack(side="left", padx=5, pady=5)
        
        # Add predefined values toggle
        ttk.Checkbutton(fuel_select_frame, text="Use predefined values", 
                       variable=self.use_predefined, 
                       command=self.toggle_input_fields,
                       bootstyle='round-toggle').pack(side="right")

        # Consumption inputs with labels and entries side by side
        self.consumption_entries = []
        
        # Create entry fields with labels
        consumption_fields = [
            ("Extraction consumption", self.extraction),
            ("Processing consumption", self.processing),
            ("Transportation consumption", self.transportation),
            ("Generation consumption", self.generation)
        ]
        # Create two column frames for consumption fields
        left_column = tk.Frame(fuel_prelim_frame)
        left_column.pack(side="left", fill="both", expand=True)
        right_column = tk.Frame(fuel_prelim_frame)
        right_column.pack(side="left", fill="both", expand=True)

        # Split fields between columns
        columns = [left_column, right_column]
        for i, (label_text, variable) in enumerate(consumption_fields):
            # Alternate between columns
            parent = columns[i % 2]
            
            frame = tk.Frame(parent)
            frame.pack(fill="x", padx=5, pady=5)
            
            label = tk.Label(frame, text=label_text, width=25, anchor="w")
            label.pack(side="left")
            
            entry = ttk.Entry(frame, textvariable=variable)
            entry.pack(side="left", padx=20)
            
            self.consumption_entries.append(entry)
        
        # CCS frame
        fuel_other_frame = ttk.LabelFrame(self, text="Carbon Capture and Storage (CCS)")
        fuel_other_frame.pack(fill="x", padx=20, pady=10)
        
        # CCS toggle and predefined values option
        ccs_header_frame = tk.Frame(fuel_other_frame)
        ccs_header_frame.pack(fill="x", padx=5)
        
        ttk.Checkbutton(ccs_header_frame, text="Include CCS", 
                       variable=self.ccs, 
                       command=self.toggle_ccs_fields,
                       bootstyle='round-toggle').pack(side="left")
        
        self.ccs_predefined_check = ttk.Checkbutton(ccs_header_frame, 
                                                   text="Use predefined values",
                                                   variable=self.use_predefined_ccs,
                                                   command=self.toggle_ccs_fields,
                                                   bootstyle='round-toggle')
        self.ccs_predefined_check.pack(side="right")

        # CCS consumption fields
        self.ccs_frame = tk.Frame(fuel_other_frame)
        self.ccs_frame.pack(fill="x", padx=5)
        
        self.ccs_entries = []
        ccs_fields = [
            ("Capture consumption", self.ccs_capture),
            ("Compression consumption", self.ccs_compression),
            ("Transportation consumption", self.ccs_transportation),
            ("Storage consumption", self.ccs_storage)
        ]

        # Create two column frames
        left_column = tk.Frame(self.ccs_frame)
        left_column.pack(side="left", fill="both", expand=True)
        right_column = tk.Frame(self.ccs_frame) 
        right_column.pack(side="left", fill="both", expand=True)

        # Split fields between columns
        columns = [left_column, right_column]
        for i, (label_text, variable) in enumerate(ccs_fields):
            # Alternate between columns
            parent = columns[i % 2]
            
            frame = tk.Frame(parent)
            frame.pack(fill="x", padx=5, pady=5)
            
            label = tk.Label(frame, text=label_text, width=25, anchor="w")
            label.pack(side="left")
            
            entry = ttk.Entry(frame, textvariable=variable)
            entry.pack(side="left", padx=20)
            
            self.ccs_entries.append(entry)

        # Initial setup
        self.toggle_ccs_fields()

        # Optional Emissions (CO2)
        emissions_frame = ttk.LabelFrame(self, text="Optional Emissions (CO2)")
        emissions_frame.pack(fill="x", padx=20, pady=10)
        ttk.Checkbutton(emissions_frame, text="Include Emissions Estimation",
                        variable=self.include_emissions,
                        bootstyle='round-toggle').pack(anchor="w")
        tk.Label(emissions_frame, text="Emissions (g CO2/kg fuel)").pack(anchor="w")
        ttk.Entry(emissions_frame, textvariable=self.emissions_value).pack(fill="x", padx=5, pady=5)

        # Sensitivity Analysis Option
        sensitivity_frame = tk.LabelFrame(self, text="Sensitivity Analysis", font=(self.controller.system_font, 14, "bold"))
        sensitivity_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(sensitivity_frame, text="Interval").pack(anchor="w")
        ttk.Entry(sensitivity_frame, textvariable=self.sensitivity_value).pack(fill="x", padx=5, pady=5)

        # Run Button
        run_button = ttk.Button(self, text="RUN", command=self.calculate_efficiency)
        run_button.pack(pady=20)

        # Error label
        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack()

        # Bind fuel selection to update predefined values
        fuel_dropdown.bind('<<ComboboxSelected>>', self.update_predefined_values)
        
        # Initial setup of fields
        self.toggle_input_fields()

    def toggle_input_fields(self):
        """Enable/disable input fields based on predefined values selection"""
        state = 'disabled' if self.use_predefined.get() else 'normal'
        for entry in self.consumption_entries:
            entry.configure(state=state)
        
        if self.use_predefined.get() and self.fuel_type.get():
            self.update_predefined_values()

    def update_predefined_values(self, event=None):
        """Update the input fields with predefined values based on fuel selection"""
        if self.use_predefined.get() and self.fuel_type.get():
            fuel = self.fuel_type.get()
            if fuel in self.predefined_values:
                values = self.predefined_values[fuel]
                self.extraction.set(values["extraction"])
                self.processing.set(values["processing"])
                self.transportation.set(values["transportation"])
                self.generation.set(values["generation"])
                self.emissions_value.set(values["emissions"])
                
                # Update CCS values if CCS is enabled and using predefined values
                if self.ccs.get() and self.use_predefined_ccs.get():
                    self.update_predefined_ccs_values()

    def toggle_ccs_fields(self):
        """Enable/disable and show/hide CCS fields based on checkboxes"""
        if self.ccs.get():
            self.ccs_frame.pack(fill="x", padx=5)
            self.ccs_predefined_check.pack(side="right")
            
            # Handle entry states
            state = 'disabled' if self.use_predefined_ccs.get() else 'normal'
            for entry in self.ccs_entries:
                entry.configure(state=state)
            
            # Update values if using predefined
            if self.use_predefined_ccs.get() and self.fuel_type.get():
                self.update_predefined_ccs_values()
        else:
            self.ccs_frame.pack_forget()
            self.ccs_predefined_check.pack_forget()

    def update_predefined_ccs_values(self):
        """Update CCS fields with predefined values based on fuel selection"""
        if self.fuel_type.get() in self.predefined_values:
            ccs_values = self.predefined_values[self.fuel_type.get()]["ccs"]
            self.ccs_capture.set(ccs_values["capture"])
            self.ccs_compression.set(ccs_values["compression"])
            self.ccs_transportation.set(ccs_values["transportation"])
            self.ccs_storage.set(ccs_values["storage"])

    def calculate_efficiency(self):
        try:
            # Get values and perform calculations
            total_input = self.extraction.get() + self.processing.get() + \
                         self.transportation.get() + self.generation.get()
            efficiency = (self.generation.get() / total_input) * 100 if total_input > 0 else 0

            # Pass results to result screen
            result_screen = self.controller.frames[ResultScreen]  # Use class as key
            result_screen.display_results(efficiency, total_input, self.ccs.get())
            self.controller.show_frame(ResultScreen)

        except Exception as e:
            self.error_label.config(text=f"Calculation failed: {str(e)}")

    def on_show(self):
        pass

    def on_hide(self):
        pass

class ResultScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Título
        tk.Label(self, text="Results", font=(self.controller.system_font, 16)).pack(pady=20)

        # Resumen de resultados
        self.result_label = tk.Label(self, text="", font=(self.controller.system_font, 14))
        self.result_label.pack(pady=10)

        # Botón para volver al inicio
        back_button = ttk.Button(self, text="Volver al Inicio",
                                 command=lambda: controller.show_frame(HomeScreen))
        back_button.pack(pady=20)

    def display_results(self, efficiency, total_input, ccs):
        ccs_text = "Yes" if ccs else "No"
        self.result_label.config(
            text=f"Total efficiency: {efficiency:.2f}%\n"
                 f"Total energy consumption: {total_input:.2f} MJ/kg\n"
                 f"CCS implementation? {ccs_text}"
        )
    
    def on_show(self):
        pass

    def on_hide(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
