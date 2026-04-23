import requests
from okx_bot.config import TELEGRAM_CONFIG
from okx_bot.logger import logger

class TelegramNotifier:
    def __init__(self):
        self.token = TELEGRAM_CONFIG['token']
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text: str):
        """Отправка сообщения в Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            logger.log('system', f"Telegram notification sent: {text[:100]}...")
        except Exception as e:
            logger.log('error', f"Failed to send Telegram notification: {str(e)}")

    def notify_trading_event(self, event: str, details: dict):
        """Отправка уведомления о торговом событии"""
        message = (
            f"<b>Торговое событие</b>\n"
            f"Тип: {event}\n"
            f"Детали: {details}"
        )
        self.send_message(message)

    def notify_error(self, error: Exception):
        """Отправка уведомления об ошибке"""
        message = (
            f"<b>🚨 Ошибка в боте</b>\n"
            f"Тип: {type(error).__name__}\n"
            f"Сообщение: {str(error)}"
        )
        self.send_message(message)
