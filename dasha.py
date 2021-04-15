from telegram.ext import Updater, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_token import TOKEN


class BotWrapper:
    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))

    def echo(self, update, context):
        self.create_message()
        context.bot.send_message(update.message.chat.id, self.message, reply_markup=self.keyboard)

    def create_message(self):
        self.question = 'строка?'
        self.answers = ['yes', 'no']
        self.button_list = []
        for i in range(len(self.answers)):
            tag = str(i + 1)
            button = InlineKeyboardButton(tag, callback_data=self.answers[i])
            self.button_list.append(button)
            self.question += '\n ' + str(i + 1) + ' ' + self.answers[i]
        self.message = self.question
        self.keyboard = InlineKeyboardMarkup([self.button_list])


if __name__ == '__main__':
    bot = BotWrapper(TOKEN)
    bot.updater.start_polling()
    bot.updater.idle()
