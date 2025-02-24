import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiException

from exceptions import (AbsenceVariableException, MissingKeyException,
                        RequestNoContentException,
                        UnexpectedHomeworkStatusException)

# Загружаем переменные окружения из .env файла.
load_dotenv()

# Константы.
ANSWER_KEYS = ('homeworks', 'current_date')
DIFFERENCE = 2592000  # 30 дней.
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
ENV_VARIABLES = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
HOMEWORK_VERDICTS = {  # Статусы домашней работы.
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
RETRY_PERIOD = 600  # Период опроса API в секундах.

# Получение токенов из переменных окружения
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Заголовки для запросов к API.
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

# Настройка логирования.
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    missing_vars = [var for var in ENV_VARIABLES if globals()[var] is None]
    if missing_vars:
        logger.critical(f'Отсутствуют переменные окружения: {missing_vars}')
        raise AbsenceVariableException()


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение отправлено: {message}.')
    except ApiException as error:
        logger.error(f'Сообщение не отправлено, из-за ошибки {error}.')


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
        if not isinstance(response, dict):
            raise TypeError('Ответ должен быть словарем.')
        for key in ANSWER_KEYS:
            if response.get(key) is None:
                raise MissingKeyException()
        if not isinstance(response['homeworks'], list):
            raise TypeError(
                'Данные под ключом "homeworks" должны быть списком.'
            )
    except MissingKeyException as error:
        logging.error(f'Отсутствуют ожидаемые ключи в ответе API: {error}.')
        raise
    except TypeError as error:
        logging.error(f'Структура данных не соответствует ожиданиям: {error}.')
        raise


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""
    if 'homework_name' not in homework:
        raise KeyError('Ключ "homework_name" отсутствует в ответе API.')

    status = homework.get('status')

    if status is None:
        raise KeyError('Ключ "status" отсутствует в ответе API.')

    if 'homework_name' not in homework or 'status' not in homework:
        raise KeyError('Отсутствуют ключи "homework_name" или "status".')

    if status not in HOMEWORK_VERDICTS:
        raise UnexpectedHomeworkStatusException(
            'Неизвестный статус домашней работы.'
        )

    homework_name = homework['homework_name']
    return (
        f'Изменился статус проверки работы "{homework_name}". '
        f'{HOMEWORK_VERDICTS[status]}'
    )


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - DIFFERENCE
    last_message = None

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response['homeworks']
            timestamp = response['current_date']

            if homeworks:
                message = parse_status(homeworks[0])
                if message != last_message:
                    send_message(bot, message)
                    last_message = message
            else:
                logger.debug('Нет новых статусов домашних работ.')

        except Exception as error:
            logger.error(f'Ошибка в работе программы: {error}')
            send_message(bot, f'Сбой в работе программы: {error}')

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
