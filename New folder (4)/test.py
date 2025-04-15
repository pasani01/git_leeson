import telebot
from google import genai
import pandas as pd

# Initialize the AI client
client = genai.Client(api_key="AIzaSyBgK1llIVF0hWvToJp9lqUFf8S2S5lEbU0")

# Initialize the Telegram bot
bot = telebot.TeleBot("5158250787:AAEsI0d4pcgwyf6EMM2TpcDt548ADA9seOM")

# Define a prompt template
PROMPT_TEMPLATE = (
    "cevapla : {user_input}"
)

# Read the content of the CSV file
def read_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        return df.to_string(index=False)  # Convert DataFrame to string
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return "Dosya okunamadı."

# Open the photo file
def open_photo(file_path):
    try:
        with open(file_path, 'rb') as photo:
            return photo
    except Exception as e:
        print(f"Error opening photo file: {e}")
        return None

# File path to read
FILE_PATH = "info.csv"
file_content = read_csv(FILE_PATH)
photo_file_path = "info.png"

# Dictionary to store user conversation history
user_history = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    # Log the received message
    print(f"Received message from {user_id}: {user_input}")

    # Initialize or update the user's conversation history
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(user_input)

    # Format the conversation history as a string
    conversation_history = "\n".join(user_history[user_id])

    # Format the prompt with the user's input, file content, and conversation history
    prompt = PROMPT_TEMPLATE.format(
        file_content=file_content,
        photo_file=photo_file_path,
        user_input=user_input,
        conversation_history=conversation_history
    )

    try:
        # Generate a response using the AI model
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        # Send the AI-generated response back to the user
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error generating AI response: {e}")
        bot.reply_to(message, "Üzgünüm, bir hata oluştu.")

    # Check if the user requested a photo
    if "fotoğraf" in user_input.lower() or "resim" in user_input.lower():
        photo = open_photo(photo_file_path)
        if photo:
            bot.send_photo(user_id, photo)
            photo.close()
        else:
            bot.reply_to(message, "Üzgünüm, fotoğraf bulunamadı.")

# Start polling for messages with increased timeout
bot.polling(timeout=20, long_polling_timeout=10)