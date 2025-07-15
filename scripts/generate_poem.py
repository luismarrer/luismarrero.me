from datetime import datetime, timedelta
import json



DEEPSEEK_API_KEY = ""
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# Class to interact with an AI API based on the OPENAI API structure (e.g., DeepSeek)
class AI_API:
    """
    Class to interact with an AI API based on the OPENAI API structure (e.g., DeepSeek)
    """
    def __init__(self, api_key: str, url: str, model: str):
        self.api_key = api_key
        self.url = url
        self.model = model
    
    def call(self, prompt):
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
            'messages': [{'role': 'user', 'content': prompt}]
        }

        try:
            response = requests.post(self.url, json=data, headers=headers)
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"] # return the content of the response message
        except requests.exceptions.RequestException as e:
            print(f"Error al hacer la petición: {e}")
            return None


deepseek_api = AI_API(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, "deepseek-chat")
poem = deepseek_api.call("Escribe un breve poema sobre la programación")

if poem:
    json_data = {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "title": poem.split('\n')[0],  # Use the first line as the title
        "poem": poem
    }
else:
    json_data = {
        "date": datetime.today().strftime("%Y-%m-%d"),
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

