import logging
import random
import redis
from environs import Env
from functools import partial
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from main import get_questions_and_answers_from_file


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


START, GAME = range(2)


def show_quiz_keyboard():
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    return ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\!',
        reply_markup=show_quiz_keyboard()
    )

    return GAME


def handle_new_question_request(update: Update, context: CallbackContext, db):
    questions_and_answers = get_questions_and_answers_from_file()
    question = random.choice(list(questions_and_answers))
    answer = questions_and_answers[question]

    user = update.message.from_user
    update.message.reply_text(question)
    db.set(f'tg-{user.id}', answer)

    return GAME


def handle_solution_attempt(update: Update, context: CallbackContext, db):
    user = update.message.from_user
    users_answer = db.get(f'tg-{user.id}').decode('utf-8').split('.')[0]
    if update.message.text == users_answer:
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми Новый вопрос',
            reply_markup=show_quiz_keyboard()
            )
        return START
    else:
        update.message.reply_text(
            'Неправильно… Попробуешь ещё раз?',
            reply_markup=show_quiz_keyboard()
            )
        return GAME


def handle_give_up(update: Update, context: CallbackContext, db):
    user = update.message.from_user
    answer = db.get(f'tg-{user.id}').decode('utf-8').split('.')[0]
    update.message.reply_text(
            f'Правильный ответ: {answer}',
            reply_markup=show_quiz_keyboard()
            )
    return START


def main() -> None:
    env = Env()
    env.read_env()

    bot_token = env.str('TG_BOT_TOKEN')
    db_url = env.str('DB_URL')
    db_password = env.str('DB_PASSWORD')
    db_port = env.str('DB_PORT')

    redis_db = redis.Redis(
        host=db_url,
        port=db_port,
        password=db_password
    )

    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    dispatcher.bot_data['redis_db'] = redis_db

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            START: [
                MessageHandler(
                    Filters.regex('^(Новый вопрос)$'),
                    partial(
                        handle_new_question_request,
                        db=redis_db
                        )
                )
            ],
            GAME: [
                MessageHandler(
                    Filters.regex('^(Новый вопрос)$'),
                    partial(
                        handle_new_question_request,
                        db=redis_db
                        )
                ),
                MessageHandler(
                    Filters.regex('^(Сдаться)$'),
                    partial(
                        handle_give_up,
                        db=redis_db
                        )
                ),
                MessageHandler(
                    Filters.text,
                    partial(
                        handle_solution_attempt,
                        db=redis_db
                        )
                ),
            ],
        },

        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling(timeout=200)

    updater.idle()


if __name__ == '__main__':
    main()
