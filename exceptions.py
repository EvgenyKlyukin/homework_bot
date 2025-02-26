class AbsenceVariableException(Exception):
    """Отсутствуют необходимые переменные окружения."""


class RequestException(Exception):
    """Ошибка при выполнении запроса."""


class RequestNoContentException(Exception):
    """Запрос к API возвращает пустой ответ."""


class UnexpectedHomeworkStatusException(Exception):
    """Получен неожиданный статус домашней работы."""
