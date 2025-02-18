# Ожидаемые ключи в ответе API Практикум Домашка.
ANSWER_KEYS = ('homeworks', 'current_date')

# Определяет за какой период был присвоен статус домашней работы.
DIFFERENCE = 2592000  # По умолчанию принят месяц.

# Эндпоинт API Практикум Домашка.
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

# Переменные окружения необходимые для работы программы.
ENV_VARIABLES = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')

# Статусы домашней работы.
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Период опрашивания API сервиса Практикум Домашка.
RETRY_PERIOD = 600
