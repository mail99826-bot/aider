"""
strategy.py - торговая логика (когда покупать/продавать)
"""

import pandas as pd

from config import *
from logger import TradeLogger


class TradingStrategy:
    def __init__(self, logger=None):
        """Инициализация стратегии"""
        self.fast_ma_period = FAST_MA_PERIOD
        self.slow_ma_period = SLOW_MA_PERIOD
        self.rsi_period = RSI_PERIOD

        # Инициализация логгера
        self.logger = logger or TradeLogger()

        print("📊 Стратегия инициализирована:")
        print(f"   Быстрая MA: {self.fast_ma_period}")
        print(f"   Медленная MA: {self.slow_ma_period}")
        print(f"   RSI период: {self.rsi_period}")

    def calculate_indicators(self, candles):
        """
        Расчет технических индикаторов
        """
        if len(candles) < max(self.slow_ma_period, self.rsi_period) + 1:
            return None, None, None

        # Создаем DataFrame из свечей
        df = pd.DataFrame(
            candles, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        # Рассчитываем скользящие средние
        df["fast_ma"] = df["close"].rolling(window=self.fast_ma_period).mean()
        df["slow_ma"] = df["close"].rolling(window=self.slow_ma_period).mean()

        # Рассчитываем RSI
        df["price_change"] = df["close"].diff()
        df["gain"] = df["price_change"].where(df["price_change"] > 0, 0)
        df["loss"] = -df["price_change"].where(df["price_change"] < 0, 0)

        avg_gain = df["gain"].rolling(window=self.rsi_period).mean()
        avg_loss = df["loss"].rolling(window=self.rsi_period).mean()

        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Получаем последние значения
        last_close = df["close"].iloc[-1]
        last_fast_ma = df["fast_ma"].iloc[-1]
        last_slow_ma = df["slow_ma"].iloc[-1]
        last_rsi = df["rsi"].iloc[-1]

        return last_close, last_fast_ma, last_slow_ma, last_rsi

    def get_signal(self, candles):
        """
        Генерация торгового сигнала на основе индикаторов
        Возвращает: "BUY", "SELL" или "HOLD"
        """
        try:
            # Рассчитываем индикаторы
            indicators = self.calculate_indicators(candles)
            if indicators[0] is None:
                return "HOLD"

            last_close, fast_ma, slow_ma, rsi = indicators

            # Логируем текущие значения
            print(
                f"📈 Цена: {last_close:.2f}, Быстрая MA: {fast_ma:.2f}, "
                f"Медленная MA: {slow_ma:.2f}, RSI: {rsi:.2f}"
            )

            # Правила для BUY сигнала:
            # 1. Быстрая MA пересекает медленную MA снизу вверх (золотое пересечение)
            # 2. RSI вышел из зоны перепроданности (<30)
            if (
                fast_ma > slow_ma
                and self.calculate_indicators(candles[:-1])[1]
                <= self.calculate_indicators(candles[:-1])[2]
                and rsi > 30
                and rsi < 70
            ):
                print("🎯 СИГНАЛ: BUY (Золотое пересечение + RSI нейтральный)")
                return "BUY"

            # Правила для SELL сигнала:
            # 1. Быстрая MA пересекает медленную MA сверху вниз (мертвое пересечение)
            # 2. RSI вышел из зоны перекупленности (>70)
            elif (
                fast_ma < slow_ma
                and self.calculate_indicators(candles[:-1])[1]
                >= self.calculate_indicators(candles[:-1])[2]
                and rsi > 30
                and rsi < 70
            ):
                print("🎯 СИГНАЛ: SELL (Мертвое пересечение + RSI нейтральный)")
                return "SELL"

            # Сигнал на продажу при перекупленности
            elif rsi > 70:
                print("⚠️  RSI > 70 (перекупленность) - SELL")
                return "SELL"

            # Сигнал на покупку при перепроданности
            elif rsi < 30:
                print("⚠️  RSI < 30 (перепроданность) - BUY")
                return "BUY"

            else:
                return "HOLD"

        except Exception as e:
            error_msg = f"Ошибка в стратегии: {e}"
            self.logger.log_error(error_msg, "get_signal")
            return "HOLD"

    def calculate_position_size(
        self, balance, risk_percent=RISK_PER_TRADE, stop_loss_percent=STOP_LOSS_PERCENT
    ):
        """
        Расчет размера позиции на основе риска
        """
        risk_amount = balance * risk_percent
        # Упрощенный расчет (в реальном боте нужно учитывать текущую цену)
        return risk_amount / stop_loss_percent
