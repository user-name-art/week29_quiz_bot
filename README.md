# Боты-помощники в Telegram и VK с обработкой сообщений в DialogFlow

Боты для **Telegram** и **VK** для проведения викторин.

Примеры ботов:
* [Telegram](https://t.me/art_2024_quiz_bot)
* Сообщество [VK](https://vk.com/club225198457)

## Как установить

Скачайте код
```
https://github.com/user-name-art/week29_quiz_bot.git
```
При необходимости создайте виртуальное окружение. Например: 
```
python -m venv .venv
``` 
Установите зависимости:
```
pip install -r requirements.txt
```

## Как запустить

Для работы понадобится файл **.env**. 
* **TG_BOT_TOKEN** токен Telegram-бота.
* **TG_ADMIN_ID** id пользователя в Telegram, который будет получать логи об ошибках ботов. Можно узнать, написав в Telegram специальному боту [@userinfobot](https://telegram.me/userinfobot).
*  **VK_TOKEN** токен бота ВКонтакте.
*  **DB_URL** ссылка на базу данных Redis, которая будет хранить промежуточные результаты. Например, localhost.
*  **DB_PORT** порт базы даннх Redis. По умолчанию 6379.

Боты запускаются по-отдельности соответствующими скриптами:
```
python tg_bot.py
```
или 
```
python vk_bot.py
```
Также понадобятся файлы с вопросами и ответами, примеры которых можно скачать [здесь](https://dvmn.org/media/modules_dist/quiz-questions.zip).

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
