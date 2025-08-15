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
            
        frame = self.frames[frame_class]
        
        # Reset input screen if we're navigating to it
        if frame_class == InputScreen:
            frame.reset_form()
            
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
        # Reset the input screen before showing it
        input_screen = self.controller.frames[InputScreen]
        input_screen.reset_form()
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
                "emissions": 0.0,
                "ccs": {
                    "capture": 0,
                    "compression": 0,
                    "transportation": 0,
                    "storage": 0
                }
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
        self.plant_efficiency.trace_add('write', lambda *args: self.safe_calculate_generation())
        self.total_output = tk.DoubleVar()
        self.total_output.trace_add('write', lambda *args: self.calculate_generation())
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

        # Power Plant Information Frame
        power_plant_frame = ttk.LabelFrame(self, text="Power Plant Information")
        power_plant_frame.pack(fill="x", padx=20, pady=10)
        
        # Create a single row frame for all three fields
        info_row = ttk.Frame(power_plant_frame)
        info_row.pack(fill="x", expand=True)
        
        # Field 1: Efficiency with placeholder
        efficiency_frame = ttk.Frame(info_row)
        efficiency_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(efficiency_frame, text="Current 'traditional' efficiency").pack(side="left")
        self.efficiency_entry = self.create_entry_with_placeholder(
            efficiency_frame,
            var=self.plant_efficiency,
            placeholder="e.g. 45.5",
            width=10
        )
        self.efficiency_entry.pack(side="left", padx=5)
        
        # Field 2: Total Output with placeholder
        output_frame = ttk.Frame(info_row)
        output_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(output_frame, text="Total output (MW)").pack(side="left")
        self.output_entry = self.create_entry_with_placeholder(
            output_frame,
            var=self.total_output,
            placeholder="e.g. 500",
            width=10
        )
        self.output_entry.pack(side="left", padx=5)
        
        # Field 3: Location (normal entry)
        location_frame = ttk.Frame(info_row)
        location_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(location_frame, text="Location").pack(side="left")
        ttk.Entry(location_frame, textvariable=self.plant_location, width=15).pack(side="left", padx=5)

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

        # Optional Emissions (CO2) with placeholder
        emissions_frame = ttk.LabelFrame(self, text="Optional Emissions (CO2)")
        emissions_frame.pack(fill="x", padx=20, pady=10)
        ttk.Checkbutton(emissions_frame, text="Include Emissions Estimation",
                        variable=self.include_emissions,
                        bootstyle='round-toggle').pack(anchor="w")
        ttk.Label(emissions_frame, text="Emissions (g CO2/kg fuel)").pack(anchor="w")
        self.emissions_entry = self.create_entry_with_placeholder(
            emissions_frame,
            var=self.emissions_value,
            placeholder="e.g. 2.42",
            width=15
        )
        self.emissions_entry.pack(fill="x", padx=5, pady=5)

        # Sensitivity Analysis with placeholder
        sensitivity_frame = tk.LabelFrame(self, text="Sensitivity Analysis", font=(self.controller.system_font, 14, "bold"))
        sensitivity_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(sensitivity_frame, text="Interval").pack(anchor="w")
        self.sensitivity_entry = self.create_entry_with_placeholder(
            sensitivity_frame,
            var=self.sensitivity_value,
            placeholder="e.g. 5",
            width=15
        )
        self.sensitivity_entry.pack(fill="x", padx=5, pady=5)

        # Run Button
        run_button = ttk.Button(self, text="RUN", command=self.collect_data)
        run_button.pack(pady=20)

        # Error label
        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack()

        # Bind fuel selection to update predefined values
        fuel_dropdown.bind('<<ComboboxSelected>>', self.update_predefined_values)
        
        # Initial setup of fields
        self.toggle_input_fields()

    def calculate_generation(self):
        """Calculate generation value based on efficiency and total output"""
        try:
            # First check if we have a fuel type selected (for efficiency)
            if not self.fuel_type.get() or self.fuel_type.get() not in self.predefined_values:
                return
                
            fuel_data = self.predefined_values[self.fuel_type.get()]
            
            # Safely get values with error handling
            try:
                efficiency = float(self.plant_efficiency.get()) if self.plant_efficiency.get() else 0
                total_output = float(self.total_output.get()) if self.total_output.get() else 0
            except (ValueError, tk.TclError):
                efficiency = 0
                total_output = 0
                
            # Calculate generation as efficiency * total_output
            if total_output > 0 and efficiency > 0:
                generation_value = (efficiency / 100) * total_output  # Convert % to decimal
                self.generation.set(round(generation_value, 2))
            else:
                self.generation.set(0.0)
                
        except Exception as e:
            print(f"Error calculating generation: {e}")
            self.generation.set(0.0)
    
    def safe_calculate_generation(self):
        """Wrapper for calculate_generation with error handling"""
        try:
            self.calculate_generation()
        except Exception as e:
            print(f"Error in generation calculation: {e}")
            self.generation.set(0.0)

    def create_entry_with_placeholder(self, parent, var, placeholder, **kwargs):
        """Create an entry with working placeholder text"""
        entry = ttk.Entry(parent, textvariable=var, **kwargs)
        entry.placeholder = placeholder
        entry.default_fg = entry.cget('foreground')
        entry.var = var  # Store the variable reference
        
        # Initialize based on variable state
        try:
            if not var.get() or str(var.get()) == "0.0":
                entry.insert(0, placeholder)
                entry.config(foreground='gray')
        except:
            entry.insert(0, placeholder)
            entry.config(foreground='gray')
        
        # Bind focus events
        entry.bind('<FocusIn>', self.clear_placeholder)
        entry.bind('<FocusOut>', self.set_placeholder_if_empty)
        
        return entry
    
    def handle_var_change(self, entry):
        """Handle when the associated variable changes"""
        current_val = entry.var.get()
        if current_val and str(current_val) != '0.0':
            entry.delete(0, 'end')
            entry.insert(0, current_val)
            entry.config(foreground=entry.default_fg)
        elif not entry.get() or entry.get() == entry.placeholder:
            self.set_placeholder(entry)
    
    def clear_placeholder(self, event):
        """Clear placeholder when entry gets focus"""
        entry = event.widget
        if entry.get() == entry.placeholder:
            entry.delete(0, 'end')
            entry.config(foreground=entry.default_fg)
            try:
                entry.var.set('')
            except:
                pass
    
    def set_placeholder(self, entry):
        """Set placeholder text if entry is empty"""
        try:
            current_value = entry.var.get()
            if current_value == "" or str(current_value) == "0.0":
                entry.delete(0, 'end')
                entry.insert(0, entry.placeholder)
                entry.config(foreground='gray')
        except:
            # If there's any error getting the value, set the placeholder
            entry.delete(0, 'end')
            entry.insert(0, entry.placeholder)
            entry.config(foreground='gray')
    
    def set_placeholder_if_empty(self, event):
        """Reset placeholder if entry is left empty"""
        entry = event.widget
        if not entry.get():
            self.set_placeholder(entry)

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
                self.calculate_generation()
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

    def collect_data(self):
        try:
            # Validate all required fields
            required_fields = {
                'plant_efficiency': (self.plant_efficiency, "Efficiency"),
                'total_output': (self.total_output, "Total Output"),
                'extraction': (self.extraction, "Extraction"),
                'processing': (self.processing, "Processing"),
                'transportation': (self.transportation, "Transportation"),
                'generation': (self.generation, "Generation")
            }
            
            input_data = {}
            errors = []
            
            # Validate and collect all required fields
            for field, (var, name) in required_fields.items():
                try:
                    value = float(var.get())
                    if value <= 0 and field not in ['plant_efficiency']:  # Efficiency can be 0
                        errors.append(f"{name} must be greater than 0")
                    input_data[field] = value
                except (ValueError, tk.TclError):
                    errors.append(f"Invalid {name} value")
            
            # Check for any validation errors
            if errors:
                self.error_label.config(text="\n".join(errors))
                return
                
            # Add optional fields
            input_data.update({
                'plant_location': self.plant_location.get(),
                'ccs': self.ccs.get(),
                'ccs_capture': float(self.ccs_capture.get()) if self.ccs.get() else 0,
                'ccs_compression': float(self.ccs_compression.get()) if self.ccs.get() else 0,
                'ccs_transportation': float(self.ccs_transportation.get()) if self.ccs.get() else 0,
                'ccs_storage': float(self.ccs_storage.get()) if self.ccs.get() else 0,
                'include_emissions': self.include_emissions.get(),
                'emissions_value': float(self.emissions_value.get()) if self.include_emissions.get() else 0,
                'sensitivity_value': float(self.sensitivity_value.get()) if self.sensitivity_value.get() else 0,
                'fuel_type': self.fuel_type.get()
            })
            
            # Pass to results screen
            self.controller.frames[ResultScreen].display_results(input_data)
            self.controller.show_frame(ResultScreen)
            
        except Exception as e:
            self.error_label.config(text=f"Error: {str(e)}")

    def reset_form(self):
        """Reset all input fields to their default values"""
        # Clear variables - initialize them properly
        self.plant_efficiency.set(0.0)
        self.total_output.set(0.0)
        self.plant_location.set('')
        self.fuel_type.set('')
        self.extraction.set(0.0)
        self.processing.set(0.0)
        self.transportation.set(0.0)
        self.generation.set(0.0)
        self.ccs.set(False)
        self.include_emissions.set(False)
        self.emissions_value.set(0.0)
        self.sensitivity_value.set(0.0)
        self.ccs_capture.set(0.0)
        self.ccs_compression.set(0.0)
        self.ccs_transportation.set(0.0)
        self.ccs_storage.set(0.0)
        
        # Reset predefined values toggle
        self.use_predefined.set(True)
        self.use_predefined_ccs.set(True)
        
        # Reset placeholders
        for entry in [self.efficiency_entry, self.output_entry, 
                    self.emissions_entry, self.sensitivity_entry]:
            self.set_placeholder(entry)
        
        # Clear error messages
        self.error_label.config(text="")
        
        # Hide CCS fields if they were visible
        self.toggle_ccs_fields()
        self.toggle_input_fields()

    def on_show(self):
        pass

    def on_hide(self):
        pass

class ResultScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        
        # Main container with scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Title - Centered
        ttk.Label(self.scrollable_frame, 
                 text="Results Summary", 
                 font=(self.controller.system_font, 16, "bold")
                ).pack(pady=20, anchor="center")

        # Results Overview Frame - Centered
        self.overview_frame = ttk.LabelFrame(self.scrollable_frame, text="Key Metrics")
        self.overview_frame.pack(fill="x", padx=20, pady=10, ipadx=10, ipady=10)
        
        # Key metrics labels - Centered
        self.total_efficiency_label = ttk.Label(self.overview_frame, 
                                              text="Total efficiency: ", 
                                              font=(self.controller.system_font, 12))
        self.total_efficiency_label.pack(anchor="nw", padx=10, pady=5)
        
        self.efficiency_drop_label = ttk.Label(self.overview_frame, 
                                             text="Efficiency drop: ", 
                                             font=(self.controller.system_font, 12))
        self.efficiency_drop_label.pack(anchor="nw", padx=10, pady=5)
        
        self.total_emissions_label = ttk.Label(self.overview_frame, 
                                             text="Total emissions: ", 
                                             font=(self.controller.system_font, 12))
        self.total_emissions_label.pack(anchor="nw", padx=10, pady=5)

        # Container for side-by-side graphs
        self.graphs_container = ttk.Frame(self.scrollable_frame)
        self.graphs_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Energy Contribution Frame (Left graph)
        self.energy_frame = ttk.LabelFrame(self.graphs_container, 
                                         text="Energy Contribution by Stage")
        self.energy_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Placeholder for bar chart
        self.bar_chart_canvas = tk.Canvas(self.energy_frame, height=300, bg="white")
        self.bar_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # CCS Sensitivity Analysis Frame (Right graph)
        self.sensitivity_frame = ttk.LabelFrame(self.graphs_container, 
                                              text="CCS Efficiency Sensitivity Analysis")
        self.sensitivity_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Placeholder for line chart
        self.line_chart_canvas = tk.Canvas(self.sensitivity_frame, height=300, bg="white")
        self.line_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Back button - Centered
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill="x", pady=20)
        back_button = ttk.Button(button_frame, 
                               text="Back to Home", 
                               command=lambda: controller.show_frame(HomeScreen))
        back_button.pack(anchor="center")

        # Sample data initialization
        self.stages = ["Extraction", "Processing", "Transportation", "CCS"]
        self.energy_values = [0, 0, 0, 0]
        self.ccs_percentages = [80, 85, 90, 95, 100]
        self.efficiency_values = [0, 0, 0, 0, 0]

    def calculate_results(self, input_data):
        """Perform all calculations based on input data with comprehensive error handling"""
        try:
            results = {}
            
            # Initialize default values for all calculations
            defaults = {
                'extraction': 0,
                'processing': 0,
                'transportation': 0,
                'generation': 0,
                'plant_efficiency': 0,
                'ccs_capture': 0,
                'ccs_compression': 0,
                'ccs_transportation': 0,
                'ccs_storage': 0,
                'emissions_value': 0,
                'ccs': False,
                'include_emissions': False
            }
            
            # Safely get all input values with defaults
            try:
                extraction = float(input_data.get('extraction', defaults['extraction']))
                processing = float(input_data.get('processing', defaults['processing']))
                transportation = float(input_data.get('transportation', defaults['transportation']))
                generation = float(input_data.get('generation', defaults['generation']))
                plant_efficiency = float(input_data.get('plant_efficiency', defaults['plant_efficiency']))
                ccs_enabled = bool(input_data.get('ccs', defaults['ccs']))
                include_emissions = bool(input_data.get('include_emissions', defaults['include_emissions']))
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid input values: {str(e)}")

            # 1. Calculate total energy contributions
            try:
                ccs_energy = 0
                if ccs_enabled:
                    ccs_energy = (
                        float(input_data.get('ccs_capture', defaults['ccs_capture'])) +
                        float(input_data.get('ccs_compression', defaults['ccs_compression'])) +
                        float(input_data.get('ccs_transportation', defaults['ccs_transportation'])) +
                        float(input_data.get('ccs_storage', defaults['ccs_storage']))
                    )
                
                total_energy = extraction + processing + transportation + generation + ccs_energy
            except Exception as e:
                raise ValueError(f"Error calculating total energy: {str(e)}")

            # 2. Calculate total efficiency
            try:
                if total_energy > 0:
                    results['total_efficiency'] = (total_output / total_energy) * 100
                else:
                    results['total_efficiency'] = 0.0
            except Exception as e:
                raise ValueError(f"Error calculating total efficiency: {str(e)}")

            # 3. Calculate efficiency drop
            try:
                results['efficiency_drop'] = max(0.0, plant_efficiency - results['total_efficiency'])
            except Exception as e:
                raise ValueError(f"Error calculating efficiency drop: {str(e)}")

            # 4. Calculate emissions (if enabled)
            try:
                if include_emissions:
                    emissions_value = float(input_data.get('emissions_value', defaults['emissions_value']))
                    results['total_emissions'] = emissions_value * (1 - results['total_efficiency']/100)
                else:
                    results['total_emissions'] = 0.0
            except Exception as e:
                raise ValueError(f"Error calculating emissions: {str(e)}")

            # 5. Energy contributions by stage
            try:
                results['energy_contributions'] = {
                    'extraction': extraction,
                    'processing': processing,
                    'transportation': transportation,
                    'generation': generation,
                    'ccs': ccs_energy if ccs_enabled else 0.0
                }
            except Exception as e:
                raise ValueError(f"Error preparing energy contributions: {str(e)}")

            # 6. CCS sensitivity analysis
            try:
                results['ccs_sensitivity'] = []
                if ccs_enabled:
                    for percentage in [80, 85, 90, 95, 100]:
                        adjusted_ccs = ccs_energy * (percentage/100)
                        adjusted_total = extraction + processing + transportation + generation + adjusted_ccs
                        eff = (total_output / adjusted_total) * 100 if adjusted_total > 0 else 0
                        results['ccs_sensitivity'].append(eff)
                else:
                    results['ccs_sensitivity'] = [results['total_efficiency']] * 5
            except Exception as e:
                raise ValueError(f"Error in CCS sensitivity analysis: {str(e)}")

            return results

        except Exception as e:
            # Return a results dictionary with error information
            return {
                'error': str(e),
                'total_efficiency': 0.0,
                'efficiency_drop': 0.0,
                'total_emissions': 0.0,
                'energy_contributions': {
                    'extraction': 0.0,
                    'processing': 0.0,
                    'transportation': 0.0,
                    'generation': 0.0,
                    'ccs': 0.0
                },
                'ccs_sensitivity': [0.0] * 5
            }

    def display_results(self, input_data):
        """Calculate and display all results with error handling"""
        # Perform all calculations
        results = self.calculate_results(input_data)
        
        # Check for calculation errors
        if 'error' in results:
            self.total_efficiency_label.config(
                text=f"Calculation Error: {results['error']}",
                foreground='red'
            )
            self.efficiency_drop_label.config(text="")
            self.total_emissions_label.config(text="")
            return
        
        # Update text displays
        self.total_efficiency_label.config(
            text=f"Total efficiency: {results['total_efficiency']:.2f}%",
            foreground='black'
        )
        self.efficiency_drop_label.config(
            text=f"Efficiency drop: {results['efficiency_drop']:.2f}%"
        )
        self.total_emissions_label.config(
            text=f"Total emissions: {results['total_emissions']:.2f} kg CO2/MWh" 
            if results['total_emissions'] > 0 else "Emissions calculation not enabled"
        )
        
        # Prepare data for visualizations
        self.energy_values = [
            results['energy_contributions']['extraction'],
            results['energy_contributions']['processing'],
            results['energy_contributions']['transportation'],
            results['energy_contributions']['ccs']
        ]
        
        self.efficiency_values = results['ccs_sensitivity']
        
        # Redraw charts
        self.draw_bar_chart()
        self.draw_line_chart()

    def draw_bar_chart(self):
        """Draw a simple bar chart of energy contributions"""
        self.bar_chart_canvas.delete("all")
        width = self.bar_chart_canvas.winfo_width()
        height = self.bar_chart_canvas.winfo_height()
        
        if width < 10 or height < 10:  # Canvas not ready
            return
            
        max_value = max(self.energy_values) if self.energy_values else 1
        bar_width = (width - 100) / len(self.stages)
        padding = 50
        
        # Draw axes
        self.bar_chart_canvas.create_line(padding, height - padding, width - padding, height - padding)  # X-axis
        self.bar_chart_canvas.create_line(padding, padding, padding, height - padding)  # Y-axis

        # Add Y-axis label (rotated vertically)
        self.bar_chart_canvas.create_text(20, height//2, 
                                    text="Total energy (MJ/kg)",
                                    font=("Arial", 10),
                                    angle=90,
                                    anchor="center")
        
        # Draw bars and labels
        for i, (stage, value) in enumerate(zip(self.stages, self.energy_values)):
            x0 = padding + i * bar_width + 10
            x1 = x0 + bar_width - 20
            y0 = height - padding
            bar_height = (value / max_value) * (height - 2 * padding) if max_value > 0 else 0
            y1 = y0 - bar_height
            
            # Draw bar
            self.bar_chart_canvas.create_rectangle(x0, y1, x1, y0, fill="skyblue")
            
            # Draw value label
            self.bar_chart_canvas.create_text((x0 + x1)/2, y1 - 15, 
                                             text=f"{value:.2f}", 
                                             anchor="center")
            
            # Draw stage label
            self.bar_chart_canvas.create_text((x0 + x1)/2, y0 + 15, 
                                             text=stage, 
                                             anchor="center", 
                                             angle=0)

    def draw_line_chart(self):
        """Draw a simple line chart of CCS sensitivity"""
        self.line_chart_canvas.delete("all")
        width = self.line_chart_canvas.winfo_width()
        height = self.line_chart_canvas.winfo_height()
        
        if width < 10 or height < 10:  # Canvas not ready
            return
            
        max_eff = max(self.efficiency_values) if self.efficiency_values else 1
        min_eff = min(self.efficiency_values) if self.efficiency_values else 0
        range_eff = max_eff - min_eff if max_eff != min_eff else 1
        
        padding = 50
        
        # Draw axes
        self.line_chart_canvas.create_line(padding, height - padding, width - padding, height - padding)  # X-axis
        self.line_chart_canvas.create_line(padding, padding, padding, height - padding)  # Y-axis
        
        # Draw labels
        self.line_chart_canvas.create_text(width//2, height - 10, 
                                         text="CCS Percentage (%)", 
                                         anchor="center")
        self.line_chart_canvas.create_text(30, height//2, 
                                         text="Efficiency (%)", 
                                         anchor="center", 
                                         angle=90)
        
        # Draw data points and lines
        prev_x, prev_y = None, None
        for i, (percentage, efficiency) in enumerate(zip(self.ccs_percentages, self.efficiency_values)):
            x = padding + i * (width - 2 * padding) / (len(self.ccs_percentages) - 1)
            y = height - padding - ((efficiency - min_eff) / range_eff) * (height - 2 * padding)
            
            # Draw point
            self.line_chart_canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")
            
            # Draw percentage label
            self.line_chart_canvas.create_text(x, height - padding + 15, 
                                             text=f"{percentage}%", 
                                             anchor="center")
            
            # Draw efficiency label
            self.line_chart_canvas.create_text(x + 20, y, 
                                             text=f"{efficiency:.1f}%", 
                                             anchor="w")
            
            # Connect points with lines
            if prev_x is not None:
                self.line_chart_canvas.create_line(prev_x, prev_y, x, y, fill="blue", width=2)
            
            prev_x, prev_y = x, y

    def on_show(self):
        """Redraw charts when frame is shown"""
        self.draw_bar_chart()
        self.draw_line_chart()

    def on_hide(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
