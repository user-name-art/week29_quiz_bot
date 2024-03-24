from environs import Env
import vk_api as vk
import redis
import random
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from load_questions_from_file import get_questions_and_answers_from_file


keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)


def handle_new_question_request(event, vk_api, db):
    questions_and_answers = get_questions_and_answers_from_file()
    question = random.choice(list(questions_and_answers))
    answer = questions_and_answers[question]

    user_id = event.user_id
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )
    db.set(f'vk-{user_id}', answer)


def handle_solution_attempt(event, vk_api, db):
    user_id = event.user_id
    users_answer = db.get(f'vk-{user_id}').split('.')[0].strip().lower()
    if event.text.strip().lower() == users_answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )


def handle_give_up(event, vk_api, db):
    user_id = event.user_id
    answer = db.get(f'vk-{user_id}').split('.')[0]
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Правильный ответ: {answer}',
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def main():
    env = Env()
    env.read_env()

    bot_token = env.str('VK_BOT_TOKEN')

    db_url = env.str('DB_URL')
    db_port = env.str('DB_PORT')

    redis_db = redis.Redis(
        host=db_url,
        port=db_port,
        charset='utf-8',
        decode_responses=True
    )

    vk_session = vk.VkApi(token=bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Начать':
                vk_api.messages.send(
                    user_id=event.user_id,
                    message='Привет! Нажми кнопку "Новый вопрос"',
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard()
                )
            elif event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api, db=redis_db)
            elif event.text == 'Сдаться':
                handle_give_up(event, vk_api, db=redis_db)
            else:
                handle_solution_attempt(event, vk_api, db=redis_db)


if __name__ == '__main__':
    main()
