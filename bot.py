from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import re
import json
import os

# ========= НАСТРОЙКИ =========
ADMIN_ID = 7849292154
ALLOWED_FILE = "allowed_users.json"

TOKEN = os.getenv("BOT_TOKEN")

# ========= ХРАНЕНИЕ ДОСТУПА =========
def load_allowed_users():
    if not os.path.exists(ALLOWED_FILE):
        with open(ALLOWED_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return set()

    with open(ALLOWED_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_allowed_users(users):
    with open(ALLOWED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)


ALLOWED_USERS = load_allowed_users()

# ========= ДАННЫЕ =========
# позже сюда вставятся вопросы
DATA = []

# ========= ПОИСК =========
def normalize(text):
    return re.sub(r"[^\u0400-\u04FFa-z0-9\s]", "", text.lower()).strip()


def first_letters(text):
    return "".join(word[0] for word in normalize(text).split() if word)


def search_data(query, mode):
    nq = normalize(query)
    results = []

    for item in DATA:
        q = normalize(item["question"])
        a = normalize(item["answer"])

        if mode == "normal":
            if nq in q or nq in a:
                results.append(item)

        else:
            if (
                first_letters(item["question"]).startswith(nq.replace(" ", ""))
                or first_letters(item["answer"]).startswith(nq.replace(" ", ""))
            ):
                results.append(item)

    return results


def is_allowed(user_id):
    return user_id == ADMIN_ID or user_id in ALLOWED_USERS


# ========= КНОПКИ =========
def mode_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔤 По первым буквам", callback_data="mode_letters"),
            InlineKeyboardButton("🔍 Обычный поиск", callback_data="mode_normal")
        ]
    ])


# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not is_allowed(user.id):

        admin_text = (
            "👤 Новый пользователь\n\n"
            f"Имя: {user.first_name}\n"
            f"ID: {user.id}\n\n"
            f"`/access {user.id}`"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="Markdown"
        )

        await update.message.reply_text(
            "⛔ Доступ закрыт.\nЖдите одобрения администратора."
        )

        return

    context.user_data["mode"] = "letters"

    await update.message.reply_text(
        "Выберите режим поиска:",
        reply_markup=mode_keyboard()
    )


# ========= ACCESS =========
async def access(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Использование: /access TG_ID")
        return

    try:

        user_id = int(context.args[0])

        ALLOWED_USERS.add(user_id)

        save_allowed_users(ALLOWED_USERS)

        await update.message.reply_text(
            f"✅ Доступ открыт для {user_id}"
        )

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Администратор разрешил доступ.\nВыберите режим поиска:",
            reply_markup=mode_keyboard()
        )

    except ValueError:

        await update.message.reply_text("❌ Неверный TG ID")


# ========= CALLBACK =========
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_allowed(query.from_user.id):
        return

    if query.data == "mode_letters":

        context.user_data["mode"] = "letters"

        await query.edit_message_text(
            "🔤 Режим: поиск по первым буквам\nВведите запрос:"
        )

    elif query.data == "mode_normal":

        context.user_data["mode"] = "normal"

        await query.edit_message_text(
            "🔍 Режим: обычный поиск\nВведите запрос:"
        )


# ========= ПОИСК =========
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_allowed(update.effective_user.id):

        await update.message.reply_text("⛔ Доступ не разрешён")

        return

    query_text = update.message.text

    mode = context.user_data.get("mode", "letters")

    results = search_data(query_text, mode)

    if not results:

        await update.message.reply_text("❌ Ничего не найдено")

        return

    text = ""

    for item in results:

        text += f"❓ {item['question']}\n"
        text += f"✅ {item['answer']}\n\n"

    for i in range(0, len(text), 4000):

        await update.message.reply_text(text[i:i+4000])


# ========= ЗАПУСК =========
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("access", access))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
