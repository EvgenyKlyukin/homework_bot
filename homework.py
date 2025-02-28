import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiException

from exceptions import (AbsenceVariableException,
                        RequestException,
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
    env_var = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    missing_vars = []
    for env_name, env_token in env_var.items():
        if env_token is None:
            missing_vars.append(env_name)
    if missing_vars:
        logger.critical(f'Отсутствуют переменные окружения: {missing_vars}')
        raise AbsenceVariableException()


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение отправлено: {message}.')
        return True
    except ApiException as error:
        logger.error(f'Сообщение не отправлено, из-за ошибки {error}.')
    except requests.RequestException:
        logger.error(
            'При обработке запроса произошло неоднозначное исключение.'
        )


def get_api_answer(timestamp):
    """Делает запрос к API-сервиса Практикум.Домашка."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise RequestException(
            f'Ошибка при выполнении запроса: {error}.'
            f'ENDPOINT: {ENDPOINT} headers: {HEADERS} params: {timestamp}'
        )
    if response.status_code == HTTPStatus.NO_CONTENT:
        raise RequestNoContentException(
            'Запрос выполнен, но нет содержимого для возврата.'
        )
    response = response.json()
    return response


def check_response(response):
    """Проверяет ответ API."""
    if not isinstance(response, dict):
        raise TypeError(f'Ответ должен быть словарем: {type(response)}')
    for key in ANSWER_KEYS:
        if response.get(key) is None:
            raise KeyError(f'Указанный ключ отсутствует: {key}')
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            'Данные под ключом "homeworks" должны быть '
            f'списком: {response["homeworks"]}'
        )


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""
    if 'homework_name' not in homework:
        raise KeyError('Ключ "homework_name" отсутствует в ответе API.')

    status = homework.get('status')

    if status is None:
        raise KeyError('Ключ "status" отсутствует в ответе API.')

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
            timestamp = int(time.time())

            if homeworks:
                message = parse_status(homeworks[0])
                if message != last_message and send_message(bot, message):
                    last_message = message
            else:
                logger.debug('Нет новых статусов домашних работ.')

        except Exception as error:
            error_message = f'Ошибка в работе программы: {error}'
            logger.error(error_message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
