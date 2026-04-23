""" "risk_manager.py - управление рисками и защита капитала"""

from config import *
from logger import TradeLogger


class RiskManager:
    def __init__(self, logger=None):
        """Инициализация менеджера рисков"""
        self.max_position_size = MAX_POSITION_SIZE
        self.stop_loss_percent = STOP_LOSS_PERCENT
        self.take_profit_percent = TAKE_PROFIT_PERCENT
        self.risk_per_trade = RISK_PER_TRADE

        # Инициализация логгера
        self.logger = logger or TradeLogger()

        self.logger.log_info("🛡️  Менеджер рисков инициализирован")
        self.logger.log_info(f"   Макс. размер позиции: {self.max_position_size}")
        self.logger.log_info(f"   Стоп-лосс: {self.stop_loss_percent}%")
        self.logger.log_info(f"   Тейк-профит: {self.take_profit_percent}%")
        self.logger.log_info(f"   Риск на сделку: {self.risk_per_trade*100}%")

    def calculate_position_size(self, balance, current_price):
        """
        Расчет размера позиции на основе баланса и риска
        """
        # Риск в денежном выражении
        risk_amount = balance * self.risk_per_trade

        # Стоп-лосс в денежном выражении
        stop_loss_amount = current_price * (self.stop_loss_percent / 100)

        # Размер позиции (сколько контрактов можно купить)
        if stop_loss_amount > 0:
            position_size = risk_amount / stop_loss_amount
        else:
            position_size = 0

        # Ограничение максимальным размером позиции
        position_size = min(position_size, self.max_position_size)

        return round(position_size, 8)  # Округляем до 8 знаков

    def calculate_stop_loss_price(self, entry_price, side):
        """
        Расчет цены стоп-лосса
        """
        if side == "buy":
            # Для лонга стоп-лосс ниже цены входа
            return entry_price * (1 - self.stop_loss_percent / 100)
        elif side == "sell":
            # Для шорта стоп-лосс выше цены входа
            return entry_price * (1 + self.stop_loss_percent / 100)
        else:
            return entry_price

    def calculate_take_profit_price(self, entry_price, side):
        """
        Расчет цены тейк-профита
        """
        if side == "buy":
            # Для лонга тейк-профит выше цены входа
            return entry_price * (1 + self.take_profit_percent / 100)
        elif side == "sell":
            # Для шорта тейк-профит ниже цены входа
            return entry_price * (1 - self.take_profit_percent / 100)
        else:
            return entry_price

    def check_position_health(self, entry_price, current_price, side):
        """
        Проверка состояния позиции
        Возвращает: "HOLD", "STOP_LOSS", "TAKE_PROFIT"
        """
        if side == "buy":
            # Лонг позиция
            if current_price <= self.calculate_stop_loss_price(entry_price, side):
                return "STOP_LOSS"
            elif current_price >= self.calculate_take_profit_price(entry_price, side):
                return "TAKE_PROFIT"
        elif side == "sell":
            # Шорт позиция
            if current_price >= self.calculate_stop_loss_price(entry_price, side):
                return "STOP_LOSS"
            elif current_price <= self.calculate_take_profit_price(entry_price, side):
                return "TAKE_PROFIT"

        return "HOLD"

    def check_max_drawdown(self, balance, initial_balance, max_drawdown_percent=20):
        """
        Проверка максимальной просадки
        """
        drawdown_percent = ((initial_balance - balance) / initial_balance) * 100

        if drawdown_percent >= max_drawdown_percent:
            self.logger.log_error(
                f"🚨 ПРЕВЫШЕНА МАКСИМАЛЬНАЯ ПРОСАДКА: {drawdown_percent:.2f}%"
            )
            return False

        return True
