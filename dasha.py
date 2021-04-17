from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_token import TOKEN
from geopy.geocoders import Nominatim
import requests
import random

apikey = "40d1649f-0493-4b70-98ba-98533de7710b"


class BotWrapper:
    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))
        self.dispatcher.add_handler(CallbackQueryHandler(self.callback_message))
        self.cities = ['Paris', 'Berlin', 'London', 'Amsterdam']

    def echo(self, update, context):
        self.create_message()
        long_list = []
        lat_list = []
        for i in self.cities:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(i)
            long_list.append(location.longitude)
            lat_list.append(location.latitude)
        map_request = 'http://static-maps.yandex.ru/1.x/?l=sat&pt='
        for i in range(len(self.cities)):
            map_request += str(long_list[i]) + ',' + str(lat_list[i]) + ',pm2rdm' + str(i+1)
            if self.cities[i] != self.cities[-1]:
                map_request += '~'
        response = requests.get(map_request)
        context.bot.send_message(update.message.chat.id, self.message)
        context.bot.send_photo(update.message.chat.id, response.content, reply_markup=self.keyboard)

    def create_message(self):
        self.button_list = []
        for i in range(len(self.cities)):
            tag = str(i + 1)
            button = InlineKeyboardButton(tag, callback_data=self.cities[i])
            self.button_list.append(button)
        self.asked_city = random.choice(self.cities)
        self.message = 'Под какой цифрой находится ' + str(self.asked_city) + '?'
        self.keyboard = InlineKeyboardMarkup([self.button_list])

    def callback_message(self, update, context):
        context.bot.send_message(update.callback_query.message.chat.id, update.callback_query.data)

    def positions(self):
        for i in self.cities:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(i)
        map_request = 'http://static-maps.yandex.ru/1.x/?ll=' + str(location.longitude) + ',' + str(location.latitude)\
                      + '&spn=20,20&l=sat'
        self.response = requests.get(map_request)


if __name__ == '__main__':
    bot = BotWrapper(TOKEN)
    bot.updater.start_polling()
    bot.updater.idle()
