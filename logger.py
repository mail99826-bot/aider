"""
logger.py - логирование действий бота
"""

import logging
import logging.handlers
import os
from datetime import datetime

from config import *

# Константы для форматирования логов
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"  # Уровень логирования по умолчанию


class TradeLogger:
    def __init__(self):
        """Инициализация системы логирования"""
        # Создаем директорию для логов
        if not os.path.exists("logs"):
            os.makedirs("logs")

        print("📁 Настройка системы логирования...")
        print("   ✅ Все ошибки → logs/errors.log")
        print("   ✅ Все ордеры → logs/orders.log")
        print("   ✅ Все сделки → logs/trades.log")
        print("   ✅ Все события бота → logs/bot.log")
        print("   ✅ Статистика → logs/stats.log")

        # Настройка разных логгеров
        self.trade_logger = self.setup_logger(
            "trade", "logs/trades.log", level=logging.INFO
        )
        self.error_logger = self.setup_logger(
            "error", "logs/errors.log", level=logging.ERROR
        )
        self.order_logger = self.setup_logger(
            "order", "logs/orders.log", level=logging.INFO
        )
        self.bot_logger = self.setup_logger("bot", "logs/bot.log", level=logging.INFO)
        self.stats_logger = self.setup_logger(
            "stats", "logs/stats.log", level=logging.INFO
        )

        # Для обратной совместимости оставляем основной логгер
        self.log_file = "logs/general.log"

        # Настройка формата логов
        self.log_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Создаем логгер
        self.logger = logging.getLogger("scalping_bot")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))

        # Удаляем существующие обработчики
        self.logger.handlers = []

        # Обработчик для файла
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setFormatter(self.log_format)

        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.log_format)

        # Добавляем обработчики
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        print("✅ Система логирования полностью настроена")
        self.log_info("Система логирования инициализирована")

    def setup_logger(self, name, log_file, level=logging.INFO):
        """Создаем логгер для разных типов событий"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Один логгер = один файл
        handler = logging.FileHandler(log_file)
        handler.setLevel(level)

        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def log_trade(self, action, symbol, side, price, amount, fee=0, pnl=0, order_id=""):
        """
        Логирование сделки
        """
        timestamp = datetime.now().strftime(LOG_DATE_FORMAT)

        if action == "OPEN":
            message = f"Открыта позиция {side.upper()} | {symbol} | Цена: {price:.2f} | Объем: {amount} | ID: {order_id}"
        elif action == "CLOSE":
            pnl_prefix = "+" if pnl > 0 else ""
            message = f"Закрыта позиция {side.upper()} | {symbol} | Цена: {price:.2f} | Объем: {amount} | P&L: {pnl_prefix}{pnl:.2f} | ID: {order_id}"
        elif action == "CANCEL":
            message = f"Отменен ордер | {symbol} | ID: {order_id}"
        else:
            message = f"{action} | {symbol} | Цена: {price:.2f} | Объем: {amount}"

        # Логируем ТОЛЬКО в logs/trades.log, НЕ в общий лог
        full_message = f"{timestamp} | TRADE | {message}"
        print(full_message)
        self.trade_logger.info(message)
        # Сделки теперь ТОЛЬКО в logs/trades.log

    def log_order(
        self, order_type, symbol, side, price, amount, status, order_id="", reason=""
    ):
        """
        Логирование ордера
        """
        timestamp = datetime.now().strftime(LOG_DATE_FORMAT)
        message = f"{order_type.upper()} | {symbol} | {side.upper()} | Цена: {price:.2f} | Объем: {amount} | Статус: {status}"
        if order_id:
            message += f" | ID: {order_id}"
        if reason:
            message += f" | Причина: {reason}"

        self.order_logger.info(message)
        self.logger.info(message)

    def log_signal(self, signal, price, fast_ma, slow_ma, rsi):
        """
        Логирование торгового сигнала
        """
        message = f"Сигнал: {signal} | Цена: {price:.2f} | MA({FAST_MA_PERIOD}): {fast_ma:.2f} | MA({SLOW_MA_PERIOD}): {slow_ma:.2f} | RSI: {rsi:.2f}"
        self.logger.info(message)

    def log_error(self, error_message, module=""):
        """
        Логирование ошибки
        """
        if module:
            message = f"Ошибка в {module}: {error_message}"
        else:
            message = f"Ошибка: {error_message}"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{timestamp} | ERROR [GENERAL] | {message}"
        print(full_message)
        self.error_logger.error(f"[GENERAL] {message}")
        self.logger.error(message)

    def log_info(self, info_message):
        """
        Логирование информационного сообщения
        """
        self.bot_logger.info(info_message)
        self.logger.info(info_message)

    def log_stats(self, stats_data):
        """
        Логирование статистики
        Пример stats_data: {
            'balance': 5000.50,
            'trades_count': 15,
            'winning_trades': 10,
            'losing_trades': 5,
            'total_pnl': 125.75,
            'win_rate': 66.67
        }
        """
        timestamp = datetime.now().strftime(LOG_DATE_FORMAT)

        # Форматируем статистику
        stats_str = f"Баланс: ${stats_data.get('balance', 0):.2f} | "
        stats_str += f"Сделки: {stats_data.get('trades_count', 0)} | "
        stats_str += f"Выигрыши: {stats_data.get('winning_trades', 0)} | "
        stats_str += f"Проигрыши: {stats_data.get('losing_trades', 0)} | "
        stats_str += f"Общий P&L: ${stats_data.get('total_pnl', 0):.2f} | "
        stats_str += f"Винрейт: {stats_data.get('win_rate', 0):.2f}%"

        message = f"{timestamp} | СТАТИСТИКА | {stats_str}"

        self.stats_logger.info(message)
        self.logger.info(message)

    def log_warning(self, warning_message):
        """
        Логирование предупреждения
        """
        self.logger.warning(warning_message)

    def get_recent_trades(self, limit=10):
        """
        Получение последних сделок из лог-файла
        """
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[-limit:]
            return lines
        except FileNotFoundError:
            return ["Лог.файл еще не создан"]
        except Exception as e:
            return [f"Ошибка чтения лога: {e}"]

    def clear_logs(self, keep_last_days=7):
        """
        Очистка старых логов (оставляет записи за последние N дней)
        """
        try:
            # В реальном боте здесь была бы логика ротации логов
            self.logger.info(
                f"Запрошена очистка логов (оставить {keep_last_days} дней)"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка очистки логов: {e}")
            return False
