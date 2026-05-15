import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from siliconmetatrader5 import MetaTrader5
mt5 = MetaTrader5(host="localhost", port=8001)
from datetime import datetime
import config

class LiveTrader:
    def __init__(self):
        self.symbol = config.SYMBOL
        self.magic_number = 123456  
    
    def execute_trade(self, signal):
    
        try:
            print("\n" + "="*70)
            print("🚀 EXECUTION ATTEMPT STARTED")
            print(f"Signal Type : {signal.get('signal')}")
            print(f"Entry Price : {signal.get('entry_price')}")
            print(f"Stop Loss   : {signal.get('stop_loss')}")
            print(f"TP1         : {signal.get('take_profit_1')}")
            print(f"Lot Size    : {signal.get('lot_size', 0.01)}")
            print("="*70)

            # Check MT5 connection
            if not mt5.terminal_info():
                print("❌ MT5 Terminal Not Connected!")
                return False

            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                print(f"❌ Symbol {self.symbol} not found in Market Watch")
                return False

            print(f"✅ Symbol found | Trade Mode: {symbol_info.trade_mode}")

            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                print("❌ Cannot get current tick prices")
                return False

            # Prepare Order
            if signal['signal'] == 'LONG':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid

            lot_size = float(signal.get('lot_size', 0.01))

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": signal['stop_loss'],
                "tp": signal.get('take_profit_1'),
                "deviation": 50,
                "magic": getattr(self, 'magic_number', 123456),
                "comment": f"NixieBot_{signal['signal']}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            print(f"📤 Sending Order to MT5 | Price: {price:.2f} | Lot: {lot_size}")
            
            result = mt5.order_send(request)

            if result is None:
                print("❌ order_send() returned None")
                print(f"Last Error: {mt5.last_error()}")
                return False

            print(f"MT5 Retcode: {result.retcode} | Comment: {result.comment}")

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print("✅ TRADE SUCCESSFULLY PLACED IN MT5!")
                print(f"Ticket: {result.order}")
                return True
            else:
                print("❌ TRADE REJECTED by Broker")
                return False

        except Exception as e:
            print(f"❌ Exception in execute_trade: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close_position(self, position_id):
        """Close a specific position"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                print(f" Position {position_id} not found")
                return False
            
            position = position[0]
            
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position_id,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "Nixie Bot Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f" Position closed: {position_id}")
                return True
            else:
                print(f" Failed to close position: {result.comment if result else 'Unknown error'}")
                return False
                
        except Exception as e:
            print(f" Error closing position: {e}")
            return False
    
    def get_open_positions(self):
        """Get all open positions from this bot"""
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            if positions is None:
                return []
            
            bot_positions = [p for p in positions if p.magic == self.magic_number]
            return bot_positions
            
        except Exception as e:
            print(f"[ Error getting positions: {e}")
            return []
    
    def check_position_status(self, position_id):
        """Check if position hit TP1 and move SL to breakeven"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                return None
            
            position = position[0]
            current_price = position.price_current
            entry_price = position.price_open
            
            if position.type == mt5.ORDER_TYPE_BUY:
                profit_pips = (current_price - entry_price) / 0.10
            else:
                profit_pips = (entry_price - current_price) / 0.10
            
            return {
                'ticket': position_id,
                'profit_pips': profit_pips,
                'profit_dollars': position.profit,
                'type': 'LONG' if position.type == mt5.ORDER_TYPE_BUY else 'SHORT'
            }
            
        except Exception as e:
            print(f" Error checking position: {e}")
            return None
    
    def modify_stop_loss(self, position_id, new_sl):
        """Modify stop loss (e.g., move to breakeven)"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                return False
            
            position = position[0]
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": self.symbol,
                "position": position_id,
                "sl": new_sl,
                "tp": position.tp
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f" Stop loss modified to ${new_sl:.2f}")
                return True
            else:
                print(f" Failed to modify SL")
                return False
                
        except Exception as e:
            print(f" Error modifying SL: {e}")
            return False


if __name__ == "__main__":
    print("  WARNING: This module executes REAL trades!")
    print("   Only use on a demo account for testing!")
    print()
    
    trader = LiveTrader()
    
    positions = trader.get_open_positions()
    print(f" Open positions: {len(positions)}")
    
    for pos in positions:
        status = trader.check_position_status(pos.ticket)
        if status:
            print(f"   Ticket: {pos.ticket}")
            print(f"   Type: {status['type']}")
            print(f"   Profit: ${status['profit_dollars']:.2f} ({status['profit_pips']:.1f} pips)")