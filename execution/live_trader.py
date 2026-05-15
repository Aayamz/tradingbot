import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from siliconmetatrader5 import MetaTrader5
mt5 = MetaTrader5(host="localhost", port=8001)
mt5._MetaTrader5__conn.execute("import numpy as np") 
print("Bridge patched! Trading should work now.")
from datetime import datetime
import config
import logging

logger = logging.getLogger(__name__)

class LiveTrader:
    def __init__(self):
        self.symbol = config.SYMBOL
        self.magic_number = 234000

    def connect(self):
        if not mt5.initialize():
            print("❌ MT5 initialize failed:", mt5.last_error())
            return False
        print("✅ MT5 Connected")
        return True

    def execute_trade(self, signal: dict):
        try:
            if not self.connect():
                return False

            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                print(f"❌ Symbol {self.symbol} not found")
                return False

            if not mt5.symbol_select(self.symbol, True):
                print(f"❌ Failed to select symbol {self.symbol}")

            # Get current price
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                print("❌ Failed to get current price")
                return False

            direction = signal.get('signal', 'LONG').upper()
            lot_size = float(signal.get('lot_size', 0.01))

            if direction == "LONG":
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid

            stop_loss = signal.get('stop_loss')
            take_profit = signal.get('take_profit_1') or signal.get('take_profit')

            # === CRITICAL FIX: Adjust SL/TP according to broker rules ===
            point = symbol_info.point
            stops_level = symbol_info.trade_stops_level * point   # Minimum distance required

            print(f"📊 Symbol: {self.symbol} | Price: {price:.2f} | Stops Level: {stops_level:.2f} points")

            if direction == "LONG":
                # For BUY: SL must be below price, TP above price
                min_sl = price - max(stops_level * 2, 0.50)   # at least 50 cents away for gold
                min_tp = price + max(stops_level * 2, 0.50)
                
                if stop_loss is None or stop_loss >= price:
                    stop_loss = min_sl
                if take_profit is None or take_profit <= price:
                    take_profit = min_tp

            else:  # SHORT
                min_sl = price + max(stops_level * 2, 0.50)
                min_tp = price - max(stops_level * 2, 0.50)
                
                if stop_loss is None or stop_loss <= price:
                    stop_loss = min_sl
                if take_profit is None or take_profit >= price:
                    take_profit = min_tp

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": round(stop_loss, 2),
                "tp": round(take_profit, 2),
                "deviation": 50,
                "magic": self.magic_number,
                "comment": f"NixieBot_{direction}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            print(f"📤 Sending {direction} | Entry: {price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ TRADE SUCCESS | Ticket: {result.order}")
                return True
            else:
                error_msg = f"Retcode: {result.retcode if result else 'None'} | {result.comment if result else mt5.last_error()}"
                print(f"❌ {error_msg}")
                return False

        except Exception as e:
            print(f"❌ Exception in execute_trade: {e}")
            return False