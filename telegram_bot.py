from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from settings import TOKEN, path_to_db
from geopy.geocoders import Nominatim
from sqlalchemy import *
from sqlalchemy.sql import select
import requests
import random
from datetime import datetime
import logging



class BotWrapper:
    def __init__(self, token):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.send_message))
        self.dispatcher.add_handler(CallbackQueryHandler(self.callback_message))
        self.dispatcher.add_error_handler(self.catch_exeptions)
        self.engine = create_engine(path_to_db, connect_args={'check_same_thread': False})
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        self.cities = Table('cities', self.metadata,
                       Column('city_id', Integer, primary_key=True),
                       Column('city', String(16), nullable=False)
                       )
        self.statistics = Table('statistics', self.metadata,
                               Column('user_id', Integer, primary_key=True),
                               Column('right_answers', Integer),
                               Column('wrong_answers', Integer),
                               Column('stamp', String)
                       )
        self.result = self.connection.execute(select(self.cities.c.city)).all()

    def catch_exeptions(self, update, context):
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def send_message(self, update, context):
        user_id = update.message.from_user.id
        id_ = self.connection.execute(select(self.statistics.c.user_id)).all()
        id = [item for t in id_ for item in t]
        if not user_id in id:
            self.connection.execute(self.statistics.insert(),
                                    {"user_id": user_id, 'right_answers': 0, 'wrong_answers': 0, 'stamp': ''})

        if update.message.text == 'Reset statistics':
            self.zero_statistics(update, context)
        else:
            self.marks(update, context)
            self.create_reply_button()
            context.bot.send_message(update.message.chat.id, self.message, reply_markup=self.reply_keyboard)
            context.bot.send_photo(update.message.chat.id, self.response.content, reply_markup=self.keyboard)

    def marks(self, update, context):
        long_list = []
        lat_list = []
        self.create_message(update, context)
        for i in self.out:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(i)
            long_list.append(location.longitude)
            lat_list.append(location.latitude)
        map_request = 'http://static-maps.yandex.ru/1.x/?l=sat&pt='
        for i in range(3):
            map_request += str(long_list[i]) + ',' + str(lat_list[i]) + ',pm2rdl' + str(i + 1) + '~'
        map_request += str(long_list[3]) + ',' + str(lat_list[3]) + ',pm2rdl' + '4'
        self.response = requests.get(map_request)

    def create_reply_button(self):
        button = KeyboardButton('Reset statistics')
        self.reply_keyboard = ReplyKeyboardMarkup([[button]], one_time_keyboard=False, resize_keyboard=True)

    def zero_statistics(self, update, context):
        user_id = update.message.from_user.id
        self.connection.execute(self.statistics.update().where(self.statistics.c.user_id == user_id),
                                {'right_answers': 0, 'wrong_answers': 0})
        context.bot.send_message(update.message.chat.id, "Your statistics is reset")

    def create_message(self, update, context):
        now = datetime.now()
        timestamp = str(datetime.timestamp(now))
        try:
            user_id = update.message.from_user.id
        except:
            user_id = update.callback_query.from_user.id
        self.connection.execute(self.statistics.update().where(self.statistics.c.user_id == user_id),
                                {"stamp": timestamp})
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
            button = InlineKeyboardButton(tag, callback_data=self.out[i] + ',' + self.asked_city + ',' + right_answer + ',' + timestamp)
            self.button_list.append(button)
        self.message = 'Which number is ' + str(self.asked_city) + '?'
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
        timestamp = self.connection.execute(
            select(self.statistics.c.stamp).where(self.statistics.c.user_id == user_id)).all()
        stamp = [item for t in timestamp for item in t]
        if callback_data[3] in stamp:
            if callback_data[0] == callback_data[1]:
                for i in right:
                    self.connection.execute(self.statistics.update().where(self.statistics.c.user_id == user_id), {'right_answers': int(i) + 1})
                    for j in wrong:
                        statistic = int((i + 1) / (i + j + 1) * 100)
                context.bot.send_message(update.callback_query.message.chat.id, f'Great!\n{statistic}% of your answers are correct.')

            else:
                for _ in callback_data:
                    if int(callback_data[2]) != 0:
                        for i in wrong:
                            self.connection.execute(self.statistics.update().where(self.statistics.c.user_id == user_id), {'wrong_answers': int(i) + 1})
                            for j in right:
                                statistic = int(j / (i + j + 1) * 100)
                        context.bot.send_message(update.callback_query.message.chat.id, f"Wrong! Right answer was {callback_data[2]}.\n{statistic}% of your answers are correct.")
                        break
            self.create_message(update, context)
            self.marks(update, context)
            context.bot.send_message(update.callback_query.message.chat.id, self.message)
            context.bot.send_photo(update.callback_query.message.chat.id, self.response.content,
                                   reply_markup=self.keyboard)
        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     'You have already answered this question:))))))))')

        update.callback_query.answer()


if __name__ == '__main__':
    bot = BotWrapper(TOKEN)
    bot.updater.start_polling()
    bot.updater.idle()
