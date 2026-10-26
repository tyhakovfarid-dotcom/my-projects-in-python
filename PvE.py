import random
import json
import os
class character:
    """бля лучше не трогай без этой хуйни ляжет весь код"""
    def __init__(self,name,hp,min_damage,max_damage):
        self.name=name
        self.hp=hp
        self.min_damage=min_damage
        self.max_damage=max_damage
        self.balance=20
        self.mult_dam = 1
        # типо умножение урона от оружия
    def attack(self, target, is_blocking=False,):
        damage= int(random.randint(self.min_damage,self.max_damage) * self.mult_dam)
        if is_blocking == True:
            damage = int(damage * 0.25)
            print(f'{target.name} заблокировал 75 процентов урона')
        target.hp -= damage
        print(f"{self.name} бьет {target.name} на {damage} урона! У {target.name} осталось {target.hp} HP.")
player = character('герой', random.randint(250, 300), min_damage=35, max_damage=45)
def unsaving(player):
    # ну знаешь это типо сейв я сам не ебу почему оно работает но оно работает, вроде
    while True:
        if not os.path.exists("saves/"):
            os.makedirs("saves")
        t = input("введите название вашего сейва и да .json игра сама добавит от вас требуется только название или выход если его нету")
        if t == "выход":
            return
        file = t+'.json'
        path = "saves/"+file
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                player.balance = data['balance']
                player.mult_dam = data['mult_dam']
                print(f"✅ Сейв '{file}' успешно загружен! Баланс: {player.balance}")
                break
        else:
            print("❌ Сейв с таким названием не найден! посмотрите папку saves")
def saving(player):
    if not os.path.exists("saves/"):
        os.makedirs("saves")
    name = input("введите название для вашего сейва без .json это добавит сама игра")
    file = name+'.json'
    path = "saves/"+file
    data = {
        "balance": player.balance,
        "mult_dam": player.mult_dam,
    }
    with open(path, "w") as f:
        json.dump(data, f)
def battle(player):
    """типо батл с монстром"""
    player.hp = random.randint(250, 300)
    print(f"у вашего героя {player.hp} здоровья")
    monster = character('монстер', random.randint(200, 250), min_damage=20, max_damage=35)
    print(f"у монстра {monster.hp} здоровья")
    while player.hp > 0 and monster.hp > 0:
        player_blocked = False
        x = input('выберите действие (блок/ударить)').strip().lower()
        if x == 'блок':
            print('вы заблокировали удар')
            player_blocked = True
        elif x == 'ударить':
            player.attack(monster)
            print('вы ударили монстра')
        else:
            print('вы замешкались и пропустили ход')
        if monster.hp <= 0:
            print("🎉 Ты победил! тебе было зачислено 50 монет за убитого монстра")
            player.balance += 50
            break
        monster.attack(player, is_blocking=player_blocked)
        print('вас ударил монстр')
        if player.hp <= 0:
            print("💀 Ты проиграл...")
            break
    return player
def casino(player):
    """типа казино"""
    symbols = ['^', '#', '*', '$']
    while player.balance >= 10:
        player.balance -= 10
        s1 = symbols[random.randint(0, 3)]
        s2 = symbols[random.randint(0, 3)]
        s3 = symbols[random.randint(0, 3)]
        print(f'{s1}{s2}{s3}')
        if s1 == s2 and s3 == s2:
            player.balance += 110
            print('поздаравляю это был ДЖЕЕКПОТ теперь на вашем балансе', player.balance, 'монет')
        elif s1 == s2:
            player.balance += 20
            print('поздравляю вы выиграли 10 монет теперь на вашем балансе', player.balance, 'монет')
        elif s2 == s3:
            player.balance += 20
            print('поздравляю вы выиграли 10 монет теперь на вашем балансе', player.balance, 'монет')
        elif s1 == s3:
            player.balance += 20
            print('поздравляю вы выиграли 10 монет теперь на вашем балансе', player.balance, 'монет')
        else:
            print('охх жаль тебя ты проиграл но не бойся еще выиграешь')
        d = input('хотите ли вы продолжить да/нет: ').strip().lower()
        if d == 'нет':
            print('эхх уже уходишь ну давай я тебя всегда жду снова')
            break
        if player.balance == 0:
            print("эхх жаль ты проиграл все но ты можешь еще зайти когда заработаешь")
    return player
def magazine(player):
    """сжалюсь над тобой и сделаю подробнее смотри это магазинчик секира приумножает урон на 1.10 двуручный меч на 1.25 катана на 1.35"""
    print("у вас на балансе", player.balance, "монеток")
    print("секира стоит 125 монеточек она дает усиление в 1.10 раза ")
    print("двуручный меч стоит 250 монеточек он дает усиление в 1.25 раза")
    print("катана стоит 500 монеточек она дает усиление в 1.35 раза")
    weapon = input('введите оружие которое хотите купить 1.секира / 2.двуручный меч / 3.катана')
    if weapon == '1' and player.balance >= 125:
        if player.mult_dam >= 1.10 or player.mult_dam == 1.10:
            print("нет вы не можете купить оружие ниже или такое же")
        else:
            player.balance -= 125
            player.mult_dam = 1.10
            print("вы купили секиру!")
    elif weapon == '2' and player.balance >= 250:
        if player.mult_dam >= 1.25 or player.mult_dam == 1.25:
            print("нет вы не можете купить оружие ниже или такое же")
        else:
            player.balance -= 250
            player.mult_dam = 1.25
            print("вы купили двуручный меч!")
    elif weapon == '3' and player.balance >= 500:
        if player.mult_dam == 1.35:
            print("у вас уже есть катана")
        else:
            player.balance -= 500
            player.mult_dam = 1.35
            print("вы купили катану!")
    else:
        print('а нука вали нищий')
game = input("если у вас есть сейв и выхотите начать с него напишите 1 если у вас его нету или вы хотите начать с нуля напишите 2")
if game == '1':
    unsaving(player)
while True:
    print(f"\n[Баланс: {player.balance} | Множитель урона: x{player.mult_dam}]")
    main = input('введите действие для вашего персонажа 1.убить монстра / 2.сыграть в казино / 3.купить чтото в магазинчике / 4.выход / и да нужно вводить имено цифру действия')
    if main == '1':
        battle(player)
        print(f"Твой баланс после боя: {player.balance}")
    elif main == '2':
        casino(player)
        print(f"Твой баланс после казино: {player.balance}")
    elif main == '3':
        magazine(player)
        print(f"Твой баланс после магазина: {player.balance} ")
    elif main == '4':
        saving(player)
        print("пока")
        break