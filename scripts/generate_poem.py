from datetime import datetime, timedelta, timezone, time
from dotenv import load_dotenv
import json
import os

load_dotenv()  # Load environment variables from .env file in development environment if it exists
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_ai_api_key_here")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def get_best_model_by_time():
    """
    Returns the best model based on the current time.
    This is a placeholder function that can be modified to return different models based on time.

    DeepSeek offers a discounted price between UTC 16:30 and 00:30. Within this hour range, the reasoner model costs the same as the chat model.
    The reasoner model is more powerful and can be used for more complex tasks.
    The idea is to use the reasoner model during this time range and the chat model during the rest of the day.

    DeepSeek pricing: https://api-docs.deepseek.com/quick_start/pricing/
    """
    current_time = datetime.now(timezone.utc)
    if current_time.hour >= 16.5 and current_time.hour < 24.5:
        return "deepseek-reasoner"
    else:
        return "deepseek-chat"

MODEL = get_best_model_by_time()
TEMPERATURE = 0.8  # Adjust the temperature for creativity

# Class to interact with an AI API based on the OPENAI API structure (e.g., DeepSeek)
class AI_API:
    """
    Class to interact with an AI API based on the OPENAI API structure (e.g., DeepSeek)
    """
    def __init__(self, api_key: str, url: str, model: str):
        self.api_key = api_key
        self.url = url
        self.model = model

    def call(self, prompt: str, temperature: float) -> str | None:
        import requests
        """
        Call the AI API with the provided prompt.
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        data = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': temperature,
        }

        try:
            response = requests.post(self.url, json=data, headers=headers)
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"] # return the content of the response message
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"Error al hacer la petición: {e}")
            return None


prompt = """
Escribe un poema breve y original sobre la programación.

Debe comenzar con un título, seguido por una línea en blanco, y luego el poema. No incluyas introducciones, despedidas ni explicaciones. Solo el poema.

Ejemplo de respuesta:

Código y Verso

Eres lógica pura,  
estructura clara,  
sintaxis precisa  
que el mundo declara.

Cada línea un paso,  
cada error, enseñanza,  
y al fin, cuando compila,  
¡qué dulce es la recompensa!

Un bucle de ideas,  
un if en la mente,  
la máquina obedece  
cuando el código es coherente.
""".strip()

deepseek_api = AI_API(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL)
poem = deepseek_api.call(prompt=prompt, temperature=TEMPERATURE)

if poem:
    poem = poem.strip()  # Clean up the poem text
    json_data = {
        "model": MODEL,
        "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),  # Use tomorrow's date for the poem
        "title": poem.split('\n')[0],  # Use the first line as the title
        "poem": poem.split('\n', 1)[1].strip()  # Use the rest as the poem content
    }
else:
    json_data = {
        "model": "Pablo Neruda",
        "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "title": "Poema del día",
        "poem": """Lo distinguimos
como
si fuera
un caballito
diferente de todos
los caballos.
Adornamos
su frente
con una cinta,
le ponemos
al cuello cascabeles colorados,
y a medianoche
vamos a recibirlo
como si fuera
explorador que baja de una estrella.

Como el pan se parece
al pan de ayer,
como un anillo a todos los anillos:
los días
parpadean
claros, tintineante, fugitivos,
y se recuestan en la noche oscura.

Veo el último
día
de este
año
en un ferrocarril, hacia las lluvias
del distante archipiélago morado,
y el hombre
de la máquina,
complicada como un reloj del cielo,
agachando los ojos
a la infinita
pauta de los rieles,
a las brillantes manivelas,
a los veloces vínculos del fuego.

Oh conductor de trenes
desbocados
hacia estaciones
negras de la noche.
Este final
del año
sin mujer y sin hijos,
no es igual al de ayer, al de mañana?
Desde las vías
y las maestranzas
el primer día, la primera aurora
de un año que comienza
tiene el mismo oxidado
color de tren de hierro:
y saludan
los seres del camino,
las vacas, las aldeas,
en el vapor del alba,
sin saber
que se trata
de la puerta del año,
de un día
sacudido
por campanas,
adornado con plumas y claveles,

La tierra
no lo
sabe:
recibirá
este día
dorado, gris, celeste,
lo extenderá en colinas,
lo mojará con
flechas
de
transparente
lluvia,
y luego
lo enrollará
en su tubo,
lo guardará en la sombra.

Así es, pero
pequeña
puerta de la esperanza,
nuevo día del año,
aunque seas igual
como los panes
a todo pan,
te vamos a vivir de otra manera,
te vamos a comer, a florecer,
a esperar.
Te pondremos
como una torta
en nuestra vida,
te encenderemos
como candelabro,
te beberemos
como
si fueras un topacio.

Día
del año
nuevo,
día eléctrico, fresco,
todas
las hojas salen verdes
del
tronco de tu tiempo.

Corónanos
con
agua,
con jazmines
abiertos,
con todos los aromas
desplegados,
sí,
aunque
sólo
seas
un día,
un pobre
día humano,
tu aureola
palpita
sobre tantos
cansados
corazones,
y eres,
oh día
nuevo,
oh nube venidera,
pan nunca visto,
torre
permanente!"""
    }

# Save the poem to a JSON file
file_path = f"src/ai_poems/{json_data['date']}.json"
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)

