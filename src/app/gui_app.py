import tkinter as tk
from tkinter import ttk, messagebox
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import datetime
import os

# Add project root to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.model.inference import PricePredictor
from src.utils.config_loader import ConfigLoader

class CarPriceApp:
    def __init__(self, root):
        self.root = root
        
        # Load Config
        try:
            self.full_config = ConfigLoader.get_config()
            self.app_config = self.full_config['app']
            self.theme = self.app_config['theme']
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load configuration:\n{e}")
            sys.exit(1)

        self.root.title(self.app_config.get("title", "Car Price Estimator"))
        self.root.geometry(self.app_config.get("window_size", "800x950"))
        self.root.resizable(True, True)

        # 1. Load Model
        try:
            self.predictor = PricePredictor()
            print("✅ Model and columns loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model!\n{e}")
            sys.exit()

        # 2. Define Options
        # Assuming these keys match the keys in config.json logic (though explicit list is safer for GUI order)
        self.fuel_types = list(self.full_config['model']['fuel_mapping'].keys())
        self.transmissions = list(self.full_config['model']['transmission_mapping'].keys())
        self.brands = self.predictor.get_clean_brands()

        # 3. Create Design
        self.create_widgets()

    def create_widgets(self):
        # --- STYLES ---
        font_family = self.app_config.get("font_family", "Segoe UI")
        bg_primary = self.theme.get("bg_primary", "#2b2b2b")
        bg_secondary = self.theme.get("bg_secondary", "#1e1e1e")
        accent_color = self.theme.get("accent_color", "#007acc")
        text_main = self.theme.get("text_main", "white")
        text_secondary = self.theme.get("text_secondary", "#aaaaaa")
        text_muted = self.theme.get("text_muted", "#dddddd")
        btn_fg = self.theme.get("button_fg", "black")
        success_color = self.theme.get("success_color", "#4CAF50")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=(font_family, 12), background=bg_primary, foreground=text_main)
        style.configure("TButton", font=(font_family, 12, "bold"), background=accent_color, foreground=text_main)

        self.root.configure(bg=bg_primary)

        # --- HEADER ---
        header = tk.Frame(self.root, bg=bg_secondary, pady=20)
        header.pack(fill=tk.X)
        tk.Label(header, text="AI Car Market Analyzer", font=(font_family, 26, "bold"), bg=bg_secondary, fg=text_main).pack()
        tk.Label(header, text="Market Price Prediction & Future Trends", font=(font_family, 11), bg=bg_secondary,
                 fg=text_secondary).pack()

        # --- FORM (Using PACK for stability on Mac) ---
        form_frame = tk.Frame(self.root, bg=bg_primary, padx=40, pady=20)
        form_frame.pack(fill=tk.X)

        def add_field(label_text, variable, values=None, is_entry=False):
            container = tk.Frame(form_frame, bg=bg_primary, pady=5)
            container.pack(fill=tk.X)

            lbl = tk.Label(container, text=label_text, font=(font_family, 12), bg=bg_primary, fg=text_muted, width=20,
                           anchor="w")
            lbl.pack(side=tk.LEFT)

            if is_entry:
                widget = ttk.Entry(container, width=30)
                widget.pack(side=tk.LEFT, padx=10)
                return widget
            else:
                widget = ttk.Combobox(container, textvariable=variable, values=values, state="readonly", width=28)
                widget.pack(side=tk.LEFT, padx=10)
                return widget

        # 1. Brand
        self.brand_var = tk.StringVar()
        self.brand_cb = add_field("Značka vozidla:", self.brand_var, values=self.brands)
        if self.brands: self.brand_cb.current(0)

        # 2. Year
        self.year_entry = add_field("Rok výroby:", None, is_entry=True)
        self.year_entry.insert(0, str(datetime.datetime.now().year - 4))

        # 3. Mileage
        self.mileage_entry = add_field("Nájezd (km):", None, is_entry=True)
        self.mileage_entry.insert(0, "65000")

        # 4. Fuel
        self.fuel_var = tk.StringVar()
        self.fuel_cb = add_field("Palivo:", self.fuel_var, values=self.fuel_types)
        if self.fuel_types: self.fuel_cb.current(0)

        # 5. Transmission
        self.trans_var = tk.StringVar()
        self.trans_cb = add_field("Převodovka:", self.trans_var, values=self.transmissions)
        if self.transmissions: self.trans_cb.current(0)

        # --- BUTTON ---
        btn_frame = tk.Frame(self.root, bg=bg_primary, pady=20)
        btn_frame.pack(fill=tk.X)
        
        btn = tk.Button(btn_frame, text="SPOČÍTAT CENU A PREDIKCI", command=self.calculate_all,
                        bg=accent_color, fg=btn_fg, font=(font_family, 13, "bold"), padx=30, pady=12, relief="flat")
        btn.pack()

        # --- RESULT ---
        self.result_label = tk.Label(self.root, text="Zadejte údaje a klikněte na tlačítko",
                                     font=(font_family, 18, "bold"), bg=bg_primary, fg=success_color)
        self.result_label.pack(pady=10)

        # --- GRAPH ---
        self.graph_frame = tk.Frame(self.root, bg=bg_primary)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calculate_all(self):
        try:
            current_price = self.predict_current_price()
            if current_price is None: return

            formatted = f"{int(current_price):,}".replace(",", " ")
            self.result_label.config(text=f"Odhad ceny: {formatted} Kč")

            self.plot_future_trend(current_price)

        except Exception as e:
            messagebox.showerror("Kritická chyba", str(e))

    def predict_current_price(self):
        # --- VALIDATION ---
        try:
            year = int(self.year_entry.get())
            mileage = int(self.mileage_entry.get())
        except ValueError:
            messagebox.showwarning("Chyba", "Rok a nájezd musí být čísla!")
            return None

        current_year = datetime.datetime.now().year
        if year < 1980 or year > current_year + 1:
            messagebox.showwarning("Chyba", f"Rok musí být mezi 1980 a {current_year + 1}.")
            return None

        if mileage < 0 or mileage > 2000000:
            messagebox.showwarning("Chyba", "Nájezd je mimo reálný rozsah.")
            return None

        brand = self.brand_var.get()
        fuel = self.fuel_var.get()
        trans = self.trans_var.get()

        if not brand:
            messagebox.showwarning("Chyba", "Vyberte značku vozidla!")
            return None

        # --- VALIDATE INPUT ---
        try:
            self.predictor.validate_input(brand, fuel, trans)
        except ValueError as ve:
             messagebox.showwarning("Neplatná Konfigurace", str(ve))
             return None

        # --- USE PREDICTOR ---
        try:
            price = self.predictor.predict_price(year, mileage, brand, fuel, trans)
            return price
        except Exception as e:
            messagebox.showerror("Chyba Predikce", str(e))
            return None

    def plot_future_trend(self, start_price):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        bg_primary = self.theme.get("bg_primary", "#2b2b2b")
        text_main = self.theme.get("text_main", "white")
        accent_color = self.theme.get("accent_color", "#007acc")
        success_color = self.theme.get("success_color", "#4CAF50")

        # Config loaded params
        # future_values calculation now uses defaults from config inside inference.py if not passed
        # OR we pass them explicitly
        future_data = self.predictor.calculate_future_value(start_price) 
        years = [d['year'] for d in future_data]
        prices = [d['price'] for d in future_data]

        # Použití Figure objektu místo pyplot (předejití memory leak)
        fig = Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor(bg_primary)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_primary)

        ax.plot(years, prices, marker='o', linestyle='-', color=accent_color, linewidth=3, markersize=8)

        # Barvy grafu (aby byly vidět na tmavém pozadí)
        for spine in ax.spines.values():
            spine.set_color(text_main)

        ax.tick_params(colors=text_main)
        ax.yaxis.label.set_color(text_main)
        ax.xaxis.label.set_color(text_main)
        ax.set_title(f"Predikce vývoje ceny ({years[0]}-{years[-1]})", fontsize=12, color=text_main)
        ax.set_ylabel("Cena (Kč)", color=text_main)
        ax.grid(True, linestyle='--', alpha=0.3, color=text_main)

        # Format Y-axis to avoid scientific notation and use 'k' or 'M'
        def currency_formatter(x, pos):
            if x >= 1_000_000:
                return f'{x*1e-6:.1f}M'
            else:
                return f'{x*1e-3:.0f}k'

        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        # Popisky
        for i, price in enumerate(prices):
            formatted_k = f"{int(price / 1000)}k"
            ax.annotate(formatted_k, (years[i], prices[i]), textcoords="offset points", xytext=(0, 10), ha='center',
                        color=success_color, fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = CarPriceApp(root)
    root.mainloop()