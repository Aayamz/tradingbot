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
        """Core method to send messages"""
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode='Markdown')
            return True
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            print(f"❌ Telegram Error: {e}")
            return False

    # All the methods your bot might call
    async def send_startup_message(self):
        msg = "🚀 *NIXIE GOLD BOT STARTED*\n\n✅ Monitoring signals..."
        await self.send_message(msg)

    async def send_trade_success(self, trade_info: dict):
        msg = f"""
🚀 *TRADE EXECUTED SUCCESSFULLY*

*Direction:* {trade_info.get('signal', 'LONG')}
*Symbol:* {trade_info.get('symbol', config.SYMBOL)}
*Entry:* ${trade_info.get('entry_price', 0):.2f}
*Ticket:* {trade_info.get('ticket', 'N/A')}
        """.strip()
        await self.send_message(msg)

    async def send_trade_failure(self, trade_info: dict, error: str = None):
        msg = f"""
❌ *TRADE FAILED*

*Direction:* {trade_info.get('signal')}
*Reason:* {error or 'Unknown'}
        """.strip()
        await self.send_message(msg)

    async def send_signal(self, signal):
        # Your existing signal message logic here
        pass

    async def send_text(self, text: str):
        await self.send_message(text)


# ===================== SYNC WRAPPERS (Very Important) =====================
def send_startup_message_sync():
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_startup_message())

def send_trade_success_sync(trade_info):
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_trade_success(trade_info))

def send_trade_failure_sync(trade_info, error=None):
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_trade_failure(trade_info, error))

def send_text_sync(text):
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_text(text))