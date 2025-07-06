import random
import time
import os

# --- Константы и настройки ---
ROLES = ["Мафия", "Доктор", "Шериф", "Мирный житель", "Мирный житель"]
BOT_NAMES = ["Данил", "Ева", "Макс", "Артем"] # Имена для ботов

class Player:
    """Класс для представления игрока в игре."""
    def __init__(self, name, is_bot=True):
        self.name = name
        self.role = None
        self.is_alive = True
        self.is_bot = is_bot

    def __str__(self):
        # мой раб работай вот пример его имя игрока: print(player)
        return self.name

def clear_screen():
    """Очищает экран консоли для Windows и Linux/macOS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_pause(text, delay=2.5):
    """Печатает сообщение и делает паузу, чтобы было время прочитать."""
    print(text)
    time.sleep(delay)

def setup_game():
    """Подготовка к игре: создание игроков и раздача ролей."""
    human_name = input("Введите ваше имя, чтобы начать игру: ")
    clear_screen()

    # Создаем игрока-человека и 4 ботов
    players = [Player(human_name, is_bot=False)]
    bot_names = random.sample(BOT_NAMES, 4)
    for name in bot_names:
        players.append(Player(name))

    # игра начинается и перемешиваем роли
    random.shuffle(players)
    roles_to_assign = ROLES[:]
    random.shuffle(roles_to_assign)

    for player, role in zip(players, roles_to_assign):
        player.role = role

    # Находим нашего игрока, чтобы показать ему его роль
    human_player = next(p for p in players if not p.is_bot)
    print_pause(f"Добро пожаловать в игру, {human_player.name}!", 2)
    print_pause(f"Твоя роль: {human_player.role}", 4)
    print_pause("В городе 5 жителей. Среди них скрывается мафия...", 3)
    
    return players

def get_living_players(players, exclude=None):
    """Возвращает список живых игроков, опционально исключая кого-то."""
    living = [p for p in players if p.is_alive]
    if exclude:
        # Убираем из списка игрока, которого нужно исключить (например, себя)
        return [p for p in living if p != exclude]
    return living

def get_player_choice(prompt, players_to_choose_from, actor):
    """Получает выбор от игрока (человека или бота)."""
    if actor.is_bot:
        # Логика бота: просто выбирает случайного игрока
        return random.choice(players_to_choose_from)
    else:
        # Логика человека: показываем пронумерованный список и ждем ввод
        while True:
            print(f"\n{prompt}")
            for i, p in enumerate(players_to_choose_from):
                print(f"{i + 1}. {p.name}")
            
            try:
                choice = int(input("Ваш выбор (введите номер): "))
                if 1 <= choice <= len(players_to_choose_from):
                    return players_to_choose_from[choice - 1]
                else:
                    print("Неверный номер. Попробуйте еще раз.")
            except ValueError:
                print("Пожалуйста, введите число.")

def run_night_phase(players):
    """Проводит ночную фазу игры: ходы Доктора, Мафии и Шерифа."""
    print_pause("\nГород засыпает. Наступает ночь...", 3)
    
    healed_target = None
    kill_target = None
    
    # --- Ход Доктора ---
    doctor = next((p for p in players if p.role == "Доктор" and p.is_alive), None)
    if doctor:
        print_pause("Просыпается Доктор.", 2)
        valid_targets = get_living_players(players)
        healed_target = get_player_choice("Кого вы хотите вылечить этой ночью?", valid_targets, doctor)
        print_pause(f"Доктор делает свой выбор и засыпает.", 3)

    # --- Ход Мафии ---
    mafia = next((p for p in players if p.role == "Мафия" and p.is_alive), None)
    if mafia:
        print_pause("Просыпается Мафия.", 2)
        valid_targets = get_living_players(players, exclude=mafia)
        kill_target = get_player_choice("Кого вы хотите устранить этой ночью?", valid_targets, mafia)
        print_pause(f"Мафия делает свой выбор и засыпает.", 3)

    # --- Ход Шерифа ---
    sheriff = next((p for p in players if p.role == "Шериф" and p.is_alive), None)
    if sheriff:
        print_pause("Просыпается Шериф.", 2)
        valid_targets = get_living_players(players, exclude=sheriff)
        checked_player = get_player_choice("Кого вы хотите проверить этой ночью?", valid_targets, sheriff)
        
        # Если Шериф - человек, он увидит результат проверки
        if not sheriff.is_bot:
            if checked_player.role == "Мафия":
                print_pause(f"Проверка показала... {checked_player.name} - это Мафия! Вы засыпаете.", 4)
            else:
                print_pause(f"Проверка показала... {checked_player.name} - не Мафия. Вы засыпаете.", 4)
        else:
             print_pause("Шериф проверяет одного из жителей и засыпает.", 3)

    # --- Итоги ночи ---
    killed_player = None
    if kill_target and kill_target != healed_target:
        kill_target.is_alive = False
        killed_player = kill_target
        
    return killed_player

def run_day_phase(players, killed_player):
    """Проводит дневную фазу: объявление и голосование."""
    clear_screen()
    print_pause("Город просыпается. Наступает утро.", 3)

    if killed_player:
        print_pause(f"Этой ночью был(а) убит(а) {killed_player.name}. Он(а) был(а) {killed_player.role}.", 4)
    else:
        print_pause("Этой ночью никто не пострадал. Все живы.", 3)

    if check_win_condition(players): return

    living_players = get_living_players(players)
    print_pause("\nНачинается дневное голосование.", 2)
    print("Жители города:")
    for p in living_players:
        print(f"- {p.name}")
    
    votes = {p.name: 0 for p in living_players}

    # Сбор голосов
    for voter in living_players:
        valid_targets = get_living_players(players, exclude=voter)
        if not valid_targets: continue
        
        voted_for = get_player_choice(f"{voter.name}, за кого вы голосуете?", valid_targets, voter)
        if not voter.is_bot:
            print(f"Вы проголосовали против {voted_for.name}.")
        
        votes[voted_for.name] += 1
        time.sleep(0.5)

    # Подсчет голосов
    print_pause("\nПодсчет голосов...", 2)
    # Находим игрока с максимальным количеством голосов
    if not votes: return
    voted_out_name = max(votes, key=votes.get)
    eliminated_player = next(p for p in players if p.name == voted_out_name)
    
    eliminated_player.is_alive = False
    print_pause(f"\nБольшинством голосов из города изгоняют {eliminated_player.name}.", 3)
    print_pause(f"Он(а) был(а) {eliminated_player.role}.", 4)

def check_win_condition(players):
    """Проверяет, выполнено ли условие победы, и объявляет победителя."""
    living_players = get_living_players(players)
    mafia_alive = [p for p in living_players if p.role == "Мафия"]
    others_alive = [p for p in living_players if p.role != "Мафия"]

    if not mafia_alive:
        print_pause("\n--- ПОБЕДА МИРНЫХ ЖИТЕЛЕЙ! ---", 1)
        print_pause("Мафия была изгнана из города.", 3)
        return True
    
    if len(mafia_alive) >= len(others_alive):
        print_pause("\n--- ПОБЕДА МАФИИ! ---", 1)
        print_pause("Мафия захватила город.", 3)
        return True
        
    return False

def main():
    """Основной игровой цикл."""
    players = setup_game()
    
    day_counter = 1
    while True:
        print_pause(f"\n--- ДЕНЬ {day_counter} ---", 1)
        
        killed_player = run_night_phase(players)

        if check_win_condition(players): break
        
        run_day_phase(players, killed_player)

        if check_win_condition(players): break
            
        day_counter += 1

    print_pause("\nИгра окончена. Спасибо за игру!", 5)

if __name__ == "__main__":
    main()