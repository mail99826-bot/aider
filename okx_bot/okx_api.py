import ccxt
from ccxt import NetworkError, ExchangeError
from config import OKX_CONFIG
from okx_bot.logger import logger
from okx_bot.telegram_notifier import TelegramNotifier

class OKXAPI:
    def __init__(self):
        self.exchange = ccxt.okx(OKX_CONFIG)
        self.notifier = TelegramNotifier()
        self._validate_connection()
        self._check_demo_mode()

    def _check_demo_mode(self):
        """Проверка работы на демо-счете"""
        if self.exchange.urls['test']:
            logger.log('system', 'Running in DEMO mode')
            self.notifier.send_message("🟡 Бот работает на ДЕМО-счете")

    def _validate_connection(self):
        """Проверка подключения к бирже"""
        try:
            self.exchange.load_markets()
            logger.log('system', 'Successfully connected to OKX')
            self.notifier.send_message("✅ Бот успешно подключился к OKX")
        except Exception as e:
            logger.log('error', f"Connection error: {str(e)}")
            self.notifier.notify_error(e)
            raise

    def get_balance(self, currency: str = 'USDT') -> float:
        """Получение баланса по валюте"""
        try:
            balance = self.exchange.fetch_balance()
            free_balance = balance['total'].get(currency, 0)
            logger.log('trading', f"Balance check: {currency} = {free_balance}")
            return float(free_balance)
        except (NetworkError, ExchangeError) as e:
            logger.log('error', f"Balance check failed: {str(e)}")
            self.notifier.notify_error(e)
            raise

    def get_ticker(self, symbol: str) -> dict:
        """Получение текущих цен"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.log('trading', f"Ticker data for {symbol}: {ticker}")
            return ticker
        except (NetworkError, ExchangeError) as e:
            logger.log('error', f"Failed to get ticker: {str(e)}")
            self.notifier.notify_error(e)
            raise

    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> dict:
        """Размещение ордера"""
        try:
            order_type = 'limit' if price else 'market'
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            logger.log('trading', f"Order placed: {order}")
            self.notifier.notify_trading_event('ORDER_PLACED', order)
            return order
        except (NetworkError, ExchangeError) as e:
            logger.log('error', f"Order placement failed: {str(e)}")
            self.notifier.notify_error(e)
            raise

    def cancel_order(self, order_id: str, symbol: str) -> dict:
        """Отмена ордера"""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.log('trading', f"Order canceled: {result}")
            self.notifier.notify_trading_event('ORDER_CANCELED', result)
            return result
        except (NetworkError, ExchangeError) as e:
            logger.log('error', f"Order cancellation failed: {str(e)}")
            self.notifier.notify_error(e)
            raise
