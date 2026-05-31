import telebot
import requests

# 1. Вставьте сюда токен вашего бота, полученный от @BotFather
TELEGRAM_TOKEN = "8863925195:AAHsloyjJyzfhiMG0cS3dHDT0sJCpbOKEtU"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Функция обращения к бесплатному ИИ без регистрации
def ask_free_ai(user_message):
    try:
        # Используем открытый API Puter, работающий без авторизации
        url = "https://puter.com"
        payload = {
            "messages": [{"role": "user", "content": user_message}]
        }
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            # Извлекаем текст ответа нейросети
            data = response.json()
            return data['message']['content']
        else:
            return "Извините, сервис ИИ временно перегружен. Попробуйте еще раз."
    except Exception as e:
        return "Ошибка соединения с ИИ. Попробуйте позже."

# Реагируем на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я Telegram-бот со встроенным ИИ. Напиши мне любой вопрос, и я отвечу!")

# Обрабатываем все текстовые сообщения пользователей
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем пользователю статус "печатает...", пока ИИ думает
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Отправляем текст пользователя в ИИ
    ai_response = ask_free_ai(message.text)
    
    # Отправляем ответ ИИ обратно в Telegram
    bot.reply_to(message, ai_response)

# Запуск бота на постоянное ожидание сообщений
print("Бот успешно запущен и готов к работе...")
bot.infinity_polling()
    
