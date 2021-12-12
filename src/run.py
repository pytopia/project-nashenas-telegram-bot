import emoji
from loguru import logger

from src.bot import bot
from src.constants import keyboards, keys, states
from src.db import db
from src.filters import IsAdmin


class Bot:
    """
    Telegram bot to connect two starangers randomly.
    """
    def __init__(self, telebot, mongodb):
        """
        Initialize bot, database, handlers, and filters.
        """
        self.bot = telebot
        self.db = mongodb

        # add custom filters
        self.bot.add_custom_filter(IsAdmin())

        # register handlers
        self.handlers()

        # run bot
        logger.info('Bot is running...')
        self.bot.infinity_polling()

    def handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            """
            /start command handler.
            """
            self.bot.send_message(
                message.chat.id,
                f"Hey <strong>{message.chat.first_name}</strong>!",
                reply_markup=keyboards.main
            )

            self.db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': message.json},
                upsert=True
            )
            self.update_state(message.chat.id, states.main)

        @self.bot.message_handler(regexp=emoji.emojize(keys.random_connect))
        def random_connect(message):
            """
            Randomly connect to another user.
            """
            self.send_message(
                message.chat.id,
                ':busts_in_silhouette: Connecting you to a random stranger...',
                reply_markup=keyboards.exit
            )
            self.update_state(message.chat.id, states.random_connect)

            other_user = self.db.users.find_one(
                {
                    'state': states.random_connect,
                    'chat.id': {'$ne': message.chat.id}
                }
            )

            if not other_user:
                return
            # update other user state
            self.update_state(other_user["chat"]["id"], states.connected)
            self.send_message(
                other_user["chat"]["id"],
                f'Connected to {other_user["chat"]["id"]}...'
            )

            # update current user state
            self.update_state(message.chat.id, states.connected)
            self.send_message(
                message.chat.id,
                f'Connected to {other_user["chat"]["id"]}...'
            )

            # store connected users
            self.db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': {'connected_to': other_user["chat"]["id"]}}
            )
            self.db.users.update_one(
                {'chat.id': other_user["chat"]["id"]},
                {'$set': {'connected_to': message.chat.id}}
            )

        @self.bot.message_handler(regexp=emoji.emojize(keys.exit))
        def exit(message):
            """
            Exit from chat or connecting state.
            """
            self.send_message(
                message.chat.id,
                keys.exit,
                reply_markup=keyboards.main
            )
            self.update_state(message.chat.id, states.main)

            # get connected to user
            connected_to = self.db.users.find_one(
                {'chat.id': message.chat.id}
            )
            if not connected_to:
                return

            # update connected to user state and terminate the connection
            other_chat_id = connected_to['connected_to']
            self.update_state(other_chat_id, states.main)
            self.send_message(
                other_chat_id,
                keys.exit,
                reply_markup=keyboards.main
            )

            # remove connected users
            self.db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': {'connected_to': None}}
            )
            self.db.users.update_one(
                {'chat.id': other_chat_id},
                {'$set': {'connected_to': None}}
            )

        @self.bot.message_handler(func=lambda ـ: True)
        def echo(message):
            """ Echo message to other connected user.
            """
            user = self.db.users.find_one(
                {'chat.id': message.chat.id}
            )

            if ((not user) or (user['state'] != states.connected) or (user['connected_to'] is None)):
                return

            self.send_message(
                user['connected_to'],
                message.text,
            )

    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        """
        Send message to telegram bot.
        """
        if emojize:
            text = emoji.emojize(text, use_aliases=True)

        self.bot.send_message(chat_id, text, reply_markup=reply_markup)

    def update_state(self, chat_id, state):
        """
        Update user state.
        """
        self.db.users.update_one(
            {'chat.id': chat_id},
            {'$set': {'state': state}}
        )

if __name__ == '__main__':
    logger.info('Bot started')
    nashenas_bot = Bot(telebot=bot, mongodb=db)
    nashenas_bot.run()
