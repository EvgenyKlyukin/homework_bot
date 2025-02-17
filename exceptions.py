from constants import ANSWER_KEYS, HOMEWORK_VERDICTS


class AbsenceVariableException(Exception):
    pass


class MissingKeyException(Exception):
    pass


class UnexpectedHomeworkStatusException(Exception):
    pass


def key_verification(response):
    for key in ANSWER_KEYS:
        if response.get(key) is None:
            raise MissingKeyException()


def homework_statuses(response):
    if response.get('status') not in HOMEWORK_VERDICTS.keys():
        raise UnexpectedHomeworkStatusException()
