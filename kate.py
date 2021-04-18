from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from settings import TOKEN
from geopy.geocoders import Nominatim
import requests
import random
from sqlalchemy import *
from settings import path_to_db
from sqlalchemy.sql import select

apikey = "40d1649f-0493-4b70-98ba-98533de7710b"


class BotWrapper:
    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))
        self.dispatcher.add_handler(CallbackQueryHandler(self.callback_message))
        self.engine = create_engine(path_to_db, connect_args={'check_same_thread': False})
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        self.cities_ = ["Paris", "London", "Saint Petersburg", "Barcelona", "Berlin", "Madrid",
                   "Kyiv", "Birmingham", "Rome", "Manchester", "Minsk", "Bucharest", "Vienna",
                   "Hamburg", "Warsaw", "Budapest", "Newcastle", "Munich", "Belgrade", "Milan",
                   "Sofia", "Prague", "Sevilla", "Dublin", "Copenhagen", "Cologne", "Amsterdam",
                   "Odesa", "Rotterdam", "Stockholm", "Zagreb", "Riga", "Oslo", "Athens", "Helsinki",
                   "Skopje", "Dnipro", "Glasgow", "Naples", "Turin", "Marseille", "Liverpool", "Portsmouth",
                   "Valencia", "Nottingham", "Krakow", "Frankfurt", "Bristol", "Lviv", "Bremen", "Grenoble",
                   "Lodz", "Sheffield", "Palermo", "Zaragoza", "Wroclaw", "Nantes", "Stuttgart", "Dusseldorf",
                   "Gothenburg"]
        self.cities = Table('cities', self.metadata,
                       Column('city_id', Integer, primary_key=True),
                       Column('city', String(16), nullable=False)
                       )
        result = self.connection.execute(select(self.cities.c.city))
        final_cities = random.sample(list(result), 4)
        self.out = [item for t in final_cities for item in t]
        self.right_answer = random.choice(self.out)

    def echo(self, update, context):
        self.create_message()
        long_list = []
        lat_list = []
        for i in self.out:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(i)
            long_list.append(location.longitude)
            lat_list.append(location.latitude)
        map_request = 'http://static-maps.yandex.ru/1.x/?l=sat&pt='
        for i in range(len(self.out)):
            map_request += str(long_list[i]) + ',' + str(lat_list[i]) + ',pm2rdm' + str(i+1)
            if self.out[i] != self.out[-1]:
                map_request += '~'
        response = requests.get(map_request)
        context.bot.send_message(update.message.chat.id, self.message)
        context.bot.send_photo(update.message.chat.id, response.content, reply_markup=self.keyboard)

    def create_message(self):
        self.button_list = []
        self.asked_city = random.choice(self.out)
        for i in range(len(self.out)):
            tag = str(i + 1)
            button = InlineKeyboardButton(tag, callback_data=self.out[i] + ' ' + self.asked_city)
            self.button_list.append(button)
        self.message = 'Под какой цифрой находится ' + str(self.asked_city) + '?'
        self.keyboard = InlineKeyboardMarkup([self.button_list])

    def callback_message(self, update, context):
        callback_data = update.callback_query.data.split()
        if callback_data[0] == callback_data[1]:
            context.bot.send_message(update.callback_query.message.chat.id, 'Great!')
        else:
            context.bot.send_message(update.callback_query.message.chat.id, 'Wrong)')


if __name__ == '__main__':
    bot = BotWrapper(TOKEN)
    bot.updater.start_polling()
    bot.updater.idle()
