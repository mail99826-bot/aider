import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
from ..config import LOG_CONFIG

class BotLogger:
    def __init__(self):
        self._setup_loggers()

    def _setup_loggers(self):
        """Настройка системы логирования"""
        self.loggers = {}
        log_level = getattr(logging, LOG_CONFIG['log_level'])

        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Инициализация логгеров
        log_types = {
            'trading': LOG_CONFIG['trading_log'],
            'error': LOG_CONFIG['error_log'],
            'bot': LOG_CONFIG['bot_log'],
            'system': LOG_CONFIG['system_log']
        }

        for log_name, log_file in log_types.items():
            logger = logging.getLogger(log_name)
            logger.setLevel(log_level)

            # Ротация логов каждый день
            handler = TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=7
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            self.loggers[log_name] = logger

    def log(self, log_type: str, message: str, level: str = 'info'):
        """Основной метод логирования"""
        logger = self.loggers.get(log_type)
        if not logger:
            raise ValueError(f"Unknown log type: {log_type}")

        log_method = getattr(logger, level.lower(), None)
        if log_method:
            log_method(message)

# Глобальный экземпляр логгера
logger = BotLogger()
