import requests
import telebot
import schedule
import time
from threading import Thread
from telebot import types

API_KEY = '7663782735:AAHwpvbzEB9ylAJev8UWVkYTfBgHOLkyWag'
CHAT_ID = None
PRAYER_TIMES_API = 'https://api.aladhan.com/v1/timingsByCity?city=Tashkent&country=Uzbekistan&method=99'

bot = telebot.TeleBot(API_KEY)

SAHARLIK_DUOSI = "Saharlik duosi: \nRo‘zamni tutishga niyat qildim bugungi kunning ro‘zasini tutishga Alloh roziligi uchun."
IFTORLIK_DUOSI = "Iftorlik duosi: \nAllohim, Sen uchun ro‘za tutdim va Senga ishonib iftor qildim."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, "Assalomu alaykum! Namoz vaqtlarini eslatib turadigan botga xush kelibsiz.")
    show_buttons(message)
    get_prayer_times()
    schedule_jobs()

# Tugmalarni ko'rsatish funksiyasi
def show_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Namoz vaqtlari")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Quyidagilardan birini tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Namoz vaqtlari")
def show_prayer_times(message):
    timings = get_prayer_times()
    if timings:
        text = (f"📌 Namoz vaqtlari:\n"
                f"Bomdod: {timings['Fajr']}\n"
                f"Quyosh: {timings['Sunrise']}\n"
                f"Peshin: {timings['Dhuhr']}\n"
                f"Asr: {timings['Asr']}\n"
                f"Shom: {timings['Maghrib']}\n"
                f"Xufton: {timings['Isha']}")
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Namoz vaqtlarini olishda xatolik yuz berdi.")

# Namoz vaqtlarini olish
def get_prayer_times():
    response = requests.get(PRAYER_TIMES_API)
    data = response.json()
    if 'data' in data:
        timings = data['data']['timings']
        return timings
    return None

# Xabar yuborish funksiyasi
def send_prayer_reminder(prayer_name, time):
    if CHAT_ID:
        bot.send_message(CHAT_ID, f"{prayer_name} vaqti: {time}")

# Saharlik va iftorlik duolarini yuborish
def send_dua(message):
    if CHAT_ID:
        bot.send_message(CHAT_ID, message)

# Vaqtlarni rejalashtirish
def schedule_jobs():
    timings = get_prayer_times()
    if timings:
        schedule.every().day.at(timings['Fajr']).do(send_prayer_reminder, "Bomdod", timings['Fajr'])
        saharlik_time = (int(timings['Fajr'].split(':')[0]) - 0, int(timings['Fajr'].split(':')[1]) - 5)
        schedule.every().day.at(f"{saharlik_time[0]:02d}:{saharlik_time[1]:02d}").do(send_dua, SAHARLIK_DUOSI)

        schedule.every().day.at(timings['Sunrise']).do(send_prayer_reminder, "Quyosh", timings['Sunrise'])
        schedule.every().day.at(timings['Dhuhr']).do(send_prayer_reminder, "Peshin", timings['Dhuhr'])
        schedule.every().day.at(timings['Asr']).do(send_prayer_reminder, "Asr", timings['Asr'])
        schedule.every().day.at(timings['Maghrib']).do(send_prayer_reminder, "Shom", timings['Maghrib'])
        iftor_time = (int(timings['Maghrib'].split(':')[0]), int(timings['Maghrib'].split(':')[1]) + 5)
        schedule.every().day.at(f"{iftor_time[0]:02d}:{iftor_time[1]:02d}").do(send_dua, IFTORLIK_DUOSI)

        schedule.every().day.at(timings['Isha']).do(send_prayer_reminder, "Xufton", timings['Isha'])
        Thread(target=run_scheduler).start()

# Doimiy ravishda rejalashtirilgan ishlarni bajarish
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.polling()