import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from tkinter import StringVar, BooleanVar, DoubleVar

from gatec.gui.components import Card
from gatec.core.data_manager import load_data
from gatec.core.calculator import calculate_generation, calculate_results
from gatec.core.db_manager import db

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

class HomeScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Title
        self.title_label = ttk.Label(self, text="GATEC", font=(self.controller.system_font, 40, "bold", "italic")).pack(padx=20, pady=20)
        
        # Create a frame for the cards
        self.card_frame = ttk.Frame(self)
        self.card_frame.pack(fill="both", expand=True)

        # Make sure the window resizes correctly
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.card_frame.grid_columnconfigure(1, weight=1)

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        self.view_history = ttk.Button(button_frame, text="View All History", padding=(10,10), command=lambda: self.controller.show_frame(HistoryScreen))
        self.view_history.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.launch = ttk.Button(button_frame, text="New calculation", padding=(10,10), command=self.launch_calc)
        self.launch.pack(side="right", expand=True, fill="x", padx=(10, 0))


        # Make the parent window fill the entire available space
        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.cards = []
    
    def on_show(self):
        """Reload cards when screen is shown"""
        self.load_cards()

    def load_cards(self):
        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards = []

        # Fetch history from DB
        history = db.get_history()

        # Limit to a maximum of 8 cards
        max_cards = 8
        history = history[:max_cards]
        
        # Calculate max char width based on content
        # We look at both the fuel types AND the word "View" (or a minimum safe width)
        max_chars = 0
        for item in history:
            fuel = item.get('fuel_type') or "Unknown Fuel"
            max_chars = max(max_chars, len(fuel))

        # Define a standard width (Max content length + a consistent padding)
        # Character-based width is more stable across different screen scales
        standard_btn_width = max(15, max_chars + 4) # Increased buffer slightly to be safe 

        # Create a card for each piece of data
        for index, item in enumerate(history):
            # Parse values for display
            total_eff = f"{item['total_efficiency']:.1f}%"
            eff_drop = f"{item['efficiency_drop']:.1f}%"
            
            card = Card(self.card_frame, 
                        title=item['plant_location'] or "Unknown Location", 
                        fuel=item['fuel_type'] or "Unknown Fuel", 
                        efficiency_drop=eff_drop, 
                        total_efficiency=total_eff, 
                        on_click=lambda i=item: self.load_history_result(i['inputs_json']),
                        controller=self.controller,
                        item_width=standard_btn_width)
            
            # Determine the row and column
            row = index // 2
            column = index % 2

            card.grid(row=row, column=column, padx=20, pady=15, sticky="nsew")
            self.cards.append(card)

    def load_history_result(self, inputs_json):
        try:
            import json
            input_data = json.loads(inputs_json)
            self.controller.frames[ResultScreen].display_results(input_data, save_to_db=False)
            self.controller.show_frame(ResultScreen)
        except Exception as e:
            print(f"Error loading history: {e}")

    def launch_calc(self):
        # Reset the input screen before showing it
        input_screen = self.controller.frames[InputScreen]
        input_screen.reset_form()
        self.controller.show_frame(InputScreen)

class InputScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Layout for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        # Main content frame - distinct from self
        self.main_frame = ttk.Frame(self.canvas)
        
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window_id, width=e.width)
        )
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Load predefined values
        self.data_store = load_data()
        self.predefined_values = self.data_store.get('predefined_values', {})

        # Variables for storing input values
        self.plant_efficiency = tk.DoubleVar()
        self.plant_efficiency.trace_add('write', lambda *args: self.safe_calculate_generation())
        self.total_output = tk.DoubleVar()
        self.total_output.trace_add('write', lambda *args: self.calculate_from_inputs())
        self.plant_location = StringVar()
        self.fuel_type = StringVar()
        self.extraction = tk.DoubleVar()
        self.processing = tk.DoubleVar()
        self.transportation = tk.DoubleVar()
        self.generation = tk.DoubleVar()
        self.ccs = BooleanVar()
        self.include_emissions = BooleanVar()
        self.ccs = BooleanVar()
        self.include_emissions = BooleanVar()
        self.emissions_value = tk.DoubleVar()
        self.sensitivity_value = tk.StringVar()
        self.ccs_sensitivity_value = tk.StringVar()
        
        # Variable to track if using predefined values
        self.use_predefined = BooleanVar(value=True)

        # Add CCS variables
        self.use_predefined_ccs = BooleanVar(value=True)
        self.ccs_capture = tk.DoubleVar()
        self.ccs_compression = tk.DoubleVar()
        self.ccs_transportation = tk.DoubleVar()
        self.ccs_storage = tk.DoubleVar()
        
        # Power Plant Information Frame
        power_plant_frame = ttk.LabelFrame(self.main_frame, text="Power Plant Information")
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
        fuel_prelim_frame = ttk.LabelFrame(self.main_frame, text="Fuel Consumption (Preliminary Stages)")
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

        # Consumption inputs
        self.consumption_entries = []
        
        consumption_fields = [
            ("Extraction consumption", self.extraction),
            ("Processing consumption", self.processing),
            ("Transportation consumption", self.transportation)
        ]
        
        left_column = tk.Frame(fuel_prelim_frame)
        left_column.pack(side="left", fill="both", expand=True)
        right_column = tk.Frame(fuel_prelim_frame)
        right_column.pack(side="left", fill="both", expand=True)

        columns = [left_column, right_column]
        for i, (label_text, variable) in enumerate(consumption_fields):
            parent = columns[i % 2]
            frame = tk.Frame(parent)
            frame.pack(fill="x", padx=5, pady=5)
            label = tk.Label(frame, text=label_text, width=25, anchor="w")
            label.pack(side="left")
            entry = ttk.Entry(frame, textvariable=variable)
            entry.pack(side="left", padx=20)
            self.consumption_entries.append(entry)
        
        # CCS frame
        fuel_other_frame = ttk.LabelFrame(self.main_frame, text="Carbon Capture and Storage (CCS)")
        fuel_other_frame.pack(fill="x", padx=20, pady=10)
        
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

        self.ccs_frame = tk.Frame(fuel_other_frame)
        self.ccs_frame.pack(fill="x", padx=5)
        
        self.ccs_entries = []
        ccs_fields = [
            ("Capture consumption", self.ccs_capture),
            ("Compression consumption", self.ccs_compression),
            ("Transportation consumption", self.ccs_transportation),
            ("Storage consumption", self.ccs_storage)
        ]

        left_column = tk.Frame(self.ccs_frame)
        left_column.pack(side="left", fill="both", expand=True)
        right_column = tk.Frame(self.ccs_frame) 
        right_column.pack(side="left", fill="both", expand=True)

        columns = [left_column, right_column]
        for i, (label_text, variable) in enumerate(ccs_fields):
            parent = columns[i % 2]
            frame = tk.Frame(parent)
            frame.pack(fill="x", padx=5, pady=5)
            label = tk.Label(frame, text=label_text, width=25, anchor="w")
            label.pack(side="left")
            entry = ttk.Entry(frame, textvariable=variable)
            entry.pack(side="left", padx=20)
            self.ccs_entries.append(entry)

        self.toggle_ccs_fields()

        # Optional Emissions (CO2)
        emissions_frame = ttk.LabelFrame(self.main_frame, text="Optional Emissions (CO2)")
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

        # Sensitivity Analysis
        sensitivity_frame = tk.LabelFrame(self.main_frame, text="Sensitivity Analysis (Interval %)", font=(self.controller.system_font, 14, "bold"))
        sensitivity_frame.pack(fill="x", padx=20, pady=10)
        
        # Grid layout for inputs
        sensitivity_frame.columnconfigure(0, weight=1)
        sensitivity_frame.columnconfigure(1, weight=1)

        # General Sensitivity
        gen_frame = ttk.Frame(sensitivity_frame)
        gen_frame.grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Label(gen_frame, text="General Factors Interval").pack(anchor="w")
        self.sensitivity_entry = self.create_entry_with_placeholder(
            gen_frame,
            var=self.sensitivity_value,
            placeholder="e.g. 5%",
            width=15
        )
        self.sensitivity_entry.pack(fill="x", pady=5)

        # CCS Sensitivity
        ccs_sens_frame = ttk.Frame(sensitivity_frame)
        ccs_sens_frame.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(ccs_sens_frame, text="CCS Efficiency Interval").pack(anchor="w")
        self.ccs_sensitivity_entry = self.create_entry_with_placeholder(
            ccs_sens_frame,
            var=self.ccs_sensitivity_value,
            placeholder="e.g. 5%",
            width=15
        )
        self.ccs_sensitivity_entry.pack(fill="x", pady=5)

        # Button Frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="x", padx=20, pady=20)

        # Back Button
        back_button = ttk.Button(button_frame, text="Back", padding=(10,10), command=lambda: self.controller.show_frame(HomeScreen))
        back_button.pack(side="left", expand=True, fill="x", padx=(0, 10))

        # Run Button
        run_button = ttk.Button(button_frame, text="RUN", padding=(10,10), command=self.collect_data, bootstyle='success')
        run_button.pack(side="right", expand=True, fill="x", padx=(10, 0))

        # Error label
        self.error_label = tk.Label(self.main_frame, text="", fg="red")
        self.error_label.pack()

        # Bind fuel selection to update predefined values
        fuel_dropdown.bind('<<ComboboxSelected>>', self.update_predefined_values)
        
        # Initial setup of fields
        self.toggle_input_fields()

    def calculate_from_inputs(self):
        """Wrapper for calling calculate_generation from calculator module"""
        try:
            # Check for selected fuel type first if needed in future logic, 
            # effectively just need efficiency and total_output
            
            # Get values safely
            try:
                efficiency = float(self.plant_efficiency.get()) if self.plant_efficiency.get() else 0
                total_output = float(self.total_output.get()) if self.total_output.get() else 0
            except (ValueError, tk.TclError):
                efficiency = 0
                total_output = 0
            
            gen_val = calculate_generation(efficiency, total_output)
            self.generation.set(gen_val)
            
        except Exception as e:
            print(f"Error calculating generation: {e}")
            self.generation.set(0.0)

    def safe_calculate_generation(self):
        self.calculate_from_inputs()

    def create_entry_with_placeholder(self, parent, var, placeholder, **kwargs):
        """Create an entry with working placeholder text"""
        entry = ttk.Entry(parent, textvariable=var, **kwargs)
        entry.placeholder = placeholder
        entry.default_fg = entry.cget('foreground')
        entry.var = var
        
        try:
            val = var.get()
            # Check if empty or "0.0" (for DoubleVar residue)
            if not val or str(val) == "0.0" or (isinstance(val, str) and not val.strip()):
                entry.delete(0, 'end')
                entry.insert(0, placeholder)
                entry.config(foreground='gray')
        except:
            entry.delete(0, 'end')
            entry.insert(0, placeholder)
            entry.config(foreground='gray')
        
        entry.bind('<FocusIn>', self.clear_placeholder)
        entry.bind('<FocusOut>', self.set_placeholder_if_empty)
        
        return entry
    
    def clear_placeholder(self, event):
        entry = event.widget
        if entry.get() == entry.placeholder:
            entry.delete(0, 'end')
            entry.config(foreground=entry.default_fg)
            try:
                entry.var.set('')
            except:
                pass
    
    def set_placeholder(self, entry):
        try:
            current_value = entry.var.get()
            if current_value == "" or str(current_value) == "0.0":
                entry.delete(0, 'end')
                entry.insert(0, entry.placeholder)
                entry.config(foreground='gray')
        except:
            entry.delete(0, 'end')
            entry.insert(0, entry.placeholder)
            entry.config(foreground='gray')
    
    def set_placeholder_if_empty(self, event):
        entry = event.widget
        if not entry.get():
            self.set_placeholder(entry)

    def toggle_input_fields(self):
        state = 'disabled' if self.use_predefined.get() else 'normal'
        for entry in self.consumption_entries:
            entry.configure(state=state)
        
        if self.use_predefined.get() and self.fuel_type.get():
            self.update_predefined_values()

    def update_predefined_values(self, event=None):
        if self.use_predefined.get() and self.fuel_type.get():
            fuel = self.fuel_type.get()
            if fuel in self.predefined_values:
                values = self.predefined_values[fuel]
                self.extraction.set(values["extraction"])
                self.processing.set(values["processing"])
                self.transportation.set(values["transportation"])
                self.calculate_from_inputs()
                self.emissions_value.set(values["emissions"])
                
                if self.ccs.get() and self.use_predefined_ccs.get():
                    self.update_predefined_ccs_values()

    def toggle_ccs_fields(self):
        if self.ccs.get():
            self.ccs_frame.pack(fill="x", padx=5)
            self.ccs_predefined_check.pack(side="right")
            
            state = 'disabled' if self.use_predefined_ccs.get() else 'normal'
            for entry in self.ccs_entries:
                entry.configure(state=state)
            
            if self.use_predefined_ccs.get() and self.fuel_type.get():
                self.update_predefined_ccs_values()
        else:
            self.ccs_frame.pack_forget()
            self.ccs_predefined_check.pack_forget()

    def update_predefined_ccs_values(self):
        if self.fuel_type.get() in self.predefined_values:
            ccs_values = self.predefined_values[self.fuel_type.get()]["ccs"]
            self.ccs_capture.set(ccs_values["capture"])
            self.ccs_compression.set(ccs_values["compression"])
            self.ccs_transportation.set(ccs_values["transportation"])
            self.ccs_storage.set(ccs_values["storage"])

    def collect_data(self):
        try:
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
            
            for field, (var, name) in required_fields.items():
                try:
                    value = float(var.get())
                    if value <= 0 and field not in ['plant_efficiency']:
                        errors.append(f"{name} must be greater than 0")
                    input_data[field] = value
                except (ValueError, tk.TclError):
                    errors.append(f"Invalid {name} value")
            
            if errors:
                self.error_label.config(text="\n".join(errors))
                return
                
            input_data.update({
                'plant_location': self.plant_location.get(),
                'ccs': self.ccs.get(),
                'ccs_capture': float(self.ccs_capture.get()) if self.ccs.get() else 0,
                'ccs_compression': float(self.ccs_compression.get()) if self.ccs.get() else 0,
                'ccs_transportation': float(self.ccs_transportation.get()) if self.ccs.get() else 0,
                'ccs_storage': float(self.ccs_storage.get()) if self.ccs.get() else 0,
                'include_emissions': self.include_emissions.get(),
                'emissions_value': float(self.emissions_value.get()) if self.include_emissions.get() else 0,
                'emissions_value': float(self.emissions_value.get()) if self.include_emissions.get() else 0,
                'sensitivity_value': float(self.sensitivity_value.get()) if self.sensitivity_value.get() and self.sensitivity_value.get().strip() else 5,
                'ccs_sensitivity_value': float(self.ccs_sensitivity_value.get()) if self.ccs_sensitivity_value.get() and self.ccs_sensitivity_value.get().strip() else 5,
                'fuel_type': self.fuel_type.get()
            })
            
            self.controller.frames[ResultScreen].display_results(input_data)
            self.controller.show_frame(ResultScreen)
            
        except Exception as e:
            self.error_label.config(text=f"Error: {str(e)}")

    def reset_form(self):
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
        self.sensitivity_value.set('')
        self.ccs_sensitivity_value.set('')
        self.ccs_capture.set(0.0)
        self.ccs_compression.set(0.0)
        self.ccs_transportation.set(0.0)
        self.ccs_storage.set(0.0)
        
        self.use_predefined.set(True)
        self.use_predefined_ccs.set(True)
        
        for entry in [self.efficiency_entry, self.output_entry, 
                    self.emissions_entry, self.sensitivity_entry, self.ccs_sensitivity_entry]:
            self.set_placeholder(entry)
        
        self.error_label.config(text="")
        
        self.toggle_ccs_fields()
        self.toggle_input_fields()


class ResultScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ensure scrollable frame expands to fill width
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window_id, width=e.width)
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        ttk.Label(self.scrollable_frame, 
                 text="Results Summary", 
                 font=(self.controller.system_font, 16, "bold")
                ).pack(pady=20, anchor="center")

        self.overview_frame = ttk.LabelFrame(self.scrollable_frame, text="Key Metrics")
        self.overview_frame.pack(fill="x", padx=20, pady=10, ipadx=10, ipady=10)
        
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

        self.graphs_container = ttk.Frame(self.scrollable_frame)
        self.graphs_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Configure Grid
        self.graphs_container.columnconfigure(0, weight=1)
        self.graphs_container.columnconfigure(1, weight=1)

        # 1. Pie Chart (Energy Contribution) - Top Left
        self.energy_frame = ttk.LabelFrame(self.graphs_container, text="Energy Contribution (Share)")
        self.energy_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        self.pie_chart_canvas = tk.Canvas(self.energy_frame, height=300, width=400, bg="white")
        self.pie_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.pie_chart_canvas.bind("<Configure>", lambda e: self.draw_pie_chart())

        # 2. CCS Sensitivity - Top Right
        self.sensitivity_frame = ttk.LabelFrame(self.graphs_container, text="CCS Efficiency Sensitivity Analysis")
        self.sensitivity_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        self.line_chart_canvas = tk.Canvas(self.sensitivity_frame, height=300, width=350, bg="white")
        self.line_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.line_chart_canvas.bind("<Configure>", lambda e: self.draw_line_chart())

        # 3. General Sensitivity - Bottom Center
        self.general_sens_frame = ttk.LabelFrame(self.graphs_container, text="General Sensitivity Analysis")
        self.general_sens_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)
        
        self.general_chart_canvas = tk.Canvas(self.general_sens_frame, height=300, width=800, bg="white")
        self.general_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.general_chart_canvas.bind("<Configure>", lambda e: self.draw_general_sensitivity_chart())

        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill="x", pady=20)
        back_button = ttk.Button(button_frame, 
                               text="Back to Home", 
                               command=lambda: controller.show_frame(HomeScreen))
        back_button.pack(anchor="center")

        self.stages = ["Extraction", "Processing", "Transportation", "CCS"]
        self.energy_values = [0, 0, 0, 0]
        self.ccs_percentages = [80, 85, 90, 95, 100]
        self.efficiency_values = [0, 0, 0, 0, 0]
        self.general_sens_percentages = []
        self.general_sens_efficiencies = []

    def display_results(self, input_data, save_to_db=True):
        """Calculate and display all results with error handling"""
        results = calculate_results(input_data)
        
        if 'error' in results:
            self.total_efficiency_label.config(
                text=f"Calculation Error: {results['error']}",
                foreground='red'
            )
            self.efficiency_drop_label.config(text="")
            self.total_emissions_label.config(text="")
            return
        
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
        
        # Save to database
        if save_to_db:
            db.save_calculation(input_data, results)
        
        self.energy_values = [
            results['energy_contributions']['extraction'],
            results['energy_contributions']['processing'],
            results['energy_contributions']['transportation'],
            results['energy_contributions']['ccs']
        ]
        
        self.efficiency_values = results['ccs_sensitivity']
        self.ccs_percentages = results.get('ccs_sensitivity_percentages', [80, 85, 90, 95, 100])
        
        # General Sensitivity Data
        if 'general_sensitivity' in results:
            self.general_sens_percentages = results['general_sensitivity'].get('percentages', [])
            self.general_sens_efficiencies = results['general_sensitivity'].get('efficiencies', [])
        else:
            self.general_sens_percentages = []
            self.general_sens_efficiencies = []
        
        self.draw_pie_chart()
        self.draw_line_chart()
        self.draw_general_sensitivity_chart()

    def draw_pie_chart(self):
        self.pie_chart_canvas.delete("all")
        width = self.pie_chart_canvas.winfo_width()
        height = self.pie_chart_canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
            
        # Filter zero values
        data = []
        labels = []
        for val, stage in zip(self.energy_values, self.stages):
            if val > 0:
                data.append(val)
                labels.append(stage)
        
        if not data:
            self.pie_chart_canvas.create_text(width/2, height/2, text="No Data")
            return
            
        total = sum(data)
        
        # Colors for pie chart
        colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2"]
        
        # Draw Pie
        x_center, y_center = width / 2 - 50, height / 2  # Shift left to make room for legend
        radius = min(width, height) / 2 - 20
        start_angle = 90
        
        for i, (val, label) in enumerate(zip(data, labels)):
            extent = (val / total) * 360
            color = colors[i % len(colors)]
            
            self.pie_chart_canvas.create_arc(
                x_center - radius, y_center - radius,
                x_center + radius, y_center + radius,
                start=start_angle, extent=extent,
                fill=color, outline="white"
            )
            
            # Draw Legend
            legend_x = width - 150
            legend_x = x_center + radius + 20
            
            legend_y = y_center - radius + i * 30
            self.pie_chart_canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15, fill=color, outline="")
            self.pie_chart_canvas.create_text(legend_x + 25, legend_y + 7, text=f"{label} ({val/total*100:.1f}%)", anchor="w", font=("Arial", 9))
            
            start_angle += extent

    def draw_line_chart(self):
        self.line_chart_canvas.delete("all")
        width = self.line_chart_canvas.winfo_width()
        height = self.line_chart_canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
            
        max_val = max(self.efficiency_values) if self.efficiency_values else 0
        min_val = min(self.efficiency_values) if self.efficiency_values else 0
        
        # Calculate Interval (Ratio)
        min_p = min(self.ccs_percentages)
        max_p = max(self.ccs_percentages)
        num = len(self.ccs_percentages)
        interval = (max_p - min_p) / (num - 1) if num > 1 else 5
        
        dynamic_padding = interval * 0.25
        
        # Add dynamic padding (Y-axis)
        max_eff = max_val + dynamic_padding
        min_eff = max(0, min_val - dynamic_padding)
        range_eff = max_eff - min_eff if max_eff != min_eff else 1
        
        # -- Flexible Padding Definition --
        PAD_LEFT = 100
        PAD_RIGHT = 40
        PAD_TOP = 40
        PAD_BOTTOM = 80
        
        # Helper: Chart area dimensions
        chart_w = width - PAD_LEFT - PAD_RIGHT
        chart_h = height - PAD_TOP - PAD_BOTTOM
        
        # 1. Draw Axes
        # X-Axis line
        self.line_chart_canvas.create_line(PAD_LEFT, height - PAD_BOTTOM, width - PAD_RIGHT, height - PAD_BOTTOM)
        # Y-Axis line
        self.line_chart_canvas.create_line(PAD_LEFT, PAD_TOP, PAD_LEFT, height - PAD_BOTTOM)
        
        # 2. Draw Axis Titles
        # X-Axis Title (Centered in the bottom margin)
        # Position: Center of chart width + left offset, vertical center of bottom margin
        x_title_x = PAD_LEFT + (chart_w // 2)
        x_title_y = height - (PAD_BOTTOM // 3) # Roughly 1/3 up from bottom edge
        self.line_chart_canvas.create_text(x_title_x, x_title_y, 
                                         text="CCS Percentage (%)", 
                                         anchor="center",
                                         font=("Arial", 9, "bold"))
                                         
        # Y-Axis Title (Rotated, centered in left margin)
        # Position: Horizontal center of left margin (e.g., 20px in), vertical center of chart
        y_title_x = PAD_LEFT // 3
        y_title_y = PAD_TOP + (chart_h // 2)
        self.line_chart_canvas.create_text(y_title_x, y_title_y, 
                                         text="Efficiency (%)", 
                                         anchor="center", 
                                         angle=90,
                                         font=("Arial", 9, "bold"))
        
        # 3. Y-Axis Values (Max/Min)
        # Position: Right-aligned against the Y-axis line (PAD_LEFT - small gap)
        # Using a gap of 5px
        axis_gap = 5
        self.line_chart_canvas.create_text(PAD_LEFT - axis_gap, PAD_TOP, 
                                         text=f"{max_eff:.1f}", 
                                         anchor="e", 
                                         font=("Arial", 8))
        self.line_chart_canvas.create_text(PAD_LEFT - axis_gap, height - PAD_BOTTOM, 
                                         text=f"{min_eff:.1f}", 
                                         anchor="e", 
                                         font=("Arial", 8))
        
        prev_x, prev_y = None, None
        
        num_points = len(self.ccs_percentages)
        if num_points < 2: return

        # X-Axis with dynamic padding
        min_val_p = min(self.ccs_percentages)
        max_val_p = max(self.ccs_percentages)
        
        min_p = min_val_p - dynamic_padding
        max_p = max_val_p + dynamic_padding
        range_p = max_p - min_p if max_p != min_p else 1

        # 4. Plot Data Points
        for percentage, efficiency in zip(self.ccs_percentages, self.efficiency_values):
            # Map Percentage -> X Coordinate
            # Formula: left_pad + ( (val - min) / range ) * chart_width
            x = PAD_LEFT + ((percentage - min_p) / range_p) * chart_w
            
            # Map Efficiency -> Y Coordinate
            # Formula: bottom_y - ( (val - min) / range ) * chart_height
            # (Note: Tkinter Y grows downwards, so we subtract from bottom limit)
            y = height - PAD_BOTTOM - ((efficiency - min_eff) / range_eff) * chart_h
            
            # Draw Data Point
            self.line_chart_canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")
            
            # Draw X-Axis Label (Value below axis)
            self.line_chart_canvas.create_text(x, height - PAD_BOTTOM + 15, 
                                             text=f"{percentage}%", 
                                             anchor="center",
                                             font=("Arial", 8))
            
            # Draw Data Label (Value above point)
            self.line_chart_canvas.create_text(x, y - 15, 
                                             text=f"{efficiency:.1f}%", 
                                             anchor="s",
                                             font=("Arial", 8))
            
            # Connect the dots
            if prev_x is not None:
                self.line_chart_canvas.create_line(prev_x, prev_y, x, y, fill="blue", width=2)
            
            prev_x, prev_y = x, y

    def draw_general_sensitivity_chart(self):
        self.general_chart_canvas.delete("all")
        width = self.general_chart_canvas.winfo_width()
        height = self.general_chart_canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
            
        percentages = self.general_sens_percentages
        efficiencies = self.general_sens_efficiencies
        
        if not percentages or not efficiencies:
            return
            
        max_val = max(efficiencies) if efficiencies else 0
        min_val = min(efficiencies) if efficiencies else 0
        
        # Calculate Interval (Ratio)
        min_p = min(percentages)
        max_p = max(percentages)
        num = len(percentages)
        interval = (max_p - min_p) / (num - 1) if num > 1 else 5
        
        dynamic_padding = interval * 0.25
        
        # Add dynamic padding (Y-axis)
        max_eff = max_val + dynamic_padding
        min_eff = max(0, min_val - dynamic_padding)
        range_eff = max_eff - min_eff if max_eff != min_eff else 1
        
        # -- Flexible Padding Definition --
        PAD_LEFT = 100
        PAD_RIGHT = 40
        PAD_TOP = 40
        PAD_BOTTOM = 80
        
        chart_w = width - PAD_LEFT - PAD_RIGHT
        chart_h = height - PAD_TOP - PAD_BOTTOM
        
        # 1. Draw Axes
        self.general_chart_canvas.create_line(PAD_LEFT, height - PAD_BOTTOM, width - PAD_RIGHT, height - PAD_BOTTOM)
        self.general_chart_canvas.create_line(PAD_LEFT, PAD_TOP, PAD_LEFT, height - PAD_BOTTOM)
        
        # 2. Draw General Axis Titles
        x_title_x = PAD_LEFT + (chart_w // 2)
        x_title_y = height - (PAD_BOTTOM // 3)
        self.general_chart_canvas.create_text(x_title_x, x_title_y, 
                                         text="Contrib. Percentage (Gener. const.) (%)", 
                                         anchor="center",
                                         font=("Arial", 9, "bold"))
                                         
        y_title_x = PAD_LEFT // 3
        y_title_y = PAD_TOP + (chart_h // 2)
        self.general_chart_canvas.create_text(y_title_x, y_title_y, 
                                         text="Efficiency (%)", 
                                         anchor="center", 
                                         angle=90,
                                         font=("Arial", 9, "bold"))
        
        # 3. Y-Axis Values
        axis_gap = 5
        self.general_chart_canvas.create_text(PAD_LEFT - axis_gap, PAD_TOP, 
                                         text=f"{max_eff:.1f}", 
                                         anchor="e", 
                                         font=("Arial", 8))
        self.general_chart_canvas.create_text(PAD_LEFT - axis_gap, height - PAD_BOTTOM, 
                                         text=f"{min_eff:.1f}", 
                                         anchor="e", 
                                         font=("Arial", 8))
        
        prev_x, prev_y = None, None
        
        num_points = len(percentages)
        if num_points < 2: return
        
        # X-Axis with dynamic padding
        min_val_p = min(percentages)
        max_val_p = max(percentages)
        
        min_p = min_val_p - dynamic_padding
        max_p = max_val_p + dynamic_padding
        range_p = max_p - min_p if max_p != min_p else 1
        
        # 4. Plot Points
        for percentage, efficiency in zip(percentages, efficiencies):
            # Map Percentage -> X
            x = PAD_LEFT + ((percentage - min_p) / range_p) * chart_w
            
            # Map Efficiency -> Y
            y = height - PAD_BOTTOM - ((efficiency - min_eff) / range_eff) * chart_h
            
            # Point
            self.general_chart_canvas.create_oval(x-3, y-3, x+3, y+3, fill="green")
            
            # X Label
            self.general_chart_canvas.create_text(x, height - PAD_BOTTOM + 15, 
                                             text=f"{percentage}%", 
                                             anchor="center",
                                             font=("Arial", 8))
            
            # Data Label
            self.general_chart_canvas.create_text(x, y - 15, 
                                             text=f"{efficiency:.1f}%", 
                                             anchor="s",
                                             font=("Arial", 8))
            
            # Line
            if prev_x is not None:
                self.general_chart_canvas.create_line(prev_x, prev_y, x, y, fill="darkgreen", width=2)
            
            prev_x, prev_y = x, y

    def on_show(self):
        self.draw_pie_chart()
        self.draw_line_chart()
        self.draw_general_sensitivity_chart()

class HistoryScreen(FrameManager):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        
        # Title
        ttk.Label(self, text="Calculation History", font=(self.controller.system_font, 24, "bold")).pack(pady=20)
        
        # Table Frame
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Columns
        self.columns = [
            {"text": "ID", "stretch": False, "width": 0}, # Hidden
            {"text": "Location", "stretch": True},
            {"text": "Fuel", "stretch": True},
            {"text": "Efficiency", "stretch": True},
            {"text": "Drop", "stretch": True},
            {"text": "Date", "stretch": True},
        ]
        
        self.table = Tableview(
            master=self.table_frame,
            coldata=self.columns,
            rowdata=[],
            paginated=True,
            pagesize=20,
            height=20,
            searchable=True,
            bootstyle=PRIMARY,
        )
        self.table.pack(fill="both", expand=True)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame(HomeScreen)).pack(side="left")
        ttk.Button(button_frame, text="View Selected", command=self.view_selected, bootstyle=INFO).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected, bootstyle=DANGER).pack(side="right", padx=5)

    def on_show(self):
        self.load_data()

    def load_data(self):
        history = db.get_history()
        
        rowdata = []
        self.map_id_to_data = {} 
        
        for item in history:
            timestamp = item['timestamp']
            
            # Format timestamp safely
            # YYYY-MM-DD HH:MM
            try:
                from datetime import datetime
                if isinstance(timestamp, str):
                    # Check if seconds are present
                    if len(timestamp) > 16:
                        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") if '.' in timestamp else datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except Exception as e:
                print(f"Date parsing error: {e}")
                pass # Fallback to original
            
            total_eff = f"{item['total_efficiency']:.2f}%"
            eff_drop = f"{item['efficiency_drop']:.2f}%"
            
            # Reordered to match columns: ID, Location, Fuel, Eff, Drop, Date
            row = (item['id'], item['plant_location'], item['fuel_type'], total_eff, eff_drop, timestamp)
            rowdata.append(row)
            self.map_id_to_data[item['id']] = item

        self.table.build_table_data(self.columns, rowdata)
        self.table.load_table_data()

    def view_selected(self):
        selected_rows = self.table.get_rows(selected=True)
        if not selected_rows:
            return
            
        for row in selected_rows:
            calc_id = row.values[0]
            if calc_id in self.map_id_to_data:
                item = self.map_id_to_data[calc_id]
                self.load_history_result(item['inputs_json'])
                break # View only one

    def delete_selected(self):
        selected_rows = self.table.get_rows(selected=True)
        if not selected_rows:
            return
            
        from tkinter import messagebox
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected calculations?"):
            return

        deleted_ids = []
        for row in selected_rows:
            calc_id = row.values[0]
            if db.delete_calculation(calc_id):
                deleted_ids.append(calc_id)
        
        if deleted_ids:
             self.load_data()
        
    def load_history_result(self, inputs_json):
        try:
            import json
            input_data = json.loads(inputs_json)
            self.controller.frames[ResultScreen].display_results(input_data, save_to_db=False)
            self.controller.show_frame(ResultScreen)
        except Exception as e:
            print(f"Error loading history: {e}")

