from collections import Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
from tg_utils import safe_edit
from database import log_write, save_player, load_or_create_player, save_exist, get_token
from game_logic import character

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


async def handle_battle(user_id, query, context, player):
    log_write(user_id, "игрок начал баттл с монстром")
    player.hp = random.randint(250, 300)
    monster = character('монстер', random.randint(225, 315), 30, 48)
    context.user_data['monster'] = monster
    keyboard = [
        [InlineKeyboardButton("⚔️ Ударить", callback_data="attack")],
        [InlineKeyboardButton("🛡️ Блок", callback_data="block")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        query,
        f"Бой начался! У монстра {monster.hp} HP.",
        reply_markup=reply_markup
    )


async def handle_casino(user_id, query, player):
    keyboard = [
        [InlineKeyboardButton("🎰 спин", callback_data="spin")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        query,
        f"Привет ты в начальном меню казино у тебя {player.balance} монет",
        reply_markup=reply_markup
    )
    log_write(user_id, "игрок зашел в казино")


async def handle_shop(user_id, query, player):
    keyboard = [
        [InlineKeyboardButton("Секира (125): 🪓", callback_data="sekira")],
        [InlineKeyboardButton("Двуручный меч (250): ⚔️", callback_data="sword")],
        [InlineKeyboardButton("Катана (500): 🗡️", callback_data="catana")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        query,
        f"привет ты в магазине оружия ниже будут оружия к покупке, твой баланс {player.balance} монет",
        reply_markup=reply_markup
    )
    log_write(user_id, "игрок зашел в магазин")


async def handle_attack(query, context, player, user_id):
    monster = context.user_data.get('monster')
    result_text = ""
    kish, mish = player.attack(monster)
    result_text += kish + "\n"
    if monster.hp <= 0:
        result_text += "🎉 Ты победил!"
        player.balance += 50
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, result_text, reply_markup=reply_markup)
        save_player(user_id, player)
        log_write(user_id, "игрок выиграл монстра")
        return
    mkish, mmish = monster.attack(player)
    result_text += mkish + "\n"
    if player.hp <= 0:
        result_text += "💀 Ты проиграл..."
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, result_text, reply_markup=reply_markup)
        log_write(user_id, "игрок проиграл монстру")
        return
    keyboard = [
        [InlineKeyboardButton("⚔️ Ударить", callback_data="attack")],
        [InlineKeyboardButton("🛡️ Блок", callback_data="block")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(query, result_text, reply_markup=reply_markup)


async def handle_block(user_id, query, context, player):
    result_text = ""
    monster = context.user_data.get('monster')
    kish, mish = monster.attack(player, is_blocking=True)
    result_text += kish + "\n" + mish + "\n"
    if player.hp <= 0:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, result_text, reply_markup=reply_markup)
        log_write(user_id, "игрок проиграл монстру")
        return


    keyboard = [
        [InlineKeyboardButton("⚔️ Ударить", callback_data="attack")],
        [InlineKeyboardButton("🛡️ Блок", callback_data="block")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(query, result_text, reply_markup=reply_markup)


async def handle_spin(query, player, user_id):
    if player.balance < 10:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "✖️ у вас нету 10 монет на спин, вы можете пойти сразиться с монстром что бы заработать",
            reply_markup=reply_markup
        )
        log_write(user_id, "игроку не хватило денег на спин")
        return

    symbols = ['^', '#', '*', '$', "&"]
    player.balance -= 10
    spin = [random.choice(symbols) for _ in range(4)]
    most = Counter(spin)
    most_common = most.most_common(1)[0][1]

    keyboard = [
        [InlineKeyboardButton("🎰 спин", callback_data="spin")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if most_common == 4:
        player.balance += 160
        await safe_edit(
            query,
            f"{''.join(spin)}\n\n🎉 ДЖЕКПОТ! Вы выиграли 150 монет!",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок выбил джекпот")
    elif most_common == 3:
        player.balance += 35
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nВы выиграли 25 монет!",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок выиграл 25 монет")
    elif most_common == 2:
        player.balance += 5
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nвам вернули половину ставки",
            reply_markup=reply_markup
        )
        log_write(user_id, "игроку вернули половину ставки")
    else:
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nк сожалению ты проиграл",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок проиграл 10 монет")
    save_player(user_id, player)


async def handle_sekira(query, player, user_id):
    if player.balance < 125:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "у вас не хватает денег",
            reply_markup=reply_markup
        )
    elif player.mult_dam >= 1.10:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "вы не можете купить оружие ниже или такое же",
            reply_markup=reply_markup
        )
    else:
        player.balance -= 125
        player.mult_dam = 1.10
        save_player(user_id, player)
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            f"✅ Вы купили секиру! Теперь ваш урон x{player.mult_dam}. Баланс: {player.balance}",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок купил секиру")


async def handle_sword(query, player, user_id):
    if player.balance < 250:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "у вас не хватает денег",
            reply_markup=reply_markup
        )


    elif player.mult_dam >= 1.25:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "вы не можете купить оружие ниже или такое же",
            reply_markup=reply_markup
        )



    else:
        player.balance -= 250
        player.mult_dam = 1.25
        save_player(user_id, player)
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            f"✅ Вы купили двуручный меч! Теперь ваш урон x{player.mult_dam}. Баланс: {player.balance}",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок купил двуручный меч")


async def handle_catana(query, player, user_id):
    if player.balance < 500:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "у вас не хватает денег",
            reply_markup=reply_markup
        )


    elif player.mult_dam == 1.35:
        keyboard = [
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            "вы не можете купить оружие ниже или такое же",
            reply_markup=reply_markup
        )


    else:
        player.balance -= 500
        player.mult_dam = 1.35
        save_player(user_id, player)
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            f"✅ Вы купили катану! Теперь ваш урон x{player.mult_dam}. Баланс: {player.balance}",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок купил катану")


async def handle_menu(query):
    keyboard = [
        [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
        [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        query,
        "Привет! Выбирай действие:",
        reply_markup=reply_markup
    )


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