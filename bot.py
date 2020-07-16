import datetime
import os

from telegram import Bot
from telegram.ext import messagequeue as mq, Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, run_async, CallbackContext

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.utils.request import Request

from test_rss import read_feed, dict_rss_items


def start_command_handler(update, context):
    user_id = update.effective_user.id

    print(f"start_command_handler user_id = {user_id}")

    update.message.reply_text(
        f'ciao {update.message.from_user.first_name}! '
    )


def help_command_handler(update, context):
    """ Show available bot commands"""

    print("help_command_handler")
    print(update)

    try:
        first_name = update.message.chat.first_name
    except AttributeError:
        print("eccezione AttributeError")
        first_name = "-"

    print(f"first_name = {first_name}")

    update.message.reply_text(
        f"questo sarà l'help del bot",
        disable_web_page_preview=True,
        parse_mode='HTML',
    )


def events_command_handler(update, context):

    # il bot mostra gli ultimi n eventi

    counter = 0

    for k, v in dict_rss_items.items():

        print(f"k={k}  v={v}")

        update.message.reply_text(
            f"rss_id={k} {v['title']} /mostra_{k}",
            disable_web_page_preview=True,
            parse_mode='HTML',
        )

        counter = counter + 1
        if counter > 5:
            break


def show_event_command_handler(update, context):

    rss_id = update.message.text.replace('/' + 'mostra_', '')
    if rss_id == '':
        return

    print(rss_id)

    v = dict_rss_items[rss_id]

    update.message.reply_text(
        f"rss_id={rss_id} summary={v['summary']}\n",
        disable_web_page_preview=True,
        parse_mode='HTML',
    )


def update_rss_feed(context: CallbackContext):
    global dict_rss_items

    UNITS_EVENTI_RSS = 'https://www.units.it/feed/eventi'

    read_feed(UNITS_EVENTI_RSS)

    dict_rss_items = dict(reversed(sorted(dict_rss_items.items())))

    # print(dict_rss_items)

    # for k,v in dict_rss_items.items():
    #     print(k)

    print("update_rss_feed ok")


class MQBot(Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            print("MQBot - __del__")
            self._msg_queue.stop()
        except Exception as error:
            print(f"error in MQBot.__del__ : {error}")
            pass

    @mq.queuedmessage
    def send_message(self, chat_id, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""

        e = None
        try:
            return super(MQBot, self).send_message(chat_id, *args, **kwargs)
        except Unauthorized as error:
            # remove chat_id from conversation list
            # orm_user_blocks_bot(chat_id)
            e = error
        except BadRequest as error:
            # handle malformed requests - read more below!
            print("BadRequest")
            e = error
        except TimedOut as error:
            # handle slow connection problems
            print("TimedOut")
            e = error
        except NetworkError as error:
            # handle other connection problems
            print("NetworkError")
            e = error
        except ChatMigrated as error:
            # the chat_id of a group has changed, use e.new_chat_id instead
            print("ChatMigrated")
            e = error
        except TelegramError as error:
            # handle all other telegram related errors
            print("TelegramError")
            e = error


def main():
    print("starting bot...")

    # *** boilerplate start
    from pathlib import Path
    token_file = Path('token.txt')

    token = os.environ.get('TOKEN') or open(token_file).read().strip()
    # None (simile a null in Java)
    print(f"len(token) = {len(token)}")

    # @user2837467823642_bot

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    q = mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=1017)  # 5% safety margin in messaging flood limits
    # set connection pool size for bot
    request = Request(con_pool_size=8)
    my_bot = MQBot(token, request=request, mqueue=q)

    global global_bot_instance
    global_bot_instance = my_bot

    updater = Updater(bot=my_bot, use_context=True)
    dp = updater.dispatcher

    job_queue = updater.job_queue
    # *** boilerplate end

    job_minute = job_queue.run_repeating(update_rss_feed, interval=60*30, first=0)

    dp.add_handler(CommandHandler('start', start_command_handler))
    dp.add_handler(CommandHandler('help', help_command_handler))

    dp.add_handler(CommandHandler('eventi', events_command_handler))

    dp.add_handler(MessageHandler(Filters.regex('^(/' + 'mostra_' + '[\\d]+)$'), show_event_command_handler))

    # dp.add_handler(MessageHandler(Filters.text, generic_message_handler))

    # *** boilerplate start
    # start updater
    updater.start_polling()

    # Stop the bot if you have pressed Ctrl + C or the process has received SIGINT, SIGTERM or SIGABRT
    updater.idle()

    print("terminating bot")

    try:
        request.stop()
        q.stop()
        my_bot.__del__()
    except Exception as e:
        print(e)

    # https://stackoverflow.com/a/40525942/974287
    print("before os._exit")
    os._exit(0)
    # *** boilerplate end


if __name__ == '__main__':
    main()
