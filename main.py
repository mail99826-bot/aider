"""main.py - главный цикл бота"""

import signal
import sys
import time
from datetime import datetime

# Импорт модулей бота
from config import *
from exchange_client import ExchangeClient
from logger import TradeLogger
from notifier import TelegramNotifier
from risk_manager import RiskManager
from strategy import TradingStrategy


class ScalpingBot:
    def __init__(self):
        """Инициализация бота"""
        print("🚀 ИНИЦИАЛИЗАЦИЯ SCALPING БОТА")
        print("=" * 50)

        # Инициализация компонентов
        self.logger = TradeLogger()  # Сначала создаем логгер
        self.exchange = ExchangeClient(self.logger)  # Передаем логгер в ExchangeClient
        self.strategy = TradingStrategy(self.logger)  # Передаем логгер в стратегию
        self.risk_manager = RiskManager(
            self.logger
        )  # Передаем логгер в менеджер рисков
        self.notifier = TelegramNotifier(self.logger)  # Передаем логгер в нотификатор

        # Переменные состояния
        self.is_running = True
        self.current_position = None
        self.initial_balance = None
        self.trade_count = 0

        # Обработка сигнала Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("=" * 50)
        print("✅ Бот инициализирован и готов к работе!\n")

    def signal_handler(self, sig, frame):
        """Обработка сигнала завершения"""
        print("\n🛑 Получен сигнал завершения...")
        self.stop()

    def stop(self):
        """Корректное завершение работы бота"""
        print("\n🛑 Завершение работы бота...")
        self.is_running = False

        # Закрытие позиций
        self.close_all_positions()

        # Отправка финального статуса
        balance = self.exchange.get_balance()
        self.notifier.send_bot_status("ОСТАНОВЛЕН", balance, [])
        self.logger.log_info("Бот остановлен")

        print("✅ Бот остановлен")
        sys.exit(0)

    def close_all_positions(self):
        """Закрытие всех открытых позиций"""
        print("🔄 Закрытие всех позиций...")
        try:
            self.exchange.close_all_positions()
            self.current_position = None
            print("✅ Все позиции закрыты")
        except Exception as e:
            print(f"❌ Ошибка при закрытии позиций: {e}")

    def initialize_account(self):
        """Инициализация аккаунта"""
        try:
            # Установка плеча
            self.exchange.set_leverage()

            # Получение начального баланса
            self.initial_balance = self.exchange.get_balance()
            print(f"💰 Начальный баланс: {self.initial_balance:.2f} USDT")

            # Отправка статуса
            self.notifier.send_bot_status("ЗАПУЩЕН", self.initial_balance, [])
            self.logger.log_info(
                f"Бот запущен. Баланс: {self.initial_balance:.2f} USDT"
            )

            return True

        except Exception as e:
            print(f"❌ Ошибка инициализации аккаунта: {e}")
            self.notifier.send_error_notification(f"Ошибка инициализации: {e}")
            return False

    def check_current_position(self):
        """Проверка текущей позиции"""
        try:
            positions = self.exchange.get_open_positions()
            if positions and len(positions) > 0:
                # Упрощенная логика (в реальном боте нужна более детальная обработка)
                pos = positions[0]
                self.current_position = {
                    "amount": float(pos["contracts"]),
                    "entry_price": float(pos["entryPrice"]),
                }
            else:
                self.current_position = None

        except Exception as e:
            print(f"❌ Ошибка проверки позиции: {e}")
            self.current_position = None

    def execute_buy(self, price):
        """Выполнение покупки"""
        try:
            # Получаем баланс
            balance = self.exchange.get_balance()

            # Рассчитываем размер позиции
            amount = self.risk_manager.calculate_position_size(balance, price)

            if amount <= 0:
                print("⏭️  Размер позиции слишком мал, пропускаем")
                return False

            print(f"🟢 BUY: {amount} контрактов по цене ~{price:.2f}")

            # Размещаем рыночный ордер
            order = self.exchange.place_market_order("buy", amount)

            if order:
                # Обновляем текущую позицию
                self.current_position = {
                    "side": "buy",
                    "amount": amount,
                    "entry_price": price,
                    "order_id": order["id"],
                }

                # Логируем сделку
                self.logger.log_trade(
                    "OPEN", TRADING_PAIR, "buy", price, amount, order_id=order["id"]
                )

                # Отправляем уведомление
                self.notifier.send_order_notification(
                    "market", TRADING_PAIR, "buy", amount, price, order["id"]
                )

                self.trade_count += 1
                print(f"✅ Покупка выполнена. ID ордера: {order['id']}")
                return True
            else:
                print("❌ Ошибка при выполнении покупки")
                return False

        except Exception as e:
            print(f"❌ Ошибка выполнения покупки: {e}")
            self.notifier.send_error_notification(f"Ошибка покупки: {e}")
            return False

    def execute_sell(self, price):
        """Выполнение продажи"""
        try:
            # Если есть открытая позиция, закрываем её
            if self.current_position and self.current_position["side"] == "buy":
                amount = self.current_position["amount"]
                entry_price = self.current_position["entry_price"]

                print(f"🔴 SELL: {amount} контрактов по цене ~{price:.2f}")

                # Размещаем рыночный ордер на продажу
                order = self.exchange.place_market_order(
                    "sell", amount, reduce_only=True
                )

                if order:
                    # Расчет прибыли/убытка
                    pnl = (price - entry_price) * amount

                    # Логируем сделку
                    self.logger.log_trade(
                        "CLOSE",
                        TRADING_PAIR,
                        "sell",
                        price,
                        amount,
                        pnl=pnl,
                        order_id=order["id"],
                    )

                    # Отправляем уведомление
                    self.notifier.send_trade_result(
                        TRADING_PAIR, "sell", entry_price, price, amount, pnl
                    )

                    # Сбрасываем текущую позицию
                    self.current_position = None

                    print(f"✅ Продажа выполнена. P&L: {pnl:.2f} USDT")
                    return True
            else:
                # Продажа без открытой позиции (шорт)
                balance = self.exchange.get_balance()
                amount = self.risk_manager.calculate_position_size(balance, price)

                if amount <= 0:
                    print("⏭️  Размер позиции слишком мал, пропускаем")
                    return False

                print(f"🔴 SELL (шорт): {amount} контрактов по цене ~{price:.2f}")

                order = self.exchange.place_market_order("sell", amount)

                if order:
                    self.current_position = {
                        "side": "sell",
                        "amount": amount,
                        "entry_price": price,
                        "order_id": order["id"],
                    }

                    self.logger.log_trade(
                        "OPEN",
                        TRADING_PAIR,
                        "sell",
                        price,
                        amount,
                        order_id=order["id"],
                    )
                    self.notifier.send_order_notification(
                        "market", TRADING_PAIR, "sell", amount, price, order["id"]
                    )

                    self.trade_count += 1
                    print(f"✅ Шорт позиция открыта. ID ордера: {order['id']}")
                    return True

            return False

        except Exception as e:
            print(f"❌ Ошибка выполнения продажи: {e}")
            self.notifier.send_error_notification(f"Ошибка продажи: {e}")
            return False

    def check_stop_loss_take_profit(self, current_price):
        """Проверка стоп-лосса и тейк-профита"""
        if not self.current_position:
            return

        side = self.current_position["side"]
        entry_price = self.current_position["entry_price"]
        amount = self.current_position["amount"]

        # Проверяем состояние позиции
        position_status = self.risk_manager.check_position_health(
            entry_price, current_price, side
        )

        if position_status == "STOP_LOSS":
            print("🛑 Сработал стоп-лосс!")

            # Закрываем позицию
            close_side = "sell" if side == "buy" else "buy"
            order = self.exchange.place_market_order(
                close_side, amount, reduce_only=True
            )

            if order:
                stop_price = self.risk_manager.calculate_stop_loss_price(
                    entry_price, side
                )
                self.notifier.send_stop_loss_notification(
                    TRADING_PAIR, side, entry_price, stop_price, amount
                )

                self.current_position = None

        elif position_status == "TAKE_PROFIT":
            print("🎯 Сработал тейк-профит!")

            # Закрываем позицию
            close_side = "sell" if side == "buy" else "buy"
            order = self.exchange.place_market_order(
                close_side, amount, reduce_only=True
            )

            if order:
                take_profit_price = self.risk_manager.calculate_take_profit_price(
                    entry_price, side
                )
                pnl = (take_profit_price - entry_price) * amount

                self.notifier.send_trade_result(
                    TRADING_PAIR, side, entry_price, take_profit_price, amount, pnl
                )
                self.current_position = None

    def run(self):
        """Главный цикл бота"""
        print("▶️  ЗАПУСК ГЛАВНОГО ЦИКЛА")
        print("=" * 50)

        # Инициализация аккаунта
        if not self.initialize_account():
            print("❌ Не удалось инициализировать аккаунт")
            return

        iteration = 0

        while self.is_running:
            try:
                iteration += 1
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n🔄 Итерация {iteration} | {current_time}")

                # 1. Получение текущей цены
                current_price = self.exchange.get_current_price()
                if not current_price:
                    time.sleep(CHECK_INTERVAL)
                    continue

                # 2. Проверка текущей позиции
                self.check_current_position()

                if self.current_position:
                    print(
                        f"📦 Открытая позиция: {self.current_position['side'].upper()} "
                        f"{self.current_position['amount']} @ {self.current_position['entry_price']:.2f}"
                    )

                    # Проверка стоп-лосса и тейк-профита
                    self.check_stop_loss_take_profit(current_price)
                else:
                    print("📭 Нет открытых позиций")

                # 3. Получение свечей для анализа
                candles = self.exchange.get_candles(limit=50)
                if len(candles) < SLOW_MA_PERIOD + 5:
                    print(f"⏭️  Недостаточно данных: {len(candles)} свечей")
                    time.sleep(CHECK_INTERVAL)
                    continue

                # 4. Получение сигнала от стратегии
                signal = self.strategy.get_signal(candles)

                # 5. Выполнение действий по сигналу
                if signal == "BUY" and not self.current_position:
                    self.execute_buy(current_price)
                elif signal == "SELL":
                    self.execute_sell(current_price)
                else:
                    print(f"⏭️  Сигнал: {signal} - пропускаем")

                # 6. Логирование баланса
                if iteration % 10 == 0:
                    balance = self.exchange.get_balance()
                    print(
                        f"💰 Текущий баланс: {balance:.2f} USDT | Сделок: {self.trade_count}"
                    )

                    # Проверка просадки
                    if self.initial_balance:
                        self.risk_manager.check_max_drawdown(
                            balance, self.initial_balance
                        )

                # 7. Пауза перед следующей итерацией
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                print("\n🛑 Прервано пользователем")
                self.stop()
                break

            except Exception as e:
                print(f"❌ Критическая ошибка в главном цикле: {e}")
                self.logger.log_error(str(e), "main loop")
                self.notifier.send_error_notification(f"Критическая ошибка: {e}")
                time.sleep(CHECK_INTERVAL * 2)


if __name__ == "__main__":
    """Запуск бота"""
    print("🚀 SCALPING BOT FOR OKX")
    print("Version 1.0")
    print()

    bot = ScalpingBot()
    bot.run()
