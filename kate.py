from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from settings import TOKEN
from geopy.geocoders import Nominatim
from sqlalchemy import *
from sqlalchemy.sql import select
from settings import path_to_db
import requests
import random

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
        self.statistics = Table('statistics', self.metadata,
                               Column('user_id', Integer, primary_key=True),
                               Column('right_answers', Integer),
                               Column('wrong_answers', Integer)
                       )
        self.result = self.connection.execute(select(self.cities.c.city)).all()

    def echo(self, update, context):
        self.marks()
        context.bot.send_message(update.message.chat.id, self.message)
        context.bot.send_photo(update.message.chat.id, self.response.content, reply_markup=self.keyboard)
        user_id = update.message.from_user.id
        id_ = self.connection.execute(select(self.statistics.c.user_id)).all()
        id = [item for t in id_ for item in t]
        if not user_id in id:
            self.connection.execute(self.statistics.insert(), {"user_id": user_id, 'right_answers': 0, 'wrong_answers': 0})

    def marks(self):
        long_list = []
        lat_list = []
        self.create_message()
        for i in self.out:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(i)
            long_list.append(location.longitude)
            lat_list.append(location.latitude)
        map_request = 'http://static-maps.yandex.ru/1.x/?l=sat&pt='
        for i in range(3):
            map_request += str(long_list[i]) + ',' + str(lat_list[i]) + ',pm2rdm' + str(i + 1) + '~'
        map_request += str(long_list[3]) + ',' + str(lat_list[3]) + ',pm2rdm' + '4'
        self.response = requests.get(map_request)

    def create_message(self):
        final_cities = random.sample(list(self.result), 4)
        self.out = [item for t in final_cities for item in t]
        self.button_list = []
        self.asked_city = random.choice(self.out)
        right_answer = '0'
        for i in range(len(self.out)):
            if self.out[i] == self.asked_city:
                right_answer = str(i + 1)
        for i in range(len(self.out)):
            tag = str(i + 1)
            button = InlineKeyboardButton(tag, callback_data=self.out[i] + ',' + self.asked_city + ',' + right_answer)
            self.button_list.append(button)
        self.message = 'Под какой цифрой находится ' + str(self.asked_city) + '?'
        self.keyboard = InlineKeyboardMarkup([self.button_list])

    def callback_message(self, update, context):
        callback_data = update.callback_query.data.split(',')
        user_id = update.callback_query.from_user.id
        right_answers = self.connection.execute(
            select(self.statistics.c.right_answers).where(self.statistics.c.user_id == user_id)).all()
        right = [item for t in right_answers for item in t]
        wrong_answers = self.connection.execute(
            select(self.statistics.c.wrong_answers).where(self.statistics.c.user_id == user_id)).all()
        wrong = [item for t in wrong_answers for item in t]
        if callback_data[0] == callback_data[1]:
            for i in right:
                self.connection.execute(self.statistics.update(), {'right_answers': int(i) + 1})
                for j in wrong:
                    print(i, j)
                    statistic = int((i + 1) / (i + j + 1) * 100)
                    print(statistic)
            context.bot.send_message(update.callback_query.message.chat.id, f'Great! Your score is {statistic}% of right answers')

        else:
            for _ in callback_data:
                if int(callback_data[2]) != 0:
                    for i in wrong:
                        self.connection.execute(self.statistics.update(), {'wrong_answers': int(i) + 1})
                        if i != 0:
                            for j in right:
                                statistic = int(j / (i + j + 1) * 100)
                        else:
                            context.bot.send_message(update.callback_query.message.chat.id,
                                                     f"Wrong! Right answer was {callback_data[2]}. Your score is 0% of right answers")
                            break
                    context.bot.send_message(update.callback_query.message.chat.id, f"Wrong! Right answer was {callback_data[2]}. Your score is {statistic}% of right answers")
                    break
        update.callback_query.answer()
        self.create_message()
        self.marks()
        context.bot.send_message(update.callback_query.message.chat.id, self.message)
        context.bot.send_photo(update.callback_query.message.chat.id, self.response.content,
                               reply_markup=self.keyboard)


if __name__ == '__main__':
    bot = BotWrapper(TOKEN)
    bot.updater.start_polling()
    bot.updater.idle()
