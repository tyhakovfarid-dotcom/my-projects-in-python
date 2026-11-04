from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import load_or_create_player, save_exist, get_token
from tg_handles import handle_block, handle_attack, handle_battle, handle_casino, handle_sekira, handle_spin, handle_sword, handle_catana, handle_menu, handle_shop


save_exist()
token = get_token()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
        [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбирай действие:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if 'player' not in context.user_data:
        context.user_data['player'] = load_or_create_player(user_id)
    player = context.user_data['player']

    if query.data == "battle":
        await handle_battle(user_id, query, context, player)
    elif query.data == "casino":
        await handle_casino(user_id, query, player)
    elif query.data == "shop":
        await handle_shop(user_id, query, player)
    elif query.data == "attack":
        await handle_attack(query, context, player, user_id)
    elif query.data == "block":
        await handle_block(user_id, query, context, player)
    elif query.data == "spin":
        await handle_spin(query, player, user_id)
    elif query.data == "sekira":
        await handle_sekira(query, player, user_id)
    elif query.data == "sword":
        await handle_sword(query, player, user_id)
    elif query.data == "catana":
        await handle_catana(query, player, user_id)
    elif query.data == "menu":
        await handle_menu(query)


def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()