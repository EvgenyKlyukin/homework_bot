class AbsenceVariableException(Exception):
    """Возникает, когда отсутствуют необходимые переменные окружения."""

    pass


class MissingKeyException(Exception):
    """Возникает, когда в ответе API отсутствуют ожидаемые ключи."""

    pass


class RequestNoContentException(Exception):
    """Возникает, когда запрос к API возвращает пустой ответ."""

    pass


class UnexpectedHomeworkStatusException(Exception):
    """Возникает, когда получен неожиданный статус домашней работы."""

    pass
