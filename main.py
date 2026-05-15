"""
Nixie's Gold Bot - Main Execution Script (Fixed & Aggressive)
"""
import schedule
import time
from datetime import datetime
import sys
import logging
from colorama import Fore, Style, init

import config
from data.data_handler import DataHandler
from strategy.signal_generator import SignalGenerator
from execution.telegram_bot import TelegramNotifier
from execution.telegram_multi_user import MultiUserTelegramBot
from models.ml_model import MLSignalFilter
from models.trade_logger import TradeLogger
from execution.live_trader import LiveTrader

# Initialize colorama
init(autoreset=True)

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NixieGoldBot:
    def __init__(self):
        self.handler = DataHandler()
        self.signal_generator = SignalGenerator()
        self.telegram = TelegramNotifier()
        self.multi_user_telegram = MultiUserTelegramBot()
        self.ml_filter = MLSignalFilter()
        self.trade_logger = TradeLogger()
        self.live_trader = LiveTrader()
        
        self.signals_today = 0
        self.running = False
        self.auto_trade_enabled = True  # Force enabled for testing

    def initialize(self):
        print(Fore.CYAN + "\nInitializing Nixie Gold Bot (Aggressive Mode)...")
        
        if not config.validate_config():
            print(Fore.RED + "[FAIL] Configuration validation failed!")
            return False

        if not self.handler.connect_mt5():
            print(Fore.RED + "[FAIL] Failed to connect to MT5")
            return False

        import asyncio
        asyncio.run(self.telegram.send_startup_message())

        print(Fore.GREEN + "✅ MT5 Connected Successfully")
        return True

    def scan_for_signals(self):
        try:
            print(Fore.CYAN + f"\n{'='*60}")
            print(Fore.CYAN + f"Scanning for signals at {datetime.now().strftime('%H:%M:%S')}")
            print(Fore.CYAN + f"{'='*60}")

            df_h4 = self.handler.get_gold_data('H4', 200)
            df_m15 = self.handler.get_gold_data('M1', 800)   # Changed to M5 for faster signals

            if df_h4 is None or df_m15 is None:
                print(Fore.RED + "Failed to fetch data")
                return

            # Calculate indicators
            df_h4 = self.signal_generator.technical.calculate_all(df_h4)
            df_m15 = self.signal_generator.technical.calculate_all(df_m15)

            signal = self.signal_generator.generate_signal(df_h4, df_m15)

            if signal:
                self._process_signal(signal, df_h4, df_m15)
            else:
                print(Fore.BLUE + "No signal at this time")

        except Exception as e:
            logger.error(f"Error in scan_for_signals: {e}")

    def _process_signal(self, signal, df_h4, df_m15):
        """Process approved signal"""
        try:
            print(Fore.GREEN + "\n" + "="*60)
            print(Fore.GREEN + "🚀 SIGNAL GENERATED!")
            print(Fore.GREEN + "="*60)

            print(Fore.WHITE + f"Direction: {Fore.GREEN if signal['signal'] == 'LONG' else Fore.RED}{signal['signal']}")
            print(Fore.WHITE + f"Entry: ${signal['entry_price']:.2f}")
            print(Fore.WHITE + f"Stop Loss: ${signal['stop_loss']:.2f}")
            print(Fore.WHITE + f"TP1: ${signal.get('take_profit_1'):.2f}")
            print(Fore.WHITE + f"Confidence: {signal.get('confidence', 50)}%")

            # FORCE EXECUTION
            if self.auto_trade_enabled and not config.DRY_RUN:
                print(Fore.YELLOW + "\n📤 Sending trade to MT5...")
                success = self.live_trader.execute_trade(signal)
                
                if success:
                    print(Fore.GREEN + "✅ Trade successfully placed in MT5!")
                else:
                    print(Fore.RED + "❌ Trade execution failed")
            else:
                print(Fore.YELLOW + "⚠️ AUTO_TRADE or DRY_RUN is blocking execution")

            # Send to Telegram
            try:
                import asyncio
                asyncio.run(self.multi_user_telegram.send_signal(signal))
            except:
                print(Fore.RED + "Failed to send to Telegram")

        except Exception as e:
            print(Fore.RED + f"Error processing signal: {e}")

    def run(self):
        if not self.initialize():
            return

        self.running = True

        schedule.every(config.SCAN_INTERVAL_MINUTES).minutes.do(self.scan_for_signals)

        print(Fore.GREEN + "\n✅ Bot is running in Aggressive Mode!")
        print(Fore.CYAN + f"Scanning every {config.SCAN_INTERVAL_MINUTES} minute(s)")

        # First scan immediately
        self.scan_for_signals()

        while self.running:
            schedule.run_pending()
            time.sleep(30)

    def shutdown(self):
        print(Fore.YELLOW + "\nShutting down bot...")
        self.handler.disconnect_mt5()
        self.running = False


def main():

    bot = NixieGoldBot()
    bot.run()


if __name__ == "__main__":

    main()
