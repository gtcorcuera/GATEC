import ttkbootstrap as ttk

class Card(ttk.Frame):
    def __init__(self, parent, controller, title, fuel, efficiency_drop, total_efficiency, on_click=None, width=None, height=None, item_width=15):
        super().__init__(parent, relief="solid", padding=(10,10))
        self.controller = controller

        # Create a frame for the two columns
        self.column_frame = ttk.Frame(self)
        self.column_frame.pack(fill="both", expand=True)

        # Column 1 - Flexible width
        self.column1 = ttk.Frame(self.column_frame)
        self.column1.grid(row=0, column=0, sticky="nsew")
        
        # Column 2 - Content based width
        self.column2 = ttk.Frame(self.column_frame)
        self.column2.grid(row=0, column=1, sticky="nsew")

        # Add text to Column 1
        self.title_label = ttk.Label(self.column1, text=title,
                                    font=(self.controller.system_font, 14, "bold"),
                                    anchor="w", justify="left").pack(anchor="w")
        self.eff_drop_label = ttk.Label(self.column1, text=f"Efficiency Drop: {efficiency_drop}",
                                    font=(self.controller.system_font, 10),
                                    anchor="w", justify="left").pack(anchor="w")
        self.eff_label = ttk.Label(self.column1, text=f"Total Efficiency: {total_efficiency}",
                                    font=(self.controller.system_font, 10), anchor="w", justify="left").pack(anchor="w")

        # Add fuel label to Column 2
        fuel_colors = {
            "Coal": "inverse-dark",
            "Natural gas": "inverse-success",
            "Hydrogen": "inverse-info",
            # Add more fuel types as needed
        }
        fuel_color = fuel_colors.get(fuel, "inverse-secondary")  # Default to gray if fuel type not found
        
        # Use consistent width for both buttons
        self.fuel_label = ttk.Label(self.column2, text=fuel,
                                    borderwidth=1, relief="solid",
                                    bootstyle=fuel_color,
                                    padding=(5,5),
                                    anchor='center',
                                    width=item_width
                                    )
        self.fuel_label.pack(anchor="e", padx=5, pady=5) # removed fill/expand to respect width

        self.view_button = ttk.Button(self.column2, text="View results", padding=(5, 5), cursor="hand2",
                                    width=item_width,
                                    command=on_click
                                    )
        self.view_button.pack(anchor="e", padx=5, pady=5) # removed fill/expand to respect width

        # Configure grid weights
        self.column_frame.grid_columnconfigure(0, weight=1)
        self.column_frame.grid_columnconfigure(1, weight=0) # 0 weight for fixed width part
