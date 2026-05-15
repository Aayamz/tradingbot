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
        self.magic_number = config.MAGIC_NUMBER

    def connect(self):
        if not mt5.initialize():
            print("❌ MT5 initialize failed:", mt5.last_error())
            return False
        print("✅ MT5 Connected")
        return True

    def calculate_lot_size(self, entry_price: float, stop_loss: float) -> float:
        """Smart lot size based on risk %"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return config.BASE_LOT_SIZE

            balance = account_info.balance
            risk_amount = (config.RISK_PERCENT / 100) * balance

            # Risk distance in price
            risk_distance = abs(entry_price - stop_loss)
            if risk_distance == 0:
                return config.BASE_LOT_SIZE

            # For XAUUSD, 1 lot = $100 per $1 move
            tick_value = 100.0  
            lot_size = risk_amount / (risk_distance * tick_value)

            # Apply limits
            lot_size = max(config.BASE_LOT_SIZE, min(lot_size, config.MAX_LOT_SIZE))
            
            # Round to broker allowed step (usually 0.01)
            lot_size = round(lot_size, 2)
            
            print(f"💰 Risk Management: {config.RISK_PERCENT}% of ${balance:.2f} = ${risk_amount:.2f} → Lot: {lot_size}")
            return lot_size

        except Exception as e:
            print(f"⚠️ Lot calculation failed, using default: {e}")
            return config.BASE_LOT_SIZE

    def execute_trade(self, signal: dict):
        try:
            if not self.connect():
                return False

            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info:
                print("❌ Symbol info not found")
                return False

            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                print("❌ Could not get price")
                return False

            direction = signal.get('signal', 'LONG').upper()
            price = tick.ask if direction == "LONG" else tick.bid

            # Calculate dynamic SL/TP
            sl_distance = signal.get('stop_loss_distance', config.DEFAULT_SL_DISTANCE)
            tp_distance = signal.get('take_profit_distance', config.DEFAULT_TP_DISTANCE)

            if direction == "LONG":
                order_type = mt5.ORDER_TYPE_BUY
                stop_loss = round(price - sl_distance, 2)
                take_profit = round(price + tp_distance, 2)
            else:
                order_type = mt5.ORDER_TYPE_SELL
                stop_loss = round(price + sl_distance, 2)
                take_profit = round(price - tp_distance, 2)

            lot_size = self.calculate_lot_size(price, stop_loss)

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": round(price, 2),
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": config.DEVIATION,
                "magic": self.magic_number,
                "comment": f"NixieBot_{direction}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            print(f"📤 Sending {direction} | Entry: {price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f} | Lot: {lot_size}")

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ TRADE SUCCESS | Ticket: {result.order} | Lot: {lot_size}")
                
                # Prepare trade_info for notification
                trade_info = {
                    **signal,
                    'entry_price': price,
                    'stop_loss': stop_loss,
                    'take_profit_1': take_profit,
                    'lot_size': lot_size,
                    'ticket': result.order,
                    'execution_time': signal.get('timestamp', 'Now')
                }
                return True, trade_info

            else:
                error = f"Retcode: {result.retcode if result else 'None'} | {result.comment if result else ''}"
                print(f"❌ {error}")
                return False, None

        except Exception as e:
            print(f"❌ Exception in execute_trade: {e}")
            return False, None