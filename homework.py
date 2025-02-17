import logging
import os
import requests
import time

from dotenv import load_dotenv
from telebot import TeleBot

from constants import ENDPOINT, ENV_VARIABLES, HOMEWORK_VERDICTS, RETRY_PERIOD
from exceptions import (
    AbsenceVariableException, homework_statuses, key_verification,
    MissingKeyException, UnexpectedHomeworkStatusException
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def check_tokens():
    """
    Проверяет доступность переменных окружения, которые необходимы для работы
    программы.
    """
    for env_variable in ENV_VARIABLES:
        if os.getenv(env_variable) is None:
            raise AbsenceVariableException(
                f'Отстутствует переменная окружения {env_variable}'
            )


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(
            f'Сбой при отправке сообщения: {error}.'
            f'TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}'
            f'message: {message}'
        )
    else:
        logging.debug(f'Сообщение отправлено: {TELEGRAM_CHAT_ID, message}')


def get_api_answer(timestamp):
    """Делает запрос к API-сервиса Практикум.Домашка. """
    try:
        response = requests.get(
            ENDPOINT,
            headers={'Authorization': f'OAuth {PRACTICUM_TOKEN}'},
            params={'from_date': timestamp}
        )
        response.raise_for_status()
        response = response.json()
        return response
    except requests.exceptions.ConnectionError:
        logging.error('Ошибка подключения к серверу.')
    except requests.exceptions.Timeout:
        logging.error('Превышено время ожидания.')
    except requests.exceptions.RequestException as error:
        logging.error(f"Ошибка при выполнении запроса: {error}.")
    except requests.exceptions.HTTPError as error:
        logging.error(f"HTTP-ошибка: {error}.")
    except Exception as error:
        logging.error(error)


def check_response(response):
    """Проверяет ответ API."""
    try:
        key_verification(response)
        homework_statuses(response)
    except MissingKeyException:
        logging.error('Отсутствуют ожидаемые ключи в ответе API.')
    except UnexpectedHomeworkStatusException:
        logging.error('Неожиданный статус домашней работы.')


def parse_status(homework):
    pass

    # return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    check_tokens()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)

        except Exception as error:
            sent_messages = []
            message = f'Сбой в работе программы: {error}'
            if message not in sent_messages:
                sent_messages.append(message)
                send_message(bot, message)


if __name__ == '__main__':
    main()
