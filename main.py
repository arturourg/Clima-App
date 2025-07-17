# Importar módulos requeridos
import tkinter as tk
from tkinter import messagebox, font
from configparser import ConfigParser
import requests

# URL base de la API y archivo de configuración como constantes
API_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang=es"
CONFIG_FILE = "config.ini"

class WeatherApp:
    def __init__(self, root):
        """Inicializa la aplicación y construye la interfaz gráfica."""
        self.root = root
        self.root.title("Clima App")
        self.root.geometry("350x300")
        
        # Cargar la API Key
        self.api_key = self._load_api_key()
        if not self.api_key:
            messagebox.showerror("Error de Configuración", 
                                 f"No se pudo encontrar la API key en {CONFIG_FILE}.\n"
                                 "Asegúrate de que el archivo existe y tiene el formato correcto.")
            self.root.destroy()
            return
            
        # Crear los widgets de la interfaz
        self._create_widgets()

    def _load_api_key(self):
        """Carga la API key desde el archivo de configuración de forma segura."""
        try:
            config = ConfigParser()
            config.read(CONFIG_FILE)
            return config['gfg']['api']
        except (FileNotFoundError, KeyError):
            return None

    def _create_widgets(self):
        """Crea y posiciona todos los elementos de la interfaz."""
        # --- Estilos ---
        main_font = font.Font(family="Arial", size=12)
        location_font = font.Font(family="Arial", size=20, weight="bold")
        temp_font = font.Font(family="Arial", size=16)
        
        # --- Frame de Entrada ---
        entry_frame = tk.Frame(self.root, pady=10)
        entry_frame.pack(fill='x', padx=10)

        self.city_entry = tk.Entry(entry_frame, font=main_font)
        self.city_entry.pack(side='left', fill='x', expand=True)
        # Permite buscar al presionar "Enter"
        self.city_entry.bind("<Return>", self.search)

        search_button = tk.Button(entry_frame, text="Buscar", command=self.search)
        search_button.pack(side='right', padx=(5, 0))

        # --- Frame de Resultados ---
        result_frame = tk.Frame(self.root, pady=15)
        result_frame.pack(fill='both', expand=True)

        self.location_label = tk.Label(result_frame, text="Ciudad", font=location_font)
        self.location_label.pack(pady=5)

        self.temperature_label = tk.Label(result_frame, text="--°C", font=temp_font)
        self.temperature_label.pack(pady=5)

        self.weather_label = tk.Label(result_frame, text="Condición", font=main_font)
        self.weather_label.pack(pady=5)

    def get_weather(self, city):
        """Obtiene los datos del clima desde la API y los devuelve como un diccionario."""
        try:
            response = requests.get(API_URL.format(city, self.api_key))
            response.raise_for_status()  # Lanza un error para respuestas HTTP malas (4xx o 5xx)
            
            data = response.json()
            
            # Devolver un diccionario en lugar de una lista para mayor claridad
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temp_celsius': data['main']['temp'],
                'description': data['weather'][0]['description'].capitalize()
            }
        except requests.exceptions.HTTPError:
            # Error específico para ciudad no encontrada
            return None
        except requests.exceptions.RequestException as e:
            # Error genérico de red (p.ej. sin conexión)
            messagebox.showerror("Error de Red", f"No se pudo conectar al servidor del clima.\n{e}")
            return None
    
    def search(self, event=None):
        """Maneja el evento de búsqueda y actualiza la interfaz."""
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Entrada Vacía", "Por favor, ingresa el nombre de una ciudad.")
            return

        weather_data = self.get_weather(city)

        if weather_data:
            self.location_label['text'] = f"{weather_data['city']}, {weather_data['country']}"
            self.temperature_label['text'] = f"{weather_data['temp_celsius']:.1f}°C"
            self.weather_label['text'] = weather_data['description']
        else:
            messagebox.showerror('Error', f"No se encontró la ciudad '{city}'.")


if __name__ == "__main__":
    app = tk.Tk()
    WeatherApp(app)
    app.mainloop()

