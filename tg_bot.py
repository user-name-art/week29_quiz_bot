import logging
import random
import redis
import argparse
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
from log_handler import TelegramLogsHandler
from load_questions_from_file import get_questions_and_answers_from_file


logger = logging.getLogger('Logger')


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


def handle_new_question_request(update: Update, context: CallbackContext, db, questions_and_answers):
    question = random.choice(list(questions_and_answers))
    answer = questions_and_answers[question]

    user = update.message.from_user
    update.message.reply_text(question)
    db.set(f'tg-{user.id}', answer)

    return GAME


def handle_solution_attempt(update: Update, context: CallbackContext, db):
    user = update.message.from_user
    users_answer = db.get(f'tg-{user.id}').split('.')[0].strip().lower()
    if update.message.text.strip().lower() == users_answer:
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
    answer = db.get(f'tg-{user.id}').split('.')[0]
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
    db_port = env.str('DB_PORT')
    admin_session_id = env.str('TG_ADMIN_ID')

    parser = argparse.ArgumentParser(
        description='Путь к папке с файлами, содержащими вопросы и ответы.'
        )
    parser.add_argument(
        'folder_path',
        nargs='?',
        default='quiz-questions',
        help='путь к папке с файлами, содержащими вопросы и ответы.'
    )
    folder_path = parser.parse_args().folder_path

    questions_and_answers = get_questions_and_answers_from_file(folder_path)

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_token, admin_session_id))

    redis_db = redis.Redis(
        host=db_url,
        port=db_port,
        charset='utf-8',
        decode_responses=True
    )

    updater = Updater(bot_token)
    logger.info('tg bot started')
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            START: [
                MessageHandler(
                    Filters.regex('^(Новый вопрос)$'),
                    partial(
                        handle_new_question_request,
                        db=redis_db,
                        questions_and_answers=questions_and_answers
                        )
                )
            ],
            GAME: [
                MessageHandler(
                    Filters.regex('^(Новый вопрос)$'),
                    partial(
                        handle_new_question_request,
                        db=redis_db,
                        questions_and_answers=questions_and_answers
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
