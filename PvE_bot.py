from collections import Counter
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import os

if not os.path.exists("saves/"):
    os.makedirs("saves")

# Загружаем токен
with open('api.json', 'r') as f:
    token = json.load(f)["TOKEN"]


async def safe_edit(query, text, reply_markup=None):
    """edit_message_text с игнором 'Message is not modified'."""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" in str(e):
            pass  # Игнорируем, если сообщение не изменилось
        else:
            raise e
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
        [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбирай действие:", reply_markup=reply_markup)


class character:
    """бля лучше не трогай без этой хуйни ляжет весь код"""
    def __init__(self, name, hp, min_damage, max_damage):
        self.name = name
        self.hp = hp
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.balance = 20
        self.mult_dam = 1
        # типо умножение урона от оружия

    def attack(self, target, is_blocking=False):
        mish = ""
        damage = int(random.randint(self.min_damage, self.max_damage) * self.mult_dam)
        if is_blocking == True:
            damage = int(damage * 0.25)
            mish = f'{target.name} заблокировал 75 процентов урона'
        target.hp -= damage
        if target.hp < 0:
            target.hp = 0
        kish = f"{self.name} бьет {target.name} на {damage} урона! У {target.name} осталось {target.hp} HP."
        return kish, mish


def save_player(user_id, player):
    data = {
        "balance": player.balance,
        "mult_dam": player.mult_dam,
    }
    with open(f"saves/{user_id}.json", "w") as f:
        json.dump(data, f)


def load_or_create_player(user_id):
    file_path = f"saves/{user_id}.json"
    player = character('герой', random.randint(250, 300), 35, 45)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        player.balance = data["balance"]
        player.mult_dam = data["mult_dam"]
    return player


async def handle_battle(query, context, player):
    player.hp = random.randint(250, 300)
    monster = character('монстер', random.randint(225, 325), 35, 52)
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


async def handle_casino(query, player):
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


async def handle_shop(query, player):
    keyboard = [
        [InlineKeyboardButton("Секира (125): 🪓", callback_data="sekira")],
        [InlineKeyboardButton("Двуручный меч (250): ⚔️", callback_data="sword")],
        [InlineKeyboardButton("Катана (500): 🗡️", callback_data="catana")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        query,
        f"привет ты в магазине оружия ниже будут оружия к покупке",
        reply_markup=reply_markup
    )


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
        return
    keyboard = [
        [InlineKeyboardButton("⚔️ Ударить", callback_data="attack")],
        [InlineKeyboardButton("🛡️ Блок", callback_data="block")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(query, result_text, reply_markup=reply_markup)


async def handle_block(query, context, player):
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
    elif most_common == 3:
        player.balance += 35
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nВы выиграли 25 монет!",
            reply_markup=reply_markup
        )
    elif most_common == 2:
        player.balance += 5
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nвам вернули половину ставки",
            reply_markup=reply_markup
        )
    else:
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nк сожалению ты проиграл",
            reply_markup=reply_markup
        )

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
        await handle_battle(query, context, player)
    elif query.data == "casino":
        await handle_casino(query, player)
    elif query.data == "shop":
        await handle_shop(query, player)
    elif query.data == "attack":
        await handle_attack(query, context, player, user_id)
    elif query.data == "block":
        await handle_block(query, context, player)
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