import tkinter as tk
from tkinter import messagebox
import requests
import re

# ---------------------- API Fetch Functions ----------------------

def get_country_currency_mapping():
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        country_to_currency = {}

        for country in data:
            if "currencies" in country:
                currency_code = list(country["currencies"].keys())[0]
                country_names = [country["name"]["common"].lower()]
                
                if "altSpellings" in country:
                    country_names.extend([name.lower() for name in country["altSpellings"]])
                
                for name in country_names:
                    country_to_currency[name] = currency_code.upper()

        return country_to_currency
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load country-currency data.\n{e}")
        return {}

def get_supported_currencies():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return set(response.json()["rates"].keys())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch supported currencies.\n{e}")
        return set()

def get_exchange_rates():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["rates"]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch exchange rates.\n{e}")
        return {}

# ---------------------- Conversion Logic ----------------------

def convert_currency(amount, from_currency, to_currency, rates):
    try:
        if from_currency not in rates or to_currency not in rates:
            raise ValueError("Unsupported currency code.")
        return (amount / rates[from_currency]) * rates[to_currency]
    except Exception as e:
        messagebox.showerror("Conversion Error", str(e))
        return None

def parse_input(amount_str, from_str, to_str, supported, country_map):
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        
        from_currency = from_str.strip().lower()
        to_currency = to_str.strip().lower()

        from_currency = country_map.get(from_currency, from_currency.upper())
        to_currency = country_map.get(to_currency, to_currency.upper())

        if from_currency not in supported or to_currency not in supported:
            raise ValueError("Invalid or unsupported currency or country.")

        return amount, from_currency, to_currency
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
        return None, None, None

# ---------------------- GUI App ----------------------

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.supported_currencies = get_supported_currencies()
        self.exchange_rates = get_exchange_rates()
        self.country_currency_map = get_country_currency_mapping()

        # UI Elements
        self.build_gui()

    def build_gui(self):
        tk.Label(self.root, text="Currency Converter", font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Label(self.root, text="Amount:").pack()
        self.amount_entry = tk.Entry(self.root, justify="center")
        self.amount_entry.pack()

        tk.Label(self.root, text="From (currency or country):").pack()
        self.from_entry = tk.Entry(self.root, justify="center")
        self.from_entry.pack()

        tk.Label(self.root, text="To (currency or country):").pack()
        self.to_entry = tk.Entry(self.root, justify="center")
        self.to_entry.pack()

        self.convert_button = tk.Button(self.root, text="Convert", command=self.perform_conversion)
        self.convert_button.pack(pady=10)

        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 12), fg="green")
        self.result_label.pack()

    def perform_conversion(self):
        amount_str = self.amount_entry.get()
        from_str = self.from_entry.get()
        to_str = self.to_entry.get()

        amount, from_currency, to_currency = parse_input(
            amount_str, from_str, to_str,
            self.supported_currencies, self.country_currency_map
        )

        if amount is None:
            return

        result = convert_currency(amount, from_currency, to_currency, self.exchange_rates)
        if result is not None:
            self.result_label.config(text=f"{amount} {from_currency} = {result:.2f} {to_currency}")

# ---------------------- Run App ----------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
