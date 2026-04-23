import os
from pathlib import Path

# Настройки OKX API
OKX_CONFIG = {
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
    'password': 'YOUR_PASSPHRASE',
    'enableRateLimit': True,
    'test': True  # Использование демо-счета
}

# Настройки Telegram
TELEGRAM_CONFIG = {
    'token': 'YOUR_TELEGRAM_BOT_TOKEN',
    'chat_id': 'YOUR_CHAT_ID'
}

# Настройки логов
LOG_CONFIG = {
    'log_dir': Path('logs'),
    'trading_log': Path('logs/trading/trading.log'),
    'error_log': Path('logs/errors/error.log'), 
    'bot_log': Path('logs/bot/bot.log'),
    'system_log': Path('logs/system/system.log'),
    'log_level': 'DEBUG'  # DEBUG/INFO/WARNING/ERROR/CRITICAL
}

# Создаем директории для логов
for log_path in LOG_CONFIG.values():
    if isinstance(log_path, Path):
        log_path.parent.mkdir(parents=True, exist_ok=True)

# Настройки бота
BOT_CONFIG = {
    'symbol': 'BTC-USDT',
    'timeframe': '1m',
    'max_retries': 3,
    'order_timeout': 30
}
