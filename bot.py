import threading

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ai import AI
from config import DB_PATH, OPENAI_API_KEY, OPENAI_MODEL, TELEGRAM_BOT_TOKEN
from db import Database
from webserver import start_health_server

db = Database(DB_PATH)
ai = AI(OPENAI_API_KEY, OPENAI_MODEL)


def merge_memory(current: list[str], add: list[str], remove: list[str]) -> list[str]:
    result = list(current)

    # Remove exact/near-exact old memories.
    for old in remove:
        result = [x for x in result if x.strip() != old.strip()]

    # Add new memories without duplicates.
    for item in add:
        if item not in result:
            result.append(item)

    return result[-30:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "هلاا 🌚\n"
        "اني موجودة حتى نسولف براحتنا.\n\n"
        "احچي وياي طبيعي، والاشياء المهمة اللي تريدني أتذكرها أگدر أخليها بالذاكرة.\n\n"
        "الأوامر:\n"
        "/memory — شنو متذكرة عنك\n"
        "/forget — مسح الذاكرة\n"
        "/clear — مسح المحادثة الأخيرة\n"
        "/help — المساعدة"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/memory — عرض الذاكرة المحفوظة\n"
        "/forget — حذف كل الذاكرة\n"
        "/clear — حذف سجل المحادثة الأخيرة\n"
        "/start — بدء البوت من جديد"
    )


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.get_or_create_user(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.full_name,
    )
    memory = user["memory"]

    if not memory:
        await update.message.reply_text("حالياً ما متذكرة عنك شي مهم.")
        return

    text = "هاي الأشياء المحفوظة عنك:\n\n" + "\n".join(
        f"• {item}" for item in memory
    )
    await update.message.reply_text(text)


async def forget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_all(update.effective_user.id)
    await update.message.reply_text("تم مسح الذاكرة وسجل المحادثة من قاعدة البوت.")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_history(update.effective_user.id)
    await update.message.reply_text("تمام، مسحت سجل المحادثة الأخيرة. الذاكرة المهمة بقت مثل ما هي.")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    tg_user = update.effective_user
    user_message = update.message.text.strip()

    user = db.get_or_create_user(
        tg_user.id,
        tg_user.username,
        tg_user.full_name,
    )

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    try:
        answer = ai.reply(
            user_message=user_message,
            memory=user["memory"],
            history=user["history"],
            display_name=tg_user.full_name,
        )

        history = user["history"] + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": answer},
        ]

        # Memory extraction is intentionally separate so the main answer
        # stays natural and the database remains easy to inspect/edit.
        try:
            add, remove = ai.extract_memory(
                user_message=user_message,
                assistant_reply=answer,
                current_memory=user["memory"],
            )
            memory = merge_memory(user["memory"], add, remove)
        except Exception:
            # If memory extraction fails, don't break the conversation.
            memory = user["memory"]

        db.save_user(
            telegram_id=tg_user.id,
            memory=memory,
            history=history,
            username=tg_user.username,
            display_name=tg_user.full_name,
        )

        await update.message.reply_text(answer)

    except Exception as exc:
        print("AI ERROR:", repr(exc))
        await update.message.reply_text(
            "صار عندي عطل بسيط بالخدمة 😅 جرب دزلي الرسالة مرة ثانية."
        )


def main():
    threading.Thread(target=start_health_server, daemon=True).start()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("memory", memory_command))
    application.add_handler(CommandHandler("forget", forget_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
