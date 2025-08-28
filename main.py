import os
import requests
import datetime as dt
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========= CONFIG =========
FYERS_BASE = os.getenv("FYERS_BASE", "https://api.fyers.in")
FYERS_DATA_BASE = os.getenv("FYERS_DATA_BASE", "https://api.fyers.in/data-rest/v2")
FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCb3NMaGhBVlNwUUtBME4tSWdvWHY0eGp0YmZqRTRxZVJUZjU2OWMxaFBtcFBUSTF5MmNoTDZ4ZmN6YWw0LWpnWFdyQjBHRl9NeFI1NlU5akZ5cW10M3J1R0VVQmtEeHM1UkJHR2J5WG9oTXROOXJ4az0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI5YmU1NGU0ZjRjZTJkOTFhMTVkZWQ4YzcyODVkMDMyODA5NWFkNTcyMTc5MjNlMjEzOWZjOGRkMSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWUEyNDY0MCIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzU2NTEzODAwLCJpYXQiOjE3NTY0MTIwMDEsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc1NjQxMjAwMSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.jnCRXBU97FrVWdd5iWijhITA3iXbCjij0ymdHU_4hrQ")
FYERS_APP_ID = os.getenv("FYERS_APP_ID","CGDSV5GE7E-100")
BANKNIFTY_SPOT = os.getenv("BANKNIFTY_SPOT", "NSE:NIFTYBANK-INDEX")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID","1597187434")

# ========= TELEGRAM BOT =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot started! It will run at 09:30 AM IST every day.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ Bot stopped manually.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Bot is online and waiting for 09:30 candle.")

# ========= TRADING FUNCTION =========
async def run_strategy(context: ContextTypes.DEFAULT_TYPE):
    now = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)  # IST
    if now.hour == 9 and now.minute == 30:
        try:
            end_time = int(dt.datetime.timestamp(now))
            start_time = end_time - 300

            url = f"{FYERS_DATA_BASE}/history/?symbol={BANKNIFTY_SPOT}&resolution=5&date_format=0&range_from={start_time}&range_to={end_time}&cont_flag=1"
            headers = {"Authorization": f"Bearer {FYERS_ACCESS_TOKEN}"}
            response = requests.get(url, headers=headers).json()

            if "candles" in response:
                candle = response["candles"][0]
                high = candle[2]
                low = candle[3]
                msg = f"📊 09:25–09:30 Candle:\nHigh = {high}\nLow = {low}"
            else:
                msg = "⚠️ Failed to fetch candle data."

        except Exception as e:
            msg = f"❌ Error: {e}"

        await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# ========= MAIN =========
def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    app.job_queue.run_repeating(run_strategy, interval=60, first=5)

    app.run_polling()

if __name__ == "__main__":
    main()
