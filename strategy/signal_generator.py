"""
Signal Generator - Aggressive & Balanced Version
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime
import config
from data.market_hours import MarketHours
from strategy.regime_detector import RegimeDetector
from strategy.risk_manager import RiskManager
from indicators.technical import TechnicalIndicators
from indicators.structural import StructuralLevels

class SignalGenerator:
    def __init__(self):
        self.market_hours = MarketHours()
        self.regime_detector = RegimeDetector()
        self.risk_manager = RiskManager()
        self.technical = TechnicalIndicators()
        self.structural = StructuralLevels()

    def generate_signal(self, df_h4, df_entry, timestamp=None):
        """
        Main signal generation function - AGGRESSIVE VERSION
        """

        # Temporary: Allow multiple trades for testing
        self.allow_multiple_trades = True
        
        try:
            # Step 1: Market Hours Check
            should_trade, reason = self.market_hours.should_trade_now(timestamp)
            if not should_trade:
                print(f" {reason}")
                return None

            # Step 2: Regime Detection
            regime, adx = self.regime_detector.detect_regime(df_h4)
            print(f" Regime: {self.regime_detector.get_regime_description(regime)} | ADX: {adx:.1f}")

            # Step 3: Current Market Data
            current_price = df_entry['Close'].iloc[-1]
            rsi = df_entry['RSI'].iloc[-1]
            stoch_k = df_entry['Stoch_K'].iloc[-1]
            stoch_d = df_entry['Stoch_D'].iloc[-1]

            print(f"[DATA] Price: {current_price:.2f} | RSI: {rsi:.1f} | Stoch: {stoch_k:.1f}/{stoch_d:.1f}")

            signal = None

            # ================== AGGRESSIVE SIGNAL CONDITIONS ==================
            
            # LONG Signal
            if (rsi < config.RSI_OVERSOLD or rsi < 48) and stoch_k > stoch_d and stoch_k < 45:
                print("→ LONG Conditions Met")
                signal = self._build_signal('LONG', current_price, current_price - 0.25, df_entry, regime)

            # SHORT Signal
            elif (rsi > config.RSI_OVERBOUGHT or rsi > 52) and stoch_k < stoch_d and stoch_k > 55:
                print("→ SHORT Conditions Met")
                signal = self._build_signal('SHORT', current_price, current_price + 0.25, df_entry, regime)

            if signal:
                signal['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                signal['regime'] = self.regime_detector.get_regime_description(regime)
                print(f"✅ SIGNAL GENERATED: {signal['signal']} | Confidence: {signal.get('confidence', 0)}")
                return signal

            print("No signal - conditions not met yet")
            return None

        except Exception as e:
            print(f" Error generating signal: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _build_signal(self, direction, entry_price, level, df, regime):
        """Build signal with safe stop levels"""
        try:
            # Increased SL distance to avoid "Invalid stops"
            sl_pips = 25   # Minimum 25 pips SL

            if direction == 'LONG':
                stop_loss = entry_price - (sl_pips * 0.01)
                multiplier = 1
            else:
                stop_loss = entry_price + (sl_pips * 0.01)
                multiplier = -1

            pip_risk = sl_pips

            # Calculate TPs
            tp1 = entry_price + (multiplier * config.TP1_RATIO * pip_risk * 0.01)
            tp2 = entry_price + (multiplier * config.TP2_RATIO * pip_risk * 0.01)
            tp3 = entry_price + (multiplier * config.TP3_RATIO * pip_risk * 0.01)

            signal = {
                'signal': direction,
                'entry_price': round(entry_price, 2),
                'stop_loss': round(stop_loss, 2),
                'take_profit_1': round(tp1, 2),
                'take_profit_2': round(tp2, 2),
                'take_profit_3': round(tp3, 2),
                'lot_size': 0.01,
                'confidence': self._calculate_confidence(df, regime, pip_risk),
                'pips_risk': round(pip_risk, 1),
                'pips_tp1': round(config.TP1_RATIO * pip_risk, 1),
                'pips_tp2': round(config.TP2_RATIO * pip_risk, 1),
                'pips_tp3': round(config.TP3_RATIO * pip_risk, 1),
                'risk_dollars': 0.0,
                'expected_reward': 0.0,
                'rr_ratio': round(config.TP1_RATIO, 2),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return signal

        except Exception as e:
            print(f" Error building signal: {e}")
            return None

    def _calculate_confidence(self, df, regime, pip_risk):
        """Calculate confidence score"""
        try:
            confidence = 50
            rsi_div = self.technical.check_rsi_divergence(df) if hasattr(self.technical, 'check_rsi_divergence') else None
            
            if rsi_div:
                confidence += 15
            if regime in ['trending', 'breakout_pending']:
                confidence += 12
            if pip_risk < 25:
                confidence += 10
                
            return min(confidence, 100)
        except:
            return 55   # Default confidence


# ================== TEST ==================
if __name__ == "__main__":
    print("Testing Aggressive Signal Generator...")
    # You can add test code here later