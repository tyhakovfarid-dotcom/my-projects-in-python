from datetime import datetime
import os
import random
import json
from game_logic import character

def save_exist():
    if not os.path.exists("saves/"):
        os.makedirs("saves")


def get_token():
    with open('api.json', 'r') as f:
        return json.load(f)["TOKEN"]


def log_write(user_id, log_message):
    if not os.path.exists("logs/"):
        os.makedirs("logs")
    file_path = f"logs/{user_id}.log"
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("--- Лог создан ---\n")
    with open(file_path, "a", encoding="utf-8") as f:
        time_now = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{time_now}] {log_message}\n")


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

#кошка-пингвин: "хозяин ну наконец то ты дописал код"