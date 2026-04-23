"""exchange_client.py - взаимодействие с биржей OKX через API"""

import ccxt

from config import *
from logger import TradeLogger


class ExchangeClient:
    def __init__(self, logger=None):
        """Инициализация клиента биржи OKX"""
        # Настройки подключения
        self.logger = TradeLogger()
        self.logger.log_info(
            f"🔧 Используется {'ТЕСТОВЫЙ' if OKX_TESTNET else 'РЕАЛЬНЫЙ'} режим OKX"
        )

        # Инициализация логгера
        if logger:
            self.logger = logger
        else:
            self.logger = TradeLogger()

        # Создаем подключение
        self.exchange = ccxt.okx(
            {
                "apiKey": OKX_API_KEY,
                "secret": OKX_API_SECRET,
                "password": OKX_API_PASSPHRASE,
                "timeout": OKX_TIMEOUT,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "swap",
                },
            }
        )

        # ВКЛЮЧАЕМ ТЕСТОВЫЙ РЕЖИМ если нужно
        if OKX_TESTNET or OKX_SANDBOX:
            self.exchange.set_sandbox_mode(True)
            self.logger.log_info("✅ Включен тестовый режим (sandbox)")

        # Установка рыночного типа (фьючерсы USDT-M)
        self.market_type = "swap"
        self.symbol = TRADING_PAIR

        self.logger.log_info(f"✅ Подключено к OKX ({MODE.upper()} режим)")
        self.logger.log_info(f"📈 Торговая пара: {self.symbol}")

    def get_current_price(self):
        """
        Получение текущей цены
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker["last"]
        except Exception as e:
            error_msg = f"Ошибка получения цены: {e}"
            self.logger.log_error(error_msg, "get_current_price")
            return None

    def get_balance(self, currency="USDT"):
        """
        Получение баланса
        """
        try:
            balance = self.exchange.fetch_balance({"type": self.market_type})
            return balance["total"].get(currency, 0)
        except Exception as e:
            error_msg = f"Ошибка получения баланса: {e}"
            self.logger.log_error(error_msg, "get_balance")
            return 0

    def get_candles(self, limit=100):
        """
        Получение истории свечей
        """
        try:
            candles = self.exchange.fetch_ohlcv(
                self.symbol, timeframe=CANDLE_INTERVAL, limit=limit
            )
            return candles
        except Exception as e:
            error_msg = f"Ошибка получения свечей: {e}"
            self.logger.log_error(error_msg, "get_candles")
            return []

    def set_leverage(self, leverage=LEVERAGE):
        """
        Установка кредитного плеча
        """
        try:
            self.exchange.set_leverage(leverage, self.symbol)
            self.logger.log_info(f"✅ Установлено плечо: {leverage}x")
            return True
        except Exception as e:
            error_msg = f"Ошибка установки плеча: {e}"
            self.logger.log_error(error_msg, "set_leverage")
            return False

    def place_market_order(self, side, amount, reduce_only=False):
        """
        Размещение рыночного ордера
        """
        try:
            order = self.exchange.create_market_order(
                symbol=self.symbol,
                side=side,
                amount=amount,
                params={"reduceOnly": reduce_only},
            )
            return order
        except Exception as e:
            error_msg = f"Ошибка размещения рыночного ордера: {e}"
            self.logger.log_error(error_msg, "place_market_order")
            return None

    def place_limit_order(self, side, amount, price, reduce_only=False):
        """
        Размещение лимитного ордера
        """
        try:
            order = self.exchange.create_limit_order(
                symbol=self.symbol,
                side=side,
                amount=amount,
                price=price,
                params={"reduceOnly": reduce_only},
            )
            return order
        except Exception as e:
            error_msg = f"Ошибка размещения лимитного ордера: {e}"
            self.logger.log_error(error_msg, "place_limit_order")
            return None

    def cancel_order(self, order_id):
        """
        Отмена ордера
        """
        try:
            result = self.exchange.cancel_order(order_id, self.symbol)
            return result
        except Exception as e:
            error_msg = f"Ошибка отмены ордера: {e}"
            self.logger.log_error(error_msg, "cancel_order")
            return None

    def get_open_positions(self):
        """
        Получение открытых позиций
        """
        try:
            positions = self.exchange.fetch_positions([self.symbol])
            return positions
        except Exception as e:
            error_msg = f"Ошибка получения позиций: {e}"
            self.logger.log_error(error_msg, "get_open_positions")
            return []

    def close_all_positions(self):
        """
        Закрытие всех позиций
        """
        try:
            positions = self.get_open_positions()
            for pos in positions:
                if float(pos["contracts"]) > 0:
                    side = "sell" if pos["side"] == "long" else "buy"
                    amount = abs(float(pos["contracts"]))
                    self.place_market_order(side, amount, reduce_only=True)
                    self.logger.log_info(
                        f"✅ Закрыта позиция: {pos['side']} {amount} контрактов"
                    )
            return True
        except Exception as e:
            error_msg = f"Ошибка закрытия позиций: {e}"
            self.logger.log_error(error_msg, "close_all_positions")
            return False
            error_msg = f"Ошибка закрытия позиций: {e}"

            self.logger.log_error(error_msg, "close_all_positions")
            return False
