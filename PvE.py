from collections import Counter
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
        t = input("введите название вашего сейва и да .json игра сама добавит от вас требуется только название или выход если его нету: ")
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
                with open("logs/log.log", "a", encoding="utf-8") as f:
                    f.write(f"\n игрок загрузил сейв {file}")
                break
        else:
            print("❌ Сейв с таким названием не найден! посмотрите папку saves")
def saving(player):
    if not os.path.exists("saves/"):
        os.makedirs("saves")
    name = input("введите название для вашего сейва без .json это добавит сама игра: ")
    file = name+'.json'
    path = "saves/"+file
    data = {
        "balance": player.balance,
        "mult_dam": player.mult_dam,
    }
    with open(path, "w") as f:
        json.dump(data, f)
    with open("logs/log.log",  "a", encoding="utf-8") as f:
        f.write(f"\n игрок сделал сейв {file}")
def battle(player):
    """типо батл с монстром"""
    with open("logs/log.log", "a", encoding="utf-8") as f:
        f.write(f"\n игрок зашел в баттл с монстром")
    player.hp = random.randint(250, 300)
    print(f"у вашего героя {player.hp} здоровья")
    monster = character('монстер', random.randint(200, 250), min_damage=20, max_damage=35)
    print(f"у монстра {monster.hp} здоровья")
    while player.hp > 0 and monster.hp > 0:
        player_blocked = False
        x = input('выберите действие (блок/ударить): ').strip().lower()
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
            with open("logs/log.log", "a", encoding="utf-8") as f:
                f.write(f"\n игрок выиграл монстра")
            break
        monster.attack(player, is_blocking=player_blocked)
        print('вас ударил монстр')
        if player.hp <= 0:
            print("💀 Ты проиграл...")
            with open("logs/log.log", "a", encoding="utf-8") as f:
                f.write(f"\n игрок проиграл монстру")
            break
    return player
def casino(player):
    """типа казино"""
    with open("logs/log.log", "a", encoding="utf-8") as f:
        f.write(f"\n игрок начал игру в казино")
    symbols = ['^', '#', '*', '$', "&"]
    i = player.balance
    while player.balance >= 10:
        player.balance -= 10
        spin = [random.choice(symbols) for _ in range(4)]
        print(''.join(spin))
        most = Counter(spin)
        most_common = most.most_common(1)[0][1]
        if most_common == 4:
            player.balance += 160
            print('🎉 ДЖЕКПОТ! Вы выиграли 150 монет!')
        elif most_common == 3:
            player.balance += 35
            print('вы выиграли 25 монет')
        elif most_common == 2:
            player.balance += 5
            print("вам была возвращена половина ставки")
        else:
            print('охх жаль тебя ты проиграл но не бойся еще выиграешь')
        g = input('хотите ли вы продолжить 1.да 2.нет: ')
        if player.balance == 0 or g == "2":
            print("эхх жаль ты можешь еще зайти когда заработаешь")
            v = i - player.balance
            with open("logs/log.log", "a", encoding="utf-8") as f:
                if v > 0:
                    f.write(f"\n игрок закончил игру в казино и проиграл {v} монет")
                elif v < 0:
                    f.write(f"\n игрок закончил игру в казино и выиграл {-v} монет")
                else:
                    f.write(f"\n игрок закончил игру в казино и остался при своих")
            break
    return player
def magazine(player):
    """сжалюсь над тобой и сделаю подробнее смотри это магазинчик секира приумножает урон на 1.10 двуручный меч на 1.25 катана на 1.35"""
    print("у вас на балансе", player.balance, "монеток")
    print("секира стоит 125 монеточек она дает усиление в 1.10 раза ")
    print("двуручный меч стоит 250 монеточек он дает усиление в 1.25 раза")
    print("катана стоит 500 монеточек она дает усиление в 1.35 раза")
    weapon = input('введите оружие которое хотите купить 1.секира / 2.двуручный меч / 3.катана: ')
    if weapon == '1' and player.balance >= 125:
        if player.mult_dam >= 1.10:
            print("нет вы не можете купить оружие ниже или такое же")
        else:
            player.balance -= 125
            player.mult_dam = 1.10
            print("вы купили секиру!")
            with open("logs/log.log", "a", encoding="utf-8") as f:
                f.write(f"\n игрок купил секиру")
    elif weapon == '2' and player.balance >= 250:
        if player.mult_dam >= 1.25:
            print("нет вы не можете купить оружие ниже или такое же")
        else:
            player.balance -= 250
            player.mult_dam = 1.25
            print("вы купили двуручный меч!")
            with open("logs/log.log", "a", encoding="utf-8") as f:
                f.write(f"\n игрок купил двуручный меч")
    elif weapon == '3' and player.balance >= 500:
        if player.mult_dam == 1.35:
            print("у вас уже есть катана")
        else:
            player.balance -= 500
            player.mult_dam = 1.35
            print("вы купили катану!")
            with open("logs/log.log", "a", encoding="utf-8") as f:
                f.write(f"\n игрок купил катану")
    else:
        print('а нука вали нищий')
def log():
    if not os.path.exists("logs/"):
        os.makedirs("logs")
    if not os.path.exists("logs/log.log"):
        with open("logs/log.log", "w", encoding="utf-8") as f:
            f.write("лог создан")
log()
game = input("если у вас есть сейв и выхотите начать с него напишите 1 если у вас его нету или вы хотите начать с нуля напишите 2: ")
if game == '1':
    unsaving(player)
while True:
    print(f"\n[Баланс: {player.balance} | Множитель урона: x{player.mult_dam}]")
    main = input('введите действие для вашего персонажа 1.убить монстра / 2.сыграть в казино / 3.купить чтото в магазинчике / 4.выход: ')
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