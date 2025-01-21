import random
import os
import json
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import google.generativeai as genai

genai.configure(api_key='GEMINI_APIKEY')

# Lista de IDs de usuarios permitidos
USUARIOS_PERMITIDOS = [TELEGRAM_USERID]  # Reemplaza con los IDs de usuario de Telegram

# Archivo para guardar la información de las dietas enviadas a los usuarios
DATA_FILE = 'user_data.json'

# Cargar los datos de los usuarios desde el archivo
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

# Guardar los datos de los usuarios en el archivo
def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)  # Mejor legibilidad con indentación

def get_random_dieta(user_id, user_data, target_week):
    user_id_str = str(user_id)  # Convertir user_id a cadena para que coincida con las claves en el diccionario
    current_time = datetime.now(pytz.timezone('Europe/Madrid'))

    # Verificar si el usuario ya tiene una dieta asignada para la semana objetivo
    if user_id_str in user_data:
        dieta_info = user_data[user_id_str].get('dietas', {})
        
        # Si ya tiene una dieta asignada para la semana objetivo, devolverla
        if target_week in dieta_info:
            return dieta_info[target_week]

    # Elegir una nueva dieta que no se haya repetido en el último mes
    last_month = current_time - timedelta(days=30)
    used_dietas = [
        entry['dieta']
        for entry in user_data.get(user_id_str, {}).get('history', [])
        if datetime.fromisoformat(entry['date']) > last_month
    ]

    available_dietas = [i for i in range(1, 28) if i not in used_dietas]  # Dietas disponibles (1-27)

    if available_dietas:
        new_dieta = random.choice(available_dietas)
    else:
        # Si todas las dietas han sido usadas en el mes, reiniciar la lista
        new_dieta = random.choice(range(1, 28))

    # Actualizar el historial del usuario y asignar la dieta para la semana
    if user_id_str not in user_data:
        user_data[user_id_str] = {'history': [], 'dietas': {}}

    # Guardar la dieta para la semana objetivo
    user_data[user_id_str]['dietas'][target_week] = new_dieta
    user_data[user_id_str]['history'].append({'dieta': new_dieta, 'date': current_time.isoformat()})
    save_user_data(user_data)

    return new_dieta

# Función para verificar si el usuario está permitido
def usuario_permitido(update: Update) -> bool:
    user_id = update.message.from_user.id
    return user_id in USUARIOS_PERMITIDOS

# Función para el comando de inicio
async def start(update: Update, context: CallbackContext) -> None:
    if usuario_permitido(update):
        await update.message.reply_text("¡Hola! Soy tu bot de dietas. Puedes pedirme dietas escribiendo /dieta o los ingredientes con /ingredientes.")
    else:
        await update.message.reply_text("Lo siento, no tienes permiso para usar este bot.")

# Función para el comando dieta
async def dieta(update: Update, context: CallbackContext) -> None:
    if not usuario_permitido(update):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return
    else:
        user_number = update.message.from_user.id
        user_data = load_user_data()    
        current_time = datetime.now(pytz.timezone('Europe/Madrid'))

        # Semana actual y semana siguiente
        current_week_of_year = current_time.strftime("%Y-%U")
        next_week_of_year = (current_time + timedelta(weeks=1)).strftime("%Y-%U")

        # Obtener la dieta para la semana actual
        dieta_actual = get_random_dieta(user_number, user_data, current_week_of_year)
        # Obtener la dieta para la semana siguiente
        dieta_siguiente = get_random_dieta(user_number, user_data, next_week_of_year)

        # Ruta local de las imágenes
        image_path_actual = f'static/{dieta_actual}.jpeg'
        image_path_siguiente = f'static/{dieta_siguiente}.jpeg'

        # Verifica si el archivo de la dieta actual existe antes de intentar abrirlo
        if os.path.exists(image_path_actual):
            # Enviar la imagen de la dieta actual
            with open(image_path_actual, 'rb') as photo_actual:
                await update.message.reply_photo(photo=photo_actual, caption=f"Dieta de esta semana (número {dieta_actual})")
        else:
            await update.message.reply_text("Lo siento, no encontré la imagen de la dieta actual.")

        # Verifica si el archivo de la dieta siguiente existe antes de intentar abrirlo
        if os.path.exists(image_path_siguiente):
            # Enviar la imagen de la dieta siguiente
            with open(image_path_siguiente, 'rb') as photo_siguiente:
                await update.message.reply_photo(photo=photo_siguiente, caption=f"Dieta de la próxima semana (número {dieta_siguiente})")
        else:
            await update.message.reply_text("Lo siento, no encontré la imagen de la dieta de la próxima semana.")

# Nuevo comando para obtener ingredientes de la semana siguiente
async def ingredientes(update: Update, context: CallbackContext) -> None:
    if not usuario_permitido(update):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return
    else:
        user_number = update.message.from_user.id
        user_data = load_user_data()
        current_time = datetime.now(pytz.timezone('Europe/Madrid'))

        # Semana siguiente
        next_week_of_year = (current_time + timedelta(weeks=1)).strftime("%Y-%U")

        # Obtener la dieta para la semana siguiente
        dieta_siguiente = get_random_dieta(user_number, user_data, next_week_of_year)

        # Ruta local de la imagen de la dieta siguiente
        image_path_siguiente = f'static/{dieta_siguiente}.jpeg'

        # Verifica si el archivo de la dieta siguiente existe antes de intentar abrirlo
        if os.path.exists(image_path_siguiente):
            # Enviar la imagen a la API de Google Gemini (o cualquier API de reconocimiento de imagen)
            # Upload the file and print a confirmation.
            sample_file = genai.upload_file(path=image_path_siguiente,
                            display_name="Dieta")

            print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
            
            file = genai.get_file(name=sample_file.name)
            print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")

            # Choose a Gemini model.
            model = genai.GenerativeModel(model_name="gemini-1.5-pro")

            # Prompt the model with text and the previously uploaded image.
            response = model.generate_content([sample_file, "Describe what products i need to buy if i will do this diet, all in spanish, without details: for example one lasagna, tuna, etc"])

            if response.text :
                # Suponiendo que la API devuelva un campo "ingredients" con los ingredientes
                ingredientes = response.text
                await update.message.reply_text(f"Ingredientes para la dieta de la próxima semana: {ingredientes}")
            else:
                await update.message.reply_text("Lo siento, hubo un error al obtener los ingredientes.")
        else:
            await update.message.reply_text("Lo siento, no encontré la imagen de la dieta de la próxima semana.")

# Función principal para configurar el bot
def main():
    # Token del bot
    TOKEN = 'TELEGRAM_BOT_TOKEN'
    # Crear la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Registrar el manejador del comando /start
    application.add_handler(CommandHandler("start", start))

    # Registrar el manejador del comando /dieta
    application.add_handler(CommandHandler("dieta", dieta))

    # Registrar el manejador del comando /ingredientes
    application.add_handler(CommandHandler("ingredientes", ingredientes))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
