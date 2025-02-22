import logging
import os
import requests
import time
from http import HTTPStatus

from dotenv import load_dotenv
from telebot import TeleBot

from constants import (
    ANSWER_KEYS, DIFFERENCE, ENDPOINT, ENV_VARIABLES,
    HOMEWORK_VERDICTS, RETRY_PERIOD
)
from exceptions import (
    AbsenceVariableException, MissingKeyException,
    RequestNoContentException, UnexpectedHomeworkStatusException
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

homework_status = None


def check_tokens():
    """Проверяет доступность переменных окружения."""
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
    """Делает запрос к API-сервиса Практикум.Домашка."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        response.raise_for_status()

        if response.status_code == HTTPStatus.NO_CONTENT:
            raise RequestNoContentException()
        response = response.json()
        return response
    except requests.exceptions.ConnectionError:
        logging.error('Ошибка подключения к серверу.')
    except requests.exceptions.Timeout:
        logging.error('Превышено время ожидания.')
    except requests.exceptions.HTTPError as error:
        logging.error(f'HTTP-ошибка: {error}.')
        raise
    except RequestNoContentException:
        logging.error('Запрос выполнен, но нет содержимого для возврата.')
        raise
    except requests.RequestException as error:
        logging.error(f'Ошибка при выполнении запроса: {error}.')
    except Exception as error:
        logging.error(f'Неизвестная ошибка: {error}.')
        raise


def check_response(response):
    """Проверяет ответ API."""
    try:
        for key in ANSWER_KEYS:
            if response.get(key) is None:
                raise MissingKeyException()
    except MissingKeyException as error:
        logging.error(f'Отсутствуют ожидаемые ключи в ответе API: {error}.')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""
    global homework_status
    try:
        current_status = homework.get('status')
        if current_status is None:
            raise KeyError('status')

        if current_status not in HOMEWORK_VERDICTS.keys():
            raise UnexpectedHomeworkStatusException()

        if current_status != homework_status:
            homework_status = current_status
            homework_name = homework.get('homework_name')
            return (
                f'Изменился статус проверки работы "{homework_name}".'
                f'{HOMEWORK_VERDICTS[current_status]}'
            )
        logging.debug('Отсутствие в ответе новых статусов.')
    except UnexpectedHomeworkStatusException:
        logging.error('Неожиданный статус домашней работы.')
        raise
    except KeyError as e:
        logging.error(f'Отсутствует ключ: {e}')
        raise


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    check_tokens()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - DIFFERENCE
    sent_messages = []

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            message = parse_status(response[ANSWER_KEYS[0]][0])
            if message:
                send_message(bot, message)
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message not in sent_messages:
                sent_messages.append(message)
                send_message(bot, message)


if __name__ == '__main__':
    main()
