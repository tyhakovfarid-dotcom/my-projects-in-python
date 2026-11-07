from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import load_or_create_player, save_exist, get_token
from tg_handles import handle_block, handle_attack, handle_battle, handle_casino, handle_sekira, handle_spin, handle_sword, handle_catana, handle_menu, handle_shop, handle_bet_x2, handle_bet_x05, handle_va_bank, handle_stairs


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
        await handle_casino(user_id, query, context, player)
    elif query.data == "shop":
        await handle_shop(user_id, query, context, player)
    elif query.data == "attack":
        await handle_attack(user_id, query, context, player)
    elif query.data == "block":
        await handle_block(user_id, query, context, player)
    elif query.data == "spin":
        await handle_spin(user_id, query, context, player)
    elif query.data == "sekira":
        await handle_sekira(user_id, query, context, player)
    elif query.data == "sword":
        await handle_sword(user_id, query, context, player)
    elif query.data == "catana":
        await handle_catana(user_id, query, context, player)
    elif query.data == "menu":
        await handle_menu(user_id, query, context, player)
    elif query.data == "bet_2x":
        await handle_bet_x2(user_id, query, context, player)
    elif query.data == "bet_0.5x":
        await handle_bet_x05(user_id, query, context, player)
    elif query.data == "va-bank":
        await handle_va_bank(user_id, query, context, player)
    elif query.data in ["stairs", "next_stair", "out"]:
        await handle_stairs(user_id, query, context, player)


def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()

#кошка-пингвин: "хозяин ну наконец то ты дописал код"