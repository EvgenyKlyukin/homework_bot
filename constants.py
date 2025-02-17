# Период опрашивания API сервиса Практикум Домашка.
RETRY_PERIOD = 600

# Эндпоинт API Практикум Домашка.
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

# Статусы домашней работы.
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Ожидаемые ключи в ответе API Практикум Домашка.
ANSWER_KEYS = ('homeworks', 'current_date')

# Переменные окружения необходимые для работы программы.
ENV_VARIABLES = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
