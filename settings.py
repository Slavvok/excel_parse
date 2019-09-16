import logging
import json

TIMEOUT = 1
THREADS_AMOUNT = 5

FILE_LOGGING = 'logs/logs.log'
FILE_ERRORS_DUMP = 'logs/exceptions.json'
DEFAULT_EXCEL_FILE = 'raw_data.xlsx'

SQLITE_DB = 'sqlite:///db.sqlite3'

dictConfig = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "error": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": FILE_LOGGING,
                "level": "INFO",
            },
            "streamHandler": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            },
            "exceptionHandler": {
                "class": "logging.FileHandler",
                "formatter": "error",
                "level": "ERROR",
                "filename": FILE_ERRORS_DUMP
            }
        },
        "loggers": {
            "scriptLogger": {
                "handlers": ["fileHandler", "streamHandler"],
                "level": "INFO"
            },
            "errorLogger": {
                "handlers": ["exceptionHandler"],
                "level": "ERROR"
            }
        },
}


class ExceptionLogging:
    def __init__(self, timestamp, exception, url, stack_info):
        self.timestamp = timestamp
        self.exception = exception
        self.url = url
        self.stack_info = stack_info

    def __str__(self):
        error_log = {"timestamp": str(self.timestamp),
                     "url": self.url,
                     "error": {
                        "exception_type": type(self.exception).__name__,
                        "exception_value": self.exception.errno,
                        "stack_info": self.stack_info,
                     }}
        return json.dumps(error_log, indent=4)
