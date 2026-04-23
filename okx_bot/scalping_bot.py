import time
from okx_bot.okx_api import OKXAPI
from okx_bot.logger import logger
from okx_bot.telegram_notifier import TelegramNotifier
from config import BOT_CONFIG

class ScalpingBot:
    def __init__(self):
        self.api = OKXAPI()
        self.notifier = TelegramNotifier()
        self.symbol = BOT_CONFIG['symbol']
        self.timeframe = BOT_CONFIG['timeframe']
        self.running = False

    def start(self):
        """Запуск бота"""
        self.running = True
        logger.log('bot', 'Scalping bot started')
        self.notifier.send_message("🚀 Скальпинг бот запущен")

        try:
            while self.running:
                self._main_loop()
                time.sleep(60)  # Интервал между итерациями
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.log('error', f"Bot crashed: {str(e)}")
            self.notifier.notify_error(e)
            raise

    def stop(self):
        """Остановка бота"""
        self.running = False
        logger.log('bot', 'Scalping bot stopped')
        self.notifier.send_message("🛑 Скальпинг бот остановлен")

    def _main_loop(self):
        """Основной цикл работы бота"""
        try:
            # Получаем текущие данные
            ticker = self.api.get_ticker(self.symbol)
            
            # Здесь будет логика торговой стратегии
            # Пример: если цена упала на 1% от последнего значения
            if ticker['last'] < ticker['open'] * 0.99:
                self._execute_buy()
            elif ticker['last'] > ticker['open'] * 1.01:
                self._execute_sell()

        except Exception as e:
            logger.log('error', f"Main loop error: {str(e)}")
            self.notifier.notify_error(e)
            raise

    def _execute_buy(self):
        """Логика покупки"""
        balance = self.api.get_balance('USDT')
        if balance > 10:  # Минимальная сумма для торговли
            self.api.place_order(
                symbol=self.symbol,
                side='buy',
                amount=balance * 0.99 / self.api.get_ticker(self.symbol)['last'],
                price=None  # Market order
            )

    def _execute_sell(self):
        """Логика продажи"""
        balance = self.api.get_balance('BTC')
        if balance > 0.001:  # Минимальное количество BTC для продажи
            self.api.place_order(
                symbol=self.symbol,
                side='sell',
                amount=balance,
                price=None  # Market order
            )

if __name__ == "__main__":
    bot = ScalpingBot()
    bot.start()
