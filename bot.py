import asyncio
import csv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TimedOut, RetryAfter, NetworkError

# ==============================
# 📄 Load Questions Safely
# ==============================
def load_questions() -> list[list[str]]:
    """Load quiz questions from CSV, handling sections and uneven rows."""
    questions = []
    with open("questions.csv", "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            row = [col.strip() for col in row]
            if not row or row[0] == "":
                continue
            # Pad missing columns up to 6 total (Question, A, B, C, D, Correct)
            while len(row) < 6:
                row.append("")
            questions.append(row)
    return questions

QUESTIONS = load_questions()

# ==============================
# 🚀 /start Command
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Welcome to the Quiz Poll Bot!\n\n"
        "Use /quiz to send all questions as quiz polls.\n"
        "Sections (marked with ###) will appear as text headers."
    )

# ==============================
# 🧩 Send All Questions as Quiz Polls
# ==============================
async def send_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("📤 Sending quiz polls... please wait.")

    for index, row in enumerate(QUESTIONS, start=1):
        # Each row can be either a section header or a question
        question_text = row[0]
        options = row[1:5]
        correct_letter = row[5].strip().upper() if len(row) > 5 else ""

        # 🔹 If it's a section header (starts with ###)
        if question_text.startswith("###"):
            header_text = question_text.replace("###", "").strip()
            await context.bot.send_message(chat_id=chat_id, text=f"📘 *{header_text}*", parse_mode="Markdown")
            print(f"📘 Sent section header: {header_text}")
            await asyncio.sleep(3)
            continue

        # 🔹 If it's a valid question
        if correct_letter not in ["A", "B", "C", "D"]:
            print(f"⚠️ Skipping invalid question {index}: Missing or invalid correct letter.")
            continue

        correct_index = ord(correct_letter) - ord("A")
        sent = False
        attempts = 0

        while not sent and attempts < 3:
            try:
                await context.bot.send_poll(
                    chat_id=chat_id,
                    question=question_text,
                    options=options,
                    type="quiz",
                    correct_option_id=correct_index,
                    is_anonymous=True,
                )
                print(f"✅ Sent question {index}: {question_text[:50]}...")
                sent = True
            except (TimedOut, RetryAfter, NetworkError) as e:
                attempts += 1
                print(f"⚠️ Error sending question {index}: {e}. Retrying in 3s...")
                await asyncio.sleep(3)
            except Exception as e:
                print(f"❌ Failed to send question {index}: {e}")
                break

        await asyncio.sleep(2)

    await update.message.reply_text("✅ All quiz polls have been posted!")

# ==============================
# 🧠 Main Entry
# ==============================
def main():
    TOKEN = "8236591484:AAE89yIh5amaGK7q36mkUFmnkODDCwWExmY"  # 🔑 Replace this with your actual token
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", send_quiz))

    print("🤖 Quiz Poll Bot is running... Type /start in your bot chat.")
    app.run_polling()

if __name__ == "__main__":
    main()
