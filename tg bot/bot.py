import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import nest_asyncio
import asyncio

# 🔒 Токен от BotFather
TOKEN = "7941509777:AAGfhazLCs94gtDwPb1qnTHY1A45P7WKy_s"

# Вопросы теста
questions = [
    "1. Мне тяжело засыпать по ночам",
    "2. Я часто чувствую тревогу без причины",
    "3. Мне трудно доверять людям",
    "4. Я чувствую себя отстранённо от близких",
    "5. У меня часто бывают резкие перепады настроения",
    "6. Я быстро устаю, даже если физически не напрягаюсь",
    "7. Меня раздражают мелочи",
    "8. Я избегаю общения с другими людьми",
    "9. Мне сложно сосредоточиться на задачах",
    "10. Я испытываю чувство вины без причины",
    "11. Мне сложно получать удовольствие от привычных вещей",
    "12. Я чувствую внутреннюю пустоту",
    "13. Я стал более подозрительным",
    "14. У меня пропал аппетит или наоборот — переедаю",
    "15. Мне кажется, что никто меня не понимает",
    "16. Я думаю о том, как всё было раньше",
    "17. Я чувствую, что застрял в прошлом",
    "18. Я тревожусь за будущее",
    "19. Иногда мне трудно дышать без причины",
    "20. Я хочу быть один и чтобы меня никто не трогал"
]

# Простая база
user_data = {}

# Логгинг
logging.basicConfig(level=logging.INFO)

# Интерпретация результата
def interpret_result(score):
    if score <= 40:
        return "🔵 Уровень тревожности низкий. Похоже, ты адаптируешься хорошо."
    elif score <= 70:
        return "🟡 Умеренный уровень тревожности. Возможно, тебе будет полезно поговорить с кем-то."
    else:
        return "🔴 Высокий уровень тревожности. Рекомендуем пообщаться с психологом."

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {
        "current_question": 0,
        "answers": []
    }

    await update.message.reply_text(
        "Привет! Это короткий тест, который поможет понять, как ты адаптируешься к мирной жизни. "
        "Ответь на 20 вопросов по шкале от 1 (совсем не согласен) до 5 (полностью согласен).\n\n"
        "Начнём:"
    )
    await send_question(update, context)

# Отправка вопроса
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    q_index = user_data[user_id]["current_question"]

    if q_index < len(questions):
        reply_markup = ReplyKeyboardMarkup([['1', '2', '3', '4', '5']], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(questions[q_index], reply_markup=reply_markup)
    else:
        await finish_test(update, context)

# Обработка ответа
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_data:
        await update.message.reply_text("Пожалуйста, начни с команды /start")
        return

    if text not in ['1', '2', '3', '4', '5']:
        await update.message.reply_text("Пожалуйста, выбери число от 1 до 5.")
        return

    user_data[user_id]["answers"].append(int(text))
    user_data[user_id]["current_question"] += 1

    await send_question(update, context)

# Завершение теста
async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score = sum(user_data[user_id]["answers"])
    result_text = interpret_result(score)

    await update.message.reply_text(
        f"Тест завершён.\n\nТвой балл: {score} из 100\n{result_text}",
        reply_markup=ReplyKeyboardRemove()
    )

    if score > 70:
        await update.message.reply_text(
            "🔴 Хочешь поговорить с психологом? Напиши нашему специалисту:\n@your_psychologist_username"
        )
    else:
        await update.message.reply_text("Если тебе когда-нибудь захочется поддержки — бот всегда на связи.")

    # Очистка данных пользователя после завершения теста
    del user_data[user_id]

# Основная функция
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    # Применяем nest_asyncio для работы с уже существующим event loop
    nest_asyncio.apply()

    # Запуск основного цикла событий
    asyncio.get_event_loop().run_until_complete(main())
