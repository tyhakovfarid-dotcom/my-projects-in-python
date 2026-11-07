import random
from collections import Counter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import log_write, save_player
from game_logic import character
from tg_utils import safe_edit


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

async def handle_casino(user_id, query, context, player):
    total_bet = context.user_data.get('bet', 10)
    keyboard = [
        [InlineKeyboardButton("🎰 спин", callback_data="spin"),
         InlineKeyboardButton("👣 Шаги", callback_data="stairs")],
        [InlineKeyboardButton("ставка 2х", callback_data="bet_2x"), InlineKeyboardButton("ставка 0.5х", callback_data="bet_0.5x")],
        [InlineKeyboardButton("ставка ва-банк", callback_data="va-bank")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        query,
        f"Привет ты в начальном меню казино у тебя {player.balance} монет.\nТекущая ставка: {total_bet}",
        reply_markup=reply_markup
    )
    log_write(user_id, "игрок зашел в казино")

async def handle_shop(user_id, query, context, player):
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

async def handle_attack(user_id, query, context, player):
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

async def handle_spin(user_id, query, context, player):
    total_bet = context.user_data.get('bet', 10)
    if player.balance < total_bet:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(
            query,
            f"✖️ у вас нету {total_bet} монет на спин, вы можете пойти сразиться с монстром что бы заработать",
            reply_markup=reply_markup
        )
        log_write(user_id, "игроку не хватило денег на спин")
        return

    symbols = ['^', '#', '*', '$', "&"]
    player.balance -= total_bet
    spin = [random.choice(symbols) for _ in range(4)]
    most = Counter(spin)
    most_common = most.most_common(1)[0][1]

    keyboard = [
        [InlineKeyboardButton("🎰 спин", callback_data="spin")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if most_common == 4:
        player.balance += int(total_bet * 3)
        await safe_edit(
            query,
            f"{''.join(spin)}\n\n🎉 ДЖЕКПОТ! Вы выиграли 3х!",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок выбил джекпот")

    elif most_common == 3:
        player.balance += int(total_bet * 1.5)
        await safe_edit(
            query,
            f"{''.join(spin)}\n\nВы выиграли 1.5х!",
            reply_markup=reply_markup
        )
        log_write(user_id, "игрок выбил 1.5х")

    elif most_common == 2:
        player.balance += int(total_bet * 0.5)
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
        log_write(user_id, f"игрок проиграл {total_bet} монет")
    save_player(user_id, player)

async def handle_sekira(user_id, query, context, player):
    if player.balance < 125:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, "у вас не хватает денег", reply_markup=reply_markup)

    elif player.mult_dam >= 1.10:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, "вы не можете купить оружие ниже или такое же", reply_markup=reply_markup)

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
        await safe_edit(query, f"✅ Вы купили секиру! Теперь ваш урон x{player.mult_dam}. Баланс: {player.balance}", reply_markup=reply_markup)
        log_write(user_id, "игрок купил секиру")

async def handle_sword(user_id, query, context, player):
    if player.balance < 250:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, "у вас не хватает денег", reply_markup=reply_markup)

    elif player.mult_dam >= 1.25:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, "вы не можете купить оружие ниже или такое же", reply_markup=reply_markup)

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
        await safe_edit(query, f"✅ Вы купили двуручный меч! Теперь ваш урон x{player.mult_dam}. Баланс: {player.balance}", reply_markup=reply_markup)
        log_write(user_id, "игрок купил двуручный меч")

async def handle_catana(user_id, query, context, player):
    if player.balance < 500:
        keyboard = [
            [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, "у вас не хватает денег", reply_markup=reply_markup)

    elif player.mult_dam == 1.35:
        keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(query, "вы не можете купить оружие ниже или такое же", reply_markup=reply_markup)

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
        await safe_edit(query, f"✅ Вы купили катану! Теперь ваш урон x{player.mult_dam}. Баланс: {player.balance}", reply_markup=reply_markup)
        log_write(user_id, "игрок купил катану")

async def handle_menu(user_id, query, context, player):
    keyboard = [
        [InlineKeyboardButton("⚔️ В бой", callback_data="battle")],
        [InlineKeyboardButton("🎰 Казино", callback_data="casino")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(query, "Привет! Выбирай действие:", reply_markup=reply_markup)

async def handle_bet_x2(user_id, query, context, player):
    total_bet = context.user_data.get('bet', 10) * 2
    if total_bet > player.balance:
        await query.answer("Вам не хватает денег на это действие", show_alert=True)
    else:
        context.user_data['bet'] = total_bet
        await handle_casino(user_id, query, context, player)

async def handle_bet_x05(user_id, query, context, player):
    total_bet = int(context.user_data.get('bet', 10) * 0.5)
    if total_bet > player.balance:
        await query.answer("Вам не хватает денег на это действие", show_alert=True)
    elif total_bet < 1:
        await query.answer("Это ниже 1 ставку делать нельзя", show_alert=True)
    else:
        context.user_data['bet'] = total_bet
        await handle_casino(user_id, query, context, player)

async def handle_va_bank(user_id, query, context, player):
    if player.balance < 1:
        await query.answer("У тебя нет денег даже на ва-банк!", show_alert=True)
    else:
        context.user_data['bet'] = player.balance
        await handle_casino(user_id, query, context, player)


async def handle_stairs(user_id, query, context, player):
    total_bet = context.user_data.get('bet', 10)

    # СТАРТ ИГРЫ
    if query.data == "stairs":
        if player.balance < total_bet:
            await query.answer("Не хватает денег на ставку!", show_alert=True)
            return

        player.balance -= total_bet
        context.user_data['stair'] = 1
        context.user_data['stair_mult'] = 1.0
        context.user_data['stair_chance'] = 20
        save_player(user_id, player)
        log_write(user_id, "игрок начал играть в шаги")

    elif query.data == "next_stair":
        if 'stair' not in context.user_data:
            await query.answer("Начни игру заново!", show_alert=True)
            return

        rand = random.randint(1, 100)
        if rand <= context.user_data['stair_chance']:
            context.user_data.pop('stair', None)
            context.user_data.pop('stair_mult', None)
            context.user_data.pop('stair_chance', None)
            log_write(user_id, f"проиграл в шаги (-{total_bet})")
            save_player(user_id, player)

            keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
            await safe_edit(
                query,
                f"Проиграл. Минус {total_bet} монет.\nБаланс: {player.balance}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        context.user_data['stair'] += 1
        context.user_data['stair_mult'] += 0.08
        context.user_data['stair_chance'] += 8

    elif query.data == "out":
        if 'stair' not in context.user_data:
            await query.answer("Игра не активна!", show_alert=True)
            return

        win = int(total_bet * context.user_data['stair_mult'])
        player.balance += win
        context.user_data.pop('stair', None)
        context.user_data.pop('stair_mult', None)
        context.user_data.pop('stair_chance', None)
        save_player(user_id, player)
        log_write(user_id, f"забрал в шаги (+{win})")

        keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
        await safe_edit(
            query,
            f"Забрал {win} монет. Баланс: {player.balance}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ОТРИСОВКА (единая для старта и после удачного шага)
    step = context.user_data['stair']
    mult = context.user_data['stair_mult']
    chance = context.user_data['stair_chance']
    win = int(total_bet * mult)

    keyboard = [
        [InlineKeyboardButton("Дальше", callback_data="next_stair")],
        [InlineKeyboardButton(f"Забрать {win}", callback_data="out")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ]
    await safe_edit(
        query,
        f"Шаг {step}. На кону: {win}.\nСледующий шанс слить: {chance}%.\nБаланс: {player.balance}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

#кошка-пингвин: "хозяин ну наконец то ты дописал код"