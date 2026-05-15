# execution/telegram_bot.py
import asyncio
import logging
from telegram import Bot
import config

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID

    async def send_message(self, text: str):
        try:
            # Changed to Markdown (more forgiving than MarkdownV2)
            await self.bot.send_message(
                chat_id=self.chat_id, 
                text=text, 
                parse_mode='Markdown'          # ← Changed here
            )
            return True
        except Exception as e:
            logger.error(f"Telegram failed: {e}")
            print(f"❌ Telegram Error: {e}")
            return False

    async def send_startup_message(self):
        msg = """
🚀 *NIXIE GOLD BOT STARTED*

✅ Bot is live and monitoring XAUUSD
📡 Auto-trading is ENABLED
        """.strip()
        await self.send_message(msg)

    async def send_signal(self, signal: dict):
        msg = f"""
📊 *NEW SIGNAL GENERATED*

*Direction:* **{signal.get('signal')}**
*Symbol:* `{signal.get('symbol', config.SYMBOL)}`
*Entry:* `${signal.get('entry_price', 0):.2f}`
*Stop Loss:* `${signal.get('stop_loss', 0):.2f}`
*TP1:* `${signal.get('take_profit_1', 0):.2f}`
*Confidence:* {signal.get('confidence', 0)}%
        """.strip()
        await self.send_message(msg)

    async def send_trade_success(self, trade_info: dict):
        msg = f"""
✅ *TRADE EXECUTED SUCCESSFULLY*

*Direction:* **{trade_info.get('signal')}**
*Symbol:* `{trade_info.get('symbol', config.SYMBOL)}`
*Entry Price:* `${trade_info.get('entry_price', 0):.2f}`
*Stop Loss:* `${trade_info.get('stop_loss', 0):.2f}`
*Take Profit:* `${trade_info.get('take_profit_1', 0):.2f}`
*Lot Size:* `{trade_info.get('lot_size', 0.01)}`
*Ticket:* `{trade_info.get('ticket', 'MT5')}`

🕒 {trade_info.get('execution_time', 'Now')}
        """.strip()
        await self.send_message(msg)

    async def send_trade_failure(self, trade_info: dict, error: str = None):
        msg = f"""
❌ *TRADE EXECUTION FAILED*

*Direction:* {trade_info.get('signal')}
*Reason:* {error or 'Broker Rejection'}
        """.strip()
        await self.send_message(msg)

    async def send_text(self, text: str):
        await self.send_message(text)


# Sync wrappers
def send_startup_message_sync():
    asyncio.run(TelegramNotifier().send_startup_message())

def send_signal_sync(signal):
    asyncio.run(TelegramNotifier().send_signal(signal))

def send_trade_success_sync(trade_info):
    asyncio.run(TelegramNotifier().send_trade_success(trade_info))

def send_trade_failure_sync(trade_info, error=None):
    asyncio.run(TelegramNotifier().send_trade_failure(trade_info, error))

def send_text_sync(text):
    asyncio.run(TelegramNotifier().send_text(text))