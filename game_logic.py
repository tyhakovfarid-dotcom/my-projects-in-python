import random

class character:
    """лучше не трогать без этой херни ляжет pve_bot и pve"""
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

#кошка-пингвин: "хозяин ну наконец то ты дописал код"