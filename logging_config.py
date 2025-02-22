import logging
import logging.config
import sys


def setup_logging():
    """Настройка логирования с использованием StreamHandler."""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': (
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            },
        },
        'handlers': {
            'file_handler': {
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'formatter': 'simple',
                'level': logging.ERROR,
            },
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'simple',
                'level': logging.DEBUG,
            },
        },
        'loggers': {
            'my_logger': {
                'handlers': ['file_handler', 'stream_handler'],
                'level': logging.DEBUG,
                'propagate': False,
            },
        }
    }

    logging.config.dictConfig(logging_config)
