import os
from dotenv import load_dotenv

load_dotenv()

# ================== BOT CONFIGURATION ==================

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

MT5_LOGIN = int(os.getenv('MT5_LOGIN', 0))
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_SERVER = os.getenv('MT5_SERVER')

SYMBOL = os.getenv('SYMBOL', 'XAUUSDm')
ACCOUNT_BALANCE = float(os.getenv('ACCOUNT_BALANCE', 100))

# ================== TIMEFRAME SETTINGS FOR TESTING ==================
TIMEFRAME_H4 = 'H4'          # Keep H4 for higher timeframe bias
TIMEFRAME_ENTRY = 'M1'       # Change this → 'M5' or 'M1'

# For very aggressive testing
# TIMEFRAME_ENTRY = 'M1'

# ================== AGGRESSIVE SETTINGS ==================

RISK_PERCENT = 2.0
MAX_RISK_PERCENT = 2.0

SCAN_INTERVAL_MINUTES = 0.5                  # Fast for debugging

# Technical Indicators
EMA_FAST = 20
EMA_SLOW = 50
RSI_PERIOD = 14
RSI_OVERSOLD = 45
RSI_OVERBOUGHT = 65
STOCH_PERIOD = 5
STOCH_SMOOTH_K = 3
STOCH_SMOOTH_D = 3
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ATR_PERIOD = 14

# Regime Detection
ADX_THRESHOLD_TRENDING = 20
ADX_THRESHOLD_RANGING = 15
BB_WIDTH_THRESHOLD = 0.015

# Trade Settings
MIN_RISK_REWARD = 1.5
MAX_STOP_LOSS_PIPS = 40

TP1_RATIO = 1.5
TP2_RATIO = 2.5
TP3_RATIO = 4.0

TP1_SIZE_PERCENT = 40
TP2_SIZE_PERCENT = 35
TP3_SIZE_PERCENT = 25

# ML Settings
USE_ML_FILTER = True
ML_CONFIDENCE_THRESHOLD = 0.45
ML_MODEL_PATH = 'models/trained_model.pkl'
ML_TRAINING_SAMPLES = 1000

# Session & Time
TRADING_SESSIONS_ONLY = False
LONDON_OPEN = 0
LONDON_CLOSE = 24
NY_OPEN = 0
NY_CLOSE = 24

# Backtesting
BACKTEST_MODE = True
BACKTEST_START_DATE = '2024-01-01'
BACKTEST_END_DATE = '2026-05-14'
BACKTEST_INITIAL_CAPITAL = 10000
BACKTEST_DATA_TIMEFRAME = "M15"

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DRY_RUN = False
# DRY_RUN = ENVIRONMENT == 'development'
AUTO_TRADE = True

LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/trading.log'


def validate_config():
    """Validate that all required config is set"""
    errors = []
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN not set in .env file")
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID not set in .env file")
    if MT5_LOGIN == 0:
        errors.append("MT5_LOGIN not set in .env file")
    if not MT5_PASSWORD:
        errors.append("MT5_PASSWORD not set in .env file")
    if not MT5_SERVER:
        errors.append("MT5_SERVER not set in .env file")
    
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f" - {error}")
        return False
    
    print("✅ Configuration validated successfully! (Aggressive Mode)")
    print(f"   Scan Interval: {SCAN_INTERVAL_MINUTES} min | ML Threshold: {ML_CONFIDENCE_THRESHOLD}")
    return True


if __name__ == "__main__":
    validate_config()