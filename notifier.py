"""notifier.py - отправка уведомлений в Telegram"""

import time

import requests

from config import *
from logger import TradeLogger


class TelegramNotifier:
    def __init__(self, logger=None):
        """Инициализация Telegram бота"""
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        # Инициализация логгера
        self.logger = logger or TradeLogger()

        if self.bot_token and self.chat_id:
            self.logger.log_info("📱 Telegram бот инициализирован")
        else:
            self.logger.log_warning("Telegram бот не настроен (проверьте .env файл)")

    def send_message(self, text, max_retries=3, level="info"):
        """
        Отправка текстового сообщения в Telegram с повторными попытками
        Args:
            text: Текст сообщения
            max_retries: Максимальное количество попыток
            level: Уровень важности (info, warning, error)
        """
        if not self.bot_token or not self.chat_id:
            self.logger.log_info("Telegram не настроен, пропускаем уведомление")
            return False

        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/sendMessage"
                payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}

                # Увеличиваем таймаут до 30 секунд
                response = requests.post(url, data=payload, timeout=30)
                response.raise_for_status()

                self.logger.log_info(f"Уведомление отправлено в Telegram (попытка {attempt + 1})")
                return True

            except requests.exceptions.RequestException as e:
                error_msg = f"Ошибка отправки в Telegram (попытка {attempt + 1}/{max_retries}): {e}"
                self.logger.log_error(error_msg)
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    self.logger.log_warning(f"Не удалось отправить сообщение после {max_retries} попыток")
                    return False

    def send_order_notification(
        self, order_type, symbol, side, amount, price, order_id
    ):
        """
        Отправка уведомления о сделке
        """
        emoji = "🟢" if side == "buy" else "🔴"

        message = (
            f"<b>{emoji} {order_type.upper()} ОРДЕР {side.upper()}</b>\n"
            f"Пара: {symbol}\n"
            f"Объем: {amount}\n"
            f"Цена: {price:.2f}\n"
            f"ID ордера: {order_id}\n"
            f"Режим: {MODE.upper()}"
        )

        return self.send_message(message)

    def send_trade_result(
        self, symbol, side, entry_price, exit_price, amount, profit_loss
    ):
        """
        Отправка результата сделки
        """
        profit_percent = ((exit_price - entry_price) / entry_price) * 100
        if side == "sell":
            profit_percent = -profit_percent

        emoji = "💰" if profit_loss > 0 else "💸"
        result_text = "ПРИБЫЛЬ" if profit_loss > 0 else "УБЫТОК"

        message = (
            f"<b>{emoji} СДЕЛКА ЗАКРЫТА: {result_text}</b>\n"
            f"Пара: {symbol}\n"
            f"Сторона: {side.upper()}\n"
            f"Вход: {entry_price:.2f}\n"
            f"Выход: {exit_price:.2f}\n"
            f"Объем: {amount}\n"
            f"P&L: {profit_loss:.2f} USDT\n"
            f"Процент: {profit_percent:.2f}%"
        )

        return self.send_message(message)

    def send_error_notification(self, error_message):
        """
        Отправка уведомления об ошибке
        """
        message = (
            f"<b>🚨 ОШИБКА БОТА</b>\n" f"{error_message}\n" f"Режим: {MODE.upper()}"
        )

        return self.send_message(message)

    def send_stop_loss_notification(
        self, symbol, side, entry_price, stop_price, amount
    ):
        """
        Отправка уведомления о срабатывании стоп,лосса
        """
        message = (
            f"<b>🛑 СТОП-ЛОСС СРАБОТАЛ</b>\n"
            f"Пара: {symbol}\n"
            f"Сторона: {side.upper()}\n"
            f"Вход: {entry_price:.2f}\n"
            f"Стоп: {stop_price:.2f}\n"
            f"Объем: {amount}\n"
            f"Убыток: {((stop_price - entry_price) / entry_price * 100):.2f}%"
        )

        return self.send_message(message)

    def send_bot_status(self, status, balance, open_positions):
        """
        Отправка статуса бота
        """
        message = (
            f"<b>🤖 СТАТУС БОТА</b>\n"
            f"Статус: {status}\n"
            f"Баланс: {balance:.2f} USDT\n"
            f"Открытые позиции: {len(open_positions)}\n"
            f"Режим: {MODE.upper()}"
        )

        return self.send_message(message)
