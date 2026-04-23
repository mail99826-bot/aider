"""
config.py - загрузка настроек и общие параметры бота
"""

import os

from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# API ключи OKX
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_API_PASSPHRASE = os.getenv("OKX_API_PASSPHRASE")

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Настройки бота
TRADING_PAIR = "BTC/USDT:USDT"
INITIAL_BALANCE = 5000  # USDT

# Торговые параметры
LEVERAGE = 1  # Изменил с 5 на 1 (без плеча)
POSITION_SIZE = 0.05  # Размер позиции в контрактах
LIVE_MODE = True  # False - тестовый режим, True - реальная торговля

# Параметры комиссий
MAKER_FEE = 0.0002  # 0.02%
TAKER_FEE = 0.0005  # 0.05%

# Временные интервалы
CANDLE_INTERVAL = "5m"  # 5-TINUTIONные свечи для скальпинга
CHECK_INTERVAL = 60  # Интервал проверки в секундах (1 раз в минуту)

# Параметры стратегии
FAST_MA_PERIOD = 10  # Быстрая скользящая средняя (50 минут)
SLOW_MA_PERIOD = 30  # Медленная скользящая средняя (150 минут)
RSI_PERIOD = 14  # Период RSI

# Настройки рисков
MAX_POSITION_SIZE = 0.05  # Максимальный размер позиции в BTC
STOP_LOSS_PERCENT = 0.5  # Стоп-лосс 0.5% для скальпинга
TAKE_PROFIT_PERCENT = 1.0  # Тейк-xрофит 1.0% для скальпинга
RISK_PER_TRADE = 0.01  # Риск 1% на сделку

# Настройки логирования
LOG_FILE = "logs/general.log"  # Основной файл логов
LOG_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s | %(params)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "verbose": {
            "format": "%(asctime)s | %(levelname)-8s | %(module)-15s | %(funcName)-20s:%(lineno)-4d | %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)s %(message)s"
        }
    },
    
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },
        "file_general": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/general.log",
            "maxBytes": 1024*1024*5,  # 5MB
            "backupCount": 3,
            "formatter": "standard",
            "level": "INFO"
        },
        "file_errors": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log", 
            "maxBytes": 1024*1024*5,
            "backupCount": 3,
            "formatter": "verbose",
            "level": "WARNING"
        },
        "file_trades": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/trades.log",
            "maxBytes": 1024*1024*5,
            "backupCount": 3,
            "formatter": "standard",
            "level": "INFO"
        },
        "file_json": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/structured.log",
            "maxBytes": 1024*1024*5,
            "backupCount": 3,
            "formatter": "json",
            "level": "INFO"
        }
    },
    
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": True
        },
        "exchange": {
            "handlers": ["file_general"],
            "level": "DEBUG",
            "propagate": False
        },
        "trades": {
            "handlers": ["file_trades"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# Настройки подключения
OKX_TESTNET = os.getenv("OKX_TESTNET", "true").lower() == "true"
OKX_SANDBOX = os.getenv("OKX_SANDBOX", "true").lower() == "true"
OKX_TIMEOUT = int(os.getenv("OKX_TIMEOUT", "30000"))

# Режимы
MODE = "test"  # "test" или "live"
USE_MARGIN = False  # Использовать маржинальную торговлю

# Определяем режим работы
if OKX_TESTNET or OKX_SANDBOX or not LIVE_MODE:
    print("⚠️  РАБОТАЕМ В ТЕСТОВОМ РЕЖИМЕ")
    MODE = "test"
else:
    print("🚨 РЕАЛЬНЫЙ РЕЖИМ ТОРГОВЛИ")
    MODE = "live"
