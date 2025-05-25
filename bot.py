import telebot
import random
from telebot import types

API_TOKEN = '7967291178:AAFSigabpCDo1m2t4VdPfmF8bABCmLK5V4M'
bot = telebot.TeleBot(API_TOKEN)

# Словарь с характеристиками предметов
ITEMS = {
    # Оружие
    "Стальной меч": {"id": 1, "name": "Стальной меч", "type": "weapon", "hp_bonus": 0, "damage_range": (8, 12), "durability": 300, "weight": 4},
    "Огненный кинжал": {"id": 2, "name": "Огненный кинжал", "type": "weapon", "hp_bonus": 0, "damage_range": (5, 9), "durability": 150, "weight": 2},
    "Ледяной топор": {"id": 3, "name": "Ледяной топор", "type": "weapon", "hp_bonus": 5, "damage_range": (10, 14), "durability": 200, "weight": 6},
    "Молниеносный посох": {"id": 4, "name": "Молниеносный посох", "type": "weapon", "hp_bonus": 10, "damage_range": (6, 11), "durability": 180, "weight": 3},
    "Драконий клинок": {"id": 5, "name": "Драконий клинок", "type": "weapon", "hp_bonus": 20, "damage_range": (12, 16), "durability": 400, "weight": 5},

    # Броня
    "Броня стража": {"id": 6, "name": "Броня стража", "type": "armor", "hp_bonus": 25, "damage_reduction": 0.08, "durability": 350, "weight": 6},
    "Броня следопыта": {"id": 7, "name": "Броня следопыта", "type": "armor", "hp_bonus": 10, "damage_reduction": 0.03, "durability": 200, "weight": 3},
    "Огненные доспехи": {"id": 8, "name": "Огненные доспехи", "type": "armor", "hp_bonus": 15, "damage_reduction": 0.05, "durability": 250, "weight": 4},
    "Ледяной панцирь": {"id": 9, "name": "Ледяной панцирь", "type": "armor", "hp_bonus": 20, "damage_reduction": 0.06, "durability": 300, "weight": 5},
    "Драконий доспех": {"id": 10, "name": "Драконий доспех", "type": "armor", "hp_bonus": 40, "damage_reduction": 0.12, "durability": 500, "weight": 7},

    # Зелья
    "Маленькое зелье восстановления": {"id": 11, "name": "Маленькое зелье восстановления", "type": "potion", "hp_bonus": 25, "consumable": True, "weight": 1},
    "Большое зелье восстановления": {"id": 12, "name": "Большое зелье восстановления", "type": "potion", "hp_bonus": 60, "consumable": True, "durability": 200, "weight": 2},
    "Маленькое зелье ярости": {"id": 13, "name": "Маленькое зелье ярости", "type": "potion", "damage_bonus": 5, "consumable": True, "weight": 1},
    "Большое зелье ярости": {"id": 14, "name": "Большое зелье ярости", "type": "potion", "damage_bonus": 8, "consumable": True, "weight": 2},
    "Маленькое зелье каменной кожи": {"id": 15, "name": "Маленькое зелье каменной кожи", "type": "potion", "damage_reduction": 0.05, "consumable": True, "weight": 1},
    "Большое зелье каменной кожи": {"id": 16, "name": "Большое зелье каменной кожи", "type": "potion", "damage_reduction": 0.08, "consumable": True, "weight": 2},

    # Рюкзаки
    "Малый рюкзак": {"id": 17, "name": "Малый рюкзак", "type": "backpack", "capacity_bonus": 10, "weight": 2},
    "Средний рюкзак": {"id": 18, "name": "Средний рюкзак", "type": "backpack", "capacity_bonus": 25, "weight": 4},
    "Большой рюкзак": {"id": 19, "name": "Большой рюкзак", "type": "backpack", "capacity_bonus": 50, "weight": 6}
}

BASE_CAPACITY = 20

# Данные игрока
player = {
    "hp": 100,
    "inventory": [],
    "equipment": {
        "helmet": None,
        "armor": None,
        "boots": None,
        "weapon": None,
        "backpack": None
    },
    "capacity": BASE_CAPACITY
}

# Глобальная переменная для текущего лута
current_loot = []

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton("Инвентарь"),
        types.KeyboardButton("Состояние"),
        types.KeyboardButton("Справочник")
    )
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Используй /loot для поиска предметов.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Инвентарь")
def show_inventory(message):
    # Рассчитываем текущий вес инвентаря
    current_weight = sum(item['weight'] for item in player['inventory'])

    # Проверяем, есть ли у игрока рюкзак
    backpack = player['equipment']['backpack']
    if backpack:
        capacity = BASE_CAPACITY + backpack['capacity_bonus']
    else:
        capacity = BASE_CAPACITY

    # Формируем сообщение об инвентаре
    inventory_message = "🎒 Инвентарь:\n"
    if player['inventory']:
        for item in player['inventory']:
            item_name = item['name']
            if item in player['equipment'].values():
                item_name += " (НАДЕТО)"
            inventory_message += f"- {item_name} (Вес: {item['weight']})\n"
    else:
        inventory_message += "Инвентарь пуст.\n"

    inventory_message += f"\nТекущий вес: {current_weight}/{capacity}"

    # Кнопки для действий с инвентарем
    markup = types.InlineKeyboardMarkup()
    equip_btn = types.InlineKeyboardButton("Надеть", callback_data="equip_item")
    discard_btn = types.InlineKeyboardButton("Выкинуть", callback_data="discard_item")
    markup.add(equip_btn, discard_btn)

    bot.send_message(message.chat.id, inventory_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "equip_item")
def equip_item_prompt(call):
    # Ищем доступные для надевания предметы
    available_items = [item for item in player['inventory'] if item['type'] in player['equipment'] and item not in player['equipment'].values()]

    if available_items:
        markup = types.InlineKeyboardMarkup()
        for item in available_items:
            btn = types.InlineKeyboardButton(item['name'], callback_data=f"equip_{item['name']}")
            markup.add(btn)
        bot.send_message(call.message.chat.id, "Выберите предмет для надевания:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "НЕТ ДОСТУПНЫХ ПРЕДМЕТОВ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("equip_"))
def equip_item(call):
    item_name = call.data.replace("equip_", "")
    item = next((i for i in player['inventory'] if i['name'] == item_name), None)

    if item:
        # Снимаем текущий экипированный предмет того же типа, если он есть
        if player['equipment'][item['type']]:
            unequipped_item = player['equipment'][item['type']]
            player['inventory'].append(unequipped_item)

        # Экипируем новый предмет
        player['equipment'][item['type']] = item
        player['inventory'].remove(item)

        bot.answer_callback_query(call.id, text=f"Ты экипировал: {item['name']}")
    else:
        bot.answer_callback_query(call.id, text="Предмет не найден в инвентаре")

@bot.callback_query_handler(func=lambda call: call.data == "discard_item")
def discard_item_prompt(call):
    # Ищем предметы, которые можно выкинуть (не экипированы)
    discardable_items = [item for item in player['inventory'] if item not in player['equipment'].values()]

    if discardable_items:
        markup = types.InlineKeyboardMarkup()
        for item in discardable_items:
            btn = types.InlineKeyboardButton(item['name'], callback_data=f"discard_{item['name']}")
            markup.add(btn)
        bot.send_message(call.message.chat.id, "Выберите предмет для выкидывания:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "НЕТ ДОСТУПНЫХ ПРЕДМЕТОВ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("discard_"))
def discard_item(call):
    item_name = call.data.replace("discard_", "")
    item = next((i for i in player['inventory'] if i['name'] == item_name), None)

    if item:
        player['inventory'].remove(item)
        bot.answer_callback_query(call.id, text=f"Ты выкинул: {item['name']}")
    else:
        bot.answer_callback_query(call.id, text="Предмет не найден в инвентаре")

@bot.message_handler(func=lambda message: message.text == "Справочник")
def show_guide(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Оружие", callback_data="guide_weapon"),
        types.InlineKeyboardButton("Зелья", callback_data="guide_potions"),
        types.InlineKeyboardButton("Броня", callback_data="guide_armor"),
        types.InlineKeyboardButton("Враги", callback_data="guide_enemies"),
        types.InlineKeyboardButton("Мирные мобы", callback_data="guide_npcs")
    )
    bot.send_message(message.chat.id, "Категории справочника:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "guide_weapon")
def guide_weapon_category(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Стальной меч", callback_data="weapon_1"),
        types.InlineKeyboardButton("Огненный кинжал", callback_data="weapon_2"),
        types.InlineKeyboardButton("Ледяной топор", callback_data="weapon_3"),
        types.InlineKeyboardButton("Молниеносный посох", callback_data="weapon_4"),
        types.InlineKeyboardButton("Драконий клинок", callback_data="weapon_5")
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Оружие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("weapon_"))
def show_weapon_info(call):
    weapon_id = call.data.split("_")[1]
    descriptions = {
        "1": "⚔️ Стальной меч\nНадёжный меч с острым клинком, выкованный из прочной стали. Подходит как для новичков, так и для опытных воинов.\nУрон: 8–12\nПрочность: 300\nВес: 4\nБонус HP: 0",
        "2": "🔥 Огненный кинжал\nЛёгкий и быстрый кинжал, зачарованный огнём. Идеален для быстрых атак и нанесения урона врагам с малой защитой.\nУрон: 5–9\nПрочность: 150\nВес: 2\nБонус HP: 0",
        "3": "🧊 Ледяной топор\nТяжёлое оружие, покрытое инеем. При ударе может временно замедлять врагов.\nУрон: 10–14\nПрочность: 200\nВес: 6\nБонус HP: +5",
        "4": "⚡ Молниеносный посох\nПосох древнего мага, способный вызывать разряд молнии. Отличается высокой скоростью атаки, но требует осторожности.\nУрон: 6–11\nПрочность: 180\nВес: 3\nБонус HP: +10",
        "5": "🐉 Драконий клинок\nЛегендарное оружие, выкованное из чешуи дракона. Великолепно сбалансировано и наносит серьёзный урон.\nУрон: 12–16\nПрочность: 400\nВес: 5\nБонус HP: +20"
    }
    bot.send_message(call.message.chat.id, descriptions.get(weapon_id, "Информация недоступна"))

@bot.callback_query_handler(func=lambda call: call.data == "guide_armor")
def guide_armor_category(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Броня стража", callback_data="armor_1"),
        types.InlineKeyboardButton("Броня следопыта", callback_data="armor_2"),
        types.InlineKeyboardButton("Огненные доспехи", callback_data="armor_3"),
        types.InlineKeyboardButton("Ледяной панцирь", callback_data="armor_4"),
        types.InlineKeyboardButton("Драконий доспех", callback_data="armor_5")
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Броня:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("armor_"))
def show_armor_info(call):
    armor_id = call.data.split("_")[1]
    descriptions = {
        "1": "🛡️ Броня стража\nТяжёлая броня, которую носят городские стражи. Обеспечивает хорошую защиту и увеличивает выносливость бойца.\nБонус HP: +25\nСнижение урона: 0.08\nПрочность: 350\nВес: 6",
        "2": "🌲 Броня следопыта\nЛёгкий комплект из кожи и ткани, созданный для охотников и разведчиков. Позволяет быстро передвигаться и уклоняться от атак.\nБонус HP: +10\nСнижение урона: 0.03\nПрочность: 200\nВес: 3",
        "3": "🔥 Огненные доспехи\nЗакалённая броня, пропитанная магией огня. Часто используется магами боевых школ.\nБонус HP: +15\nСнижение урона: 0.05\nПрочность: 250\nВес: 4",
        "4": "❄️ Ледяной панцирь\nБлестящий комплект из зачарованного льда и стали. Отлично отражает физические атаки и слегка снижает урон от магии.\nБонус HP: +20\nСнижение урона: 0.06\nПрочность: 300\nВес: 5",
        "5": "🐉 Драконий доспех\nЛегендарная броня, созданная из чешуи древнего дракона. Предоставляет исключительную защиту и усиливает жизненные силы владельца.\nБонус HP: +40\nСнижение урона: 0.12\nПрочность: 500\nВес: 7"
    }
    bot.send_message(call.message.chat.id, descriptions.get(armor_id, "Информация недоступна"))

@bot.callback_query_handler(func=lambda call: call.data == "guide_potions")
def guide_potions_category(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Маленькое зелье восстановления", callback_data="potions_1"),
        types.InlineKeyboardButton("Большое зелье восстановления", callback_data="potions_2"),
        types.InlineKeyboardButton("Маленькое зелье ярости", callback_data="potions_3"),
        types.InlineKeyboardButton("Большое зелье ярости", callback_data="potions_4"),
        types.InlineKeyboardButton("Маленькое зелье каменной кожи", callback_data="potions_5"),
        types.InlineKeyboardButton("Большое зелье каменной кожи", callback_data="potions_6")
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Зелья:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("potions_"))
def show_potions_info(call):
    potions_id = call.data.split("_")[1]
    descriptions = {
        "1": "🧪 Маленькое зелье восстановления\nПростое зелье первой помощи, пригодится в экстренной ситуации.Восстанавливает 25 HP при использовании.\nБонус HP: +25\n\nВес: 1",
        "2": "🧪 Большое зелье восстановления\nМощное зелье, быстро возвращающее жизненные силы даже после тяжёлого боя.Восстанавливает 60 HP при использовании.\nБонус HP: +60\nПрочность: 200\nВес: 2",
        "3": "🧪 Маленькое зелье ярости\nВременный прилив ярости усиливает удары, но действует недолго.Увеличивает урон на +5 на 3 удара.\nБонус к урону: +5\nВес: 1",
        "4": "🧪 Большое зелье ярости\nМогущественное зелье для тех, кто хочет пробивать любую защиту.Увеличивает урон на +8 на 5 ударов.\nБонус к урону: +8\nВес: 2",
        "5": "🧪 Маленькое зелье каменной кожи\nОбволакивает кожу защитной магической бронёй, временно снижая получаемый урон.Повышает сопротивление урону на +0.05 на 3 получения урона.\nСнижение урона: +0.05\nВес: 1",
        "6": "🧪 Большое зелье каменной кожи\nЭликсир, превращающий кожу в подобие камня, делает владельца практически неуязвимым на короткое время.Повышает сопротивление урону на +0.08 на 5 получений урона.\nСнижение урона: +0.08\nВес: 2"
    }
    bot.send_message(call.message.chat.id, descriptions.get(potions_id, "Информация недоступна"))

# Переменная для дебаффа
debuff = 0

@bot.message_handler(func=lambda message: message.text == "Состояние")
def show_status(message):
    # Базовые характеристики
    base_hp = 100
    base_damage = 5  # Базовый урон без оружия
    base_damage_reduction = 0.0  # Базовое сопротивление урону

    # Рассчитываем бонусы от экипированных предметов
    hp_bonus = sum(item.get('hp_bonus', 0) for item in player['equipment'].values() if item)
    damage_bonus = 0
    damage_reduction_bonus = 0.0

    for item in player['equipment'].values():
        if item and 'damage_range' in item:
            damage_bonus += sum(item['damage_range']) / 2  # Средний урон
        if item and 'damage_reduction' in item:
            damage_reduction_bonus += item['damage_reduction']

    # Общие характеристики с учетом дебаффа
    total_hp = base_hp + hp_bonus - debuff
    total_damage = base_damage + damage_bonus
    total_damage_reduction = base_damage_reduction + damage_reduction_bonus

    # Формируем сообщение с состоянием
    status_message = (
        f"📊 Состояние персонажа:\n"
        f"💖 Здоровье: {total_hp} HP\n"
        f"⚔️ Урон: {total_damage:.1f}\n"
        f"🛡️ Сопротивление урону: {total_damage_reduction * 100:.1f}%\n"
    )

    bot.send_message(message.chat.id, status_message)

@bot.message_handler(commands=['loot'])
def open_chest_command(message, context=None):
    global current_loot

    # Определяем тип сундука
    chest_type = random.choices(
        ["Маленький сундук", "Средний сундук", "Большой сундук"],
        weights=[0.5, 0.35, 0.15],
        k=1
    )[0]

    # Определяем количество предметов в сундуке
    if chest_type == "Маленький сундук":
        item_count = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
    elif chest_type == "Средний сундук":
        item_count = random.choices([2, 3], weights=[0.7, 0.3], k=1)[0]
    else:  # Большой сундук
        item_count = random.choices([4, 5], weights=[0.7, 0.3], k=1)[0]

    # Выбираем случайные предметы
    loot_items = random.sample(list(ITEMS.values()), item_count)

    # Рассчитываем текущий вес инвентаря
    current_weight = sum(item['weight'] for item in player['inventory'])

    # Проверяем, есть ли у игрока рюкзак
    backpack = player['equipment']['backpack']
    if backpack:
        capacity = BASE_CAPACITY + backpack['capacity_bonus']
    else:
        capacity = BASE_CAPACITY

    # Формируем сообщение о сундуке
    chest_message = f"Вы открыли {chest_type}!\n"
    chest_message += f"Текущий вес: {current_weight}/{capacity}\n"
    chest_message += "В сундуке:\n"

    # Кнопки для предметов в сундуке
    markup = types.InlineKeyboardMarkup()
    for index, item in enumerate(loot_items):
        item_text = f"{item['name']} (Вес: {item['weight']})"
        btn = types.InlineKeyboardButton(f"Взять {item_text}", callback_data=f"take_{index}")
        markup.add(btn)

    # Кнопка для закрытия сундука
    close_btn = types.InlineKeyboardButton("Закрыть сундук", callback_data=f"close_chest_{context}")
    markup.add(close_btn)

    # Сохраняем текущий лут
    current_loot = loot_items

    bot.send_message(message.chat.id, chest_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("take_"))
def take_loot(call):
    global current_loot

    item_index = int(call.data.replace("take_", ""))

    # Ищем предмет в текущем луте
    if 0 <= item_index < len(current_loot):
        item = current_loot[item_index]

        # Проверяем, есть ли место в инвентаре
        current_weight = sum(i['weight'] for i in player['inventory'])
        backpack = player['equipment']['backpack']
        capacity = BASE_CAPACITY + backpack['capacity_bonus'] if backpack else BASE_CAPACITY

        if current_weight + item['weight'] <= capacity:
            player['inventory'].append(item)
            current_loot.pop(item_index)
            bot.answer_callback_query(call.id, text=f"Ты взял: {item['name']}")

            # Обновляем сообщение о сундуке
            update_chest_message(call.message)
        else:
            bot.answer_callback_query(call.id, text="Недостаточно места в инвентаре")
    else:
        bot.answer_callback_query(call.id, text="Предмет не найден в сундуке")

def update_chest_message(message):
    # Рассчитываем текущий вес инвентаря
    current_weight = sum(item['weight'] for item in player['inventory'])

    # Проверяем, есть ли у игрока рюкзак
    backpack = player['equipment']['backpack']
    if backpack:
        capacity = BASE_CAPACITY + backpack['capacity_bonus']
    else:
        capacity = BASE_CAPACITY

    # Формируем сообщение о сундуке
    chest_message = f"Текущий вес: {current_weight}/{capacity}\n"
    chest_message += "В сундуке:\n"

    # Кнопки для предметов в сундуке
    markup = types.InlineKeyboardMarkup()
    for index, item in enumerate(current_loot):
        item_text = f"{item['name']} (Вес: {item['weight']})"
        btn = types.InlineKeyboardButton(f"Взять {item_text}", callback_data=f"take_{index}")
        markup.add(btn)

    # Кнопка для закрытия сундука
    close_btn = types.InlineKeyboardButton("Закрыть сундук", callback_data="close_chest")
    markup.add(close_btn)

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=chest_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("close_chest_"))
def close_chest(call):
    # Получаем контекст из callback_data
    context = call.data.split("_")[2]
    print(context)
    # Формируем сообщение о закрытии сундука
    close_message = (
        "Вы открыли сундук и получили полезные предметы. "
        "Продолжайте свой путь."
    )

    # Кнопка для продолжения квеста
    markup = types.InlineKeyboardMarkup()
    if context == "dark":
        dark_corridor_btn = types.InlineKeyboardButton("Войти в темный коридор", callback_data="enter_dark_corridor")
        markup.add(dark_corridor_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=close_message,
        reply_markup=markup
    )

# НАЧАЛО КВЕСТА.................................................................................................................................................

@bot.message_handler(commands=['quest'])
def start_quest(message):
    # Формируем сообщение о начале квеста
    quest_message = (
        "Вы — молодой воин, который только что завершил обучение в Академии Боевых Искусств. "
        "Ваша задача — доказать свою доблесть и мастерство, пройдя через древние руины, "
        "где, по легендам, скрыт могущественный артефакт, способный изменить судьбу королевства."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    start_btn = types.InlineKeyboardButton("Начать путешествие", callback_data="start_journey")
    flee_btn = types.InlineKeyboardButton("Сбежать", callback_data="flee")
    markup.add(start_btn, flee_btn)

    bot.send_message(message.chat.id, quest_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_journey")
def start_journey(call):
    # Формируем сообщение о начале путешествия
    journey_message = (
        "Вы решили начать путешествие и отправились в древние руины. "
        "Перед вами два пути: налево и направо."
    )

    # Кнопки для выбора пути
    markup = types.InlineKeyboardMarkup()
    left_btn = types.InlineKeyboardButton("Налево", callback_data="go_left")
    right_btn = types.InlineKeyboardButton("Направо", callback_data="go_right")
    markup.add(left_btn, right_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=journey_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "flee")
def flee(call):
    # Формируем сообщение о побеге
    flee_message = (
        "Вы позорно сбежали и поселились в маленьком доме в лесу под другим именем."
    )

    # Кнопка для повторного начала квеста
    markup = types.InlineKeyboardMarkup()
    retry_btn = types.InlineKeyboardButton("Попробовать снова", callback_data="retry_quest")
    markup.add(retry_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=flee_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "retry_quest")
def retry_quest(call):
    # Формируем сообщение о повторном начале квеста
    retry_message = (
        "Вы решили попробовать снова. Вы — молодой воин, который только что завершил обучение в Академии Боевых Искусств. "
        "Ваша задача — доказать свою доблесть и мастерство, пройдя через древние руины, "
        "где, по легендам, скрыт могущественный артефакт, способный изменить судьбу королевства."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    start_btn = types.InlineKeyboardButton("Начать путешествие", callback_data="start_journey")
    flee_btn = types.InlineKeyboardButton("Сбежать", callback_data="flee")
    markup.add(start_btn, flee_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=retry_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "go_left")
def go_left(call):
    # Формируем сообщение о выборе пути налево
    left_message = (
        "Вы выбрали путь налево и наткнулись на спящего волка. "
        "Вы можете сразиться с ним или тихо пройти мимо."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    fight_btn = types.InlineKeyboardButton("Сразиться", callback_data="fight_wolf")
    sneak_btn = types.InlineKeyboardButton("Тихо пройти мимо", callback_data="sneak_past")
    markup.add(fight_btn, sneak_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=left_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "go_right")
def go_right(call):
    # Формируем сообщение о выборе пути направо
    right_message = (
        "Вы выбрали путь направо и увидели сундук. "
        "Вы можете открыть его или пройти мимо в темный коридор."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    open_chest_btn = types.InlineKeyboardButton("Открыть сундук", callback_data="open_chest_dark_corridor")
    continue_btn = types.InlineKeyboardButton("Пройти мимо в темный коридор", callback_data="enter_dark_corridor")
    markup.add(open_chest_btn, continue_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=right_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "fight_wolf")
def fight_wolf(call):
    # Формируем сообщение о сражении с волком
    fight_message = (
        "Ваш горячий разум захотел крови, но вы были слишком слабы и наивны, "
        "бросившись на волка с голыми руками. Он одним прыжком впился зубами вам в шею и перекусил ее. "
        "Волк лег дальше отдыхать, даже не захотев вас съесть, а вы умираете истекая кровью.\n\n"
        "Вы можете совершить еще одну попытку этого опасного путешествия."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    retry_btn = types.InlineKeyboardButton("Начать сначала", callback_data="retry_quest")
    end_btn = types.InlineKeyboardButton("Завершить квест", callback_data="end_quest")
    markup.add(retry_btn, end_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=fight_message,
        reply_markup=markup
    )



@bot.callback_query_handler(func=lambda call: call.data == "open_chest_dark_corridor")
def open_chest_dark_corridor(call):
    # Вызываем функцию открытия сундука с контекстом
    open_chest_command(call.message, context="dark")



@bot.callback_query_handler(func=lambda call: call.data == "enter_dark_corridor")
def enter_dark_corridor(call):
    # Формируем сообщение о входе в темный коридор
    dark_corridor_message = (
        "Вы вошли в темный коридор. "
        "Справа по стене вы нащупали факел, зажечь его, враги могут увидеть свет?"
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    light_torch_btn = types.InlineKeyboardButton("Зажечь факел", callback_data="light_torch")
    go_in_darkness_btn = types.InlineKeyboardButton("Идти в темноте", callback_data="go_in_darkness")
    markup.add(light_torch_btn, go_in_darkness_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=dark_corridor_message,
        reply_markup=markup
    )



@bot.callback_query_handler(func=lambda call: call.data == "go_in_darkness")
def go_in_darkness(call):
    global debuff

    # Уменьшаем здоровье игрока
    debuff = 10

    # Формируем сообщение о входе в темноту
    go_in_darkness_message = (
        "Вы продолжили свое путешествие по коридору в темноте и попали в ловушку, "
        "вы получили легкую рану и потеряли 10 ХП. Вы в силах идти дальше, но вы слабы."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    rest_btn = types.InlineKeyboardButton("Лечь отдохнуть", callback_data="rest")
    continue_btn = types.InlineKeyboardButton("Пойти дальше по коридору", callback_data="continue_corridor")
    markup.add(rest_btn, continue_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=go_in_darkness_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "rest")
def rest(call):
    # Формируем сообщение об отдыхе
    rest_message = (
        "Вы без сил провалились в сон и замерзли насмерть, "
        "обидная смерть для героя, но может повезет в следующий раз."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    retry_btn = types.InlineKeyboardButton("Попробовать снова", callback_data="retry_quest")
    end_btn = types.InlineKeyboardButton("Закончить квест", callback_data="end_quest")
    markup.add(retry_btn, end_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=rest_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "continue_corridor")
def continue_corridor(call):
    # Формируем сообщение о продолжении пути по коридору
    continue_corridor_message = (
        "Вы продолжаете свой путь по коридору."
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=continue_corridor_message
    )

@bot.callback_query_handler(func=lambda call: call.data == "end_quest")
def end_quest(call):
    # Формируем сообщение о завершении квеста
    end_message = (
        "Будем ждать тебя \"герой\" снова."
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=end_message
    )

@bot.callback_query_handler(func=lambda call: call.data == "light_torch")
def light_torch(call):
    # Формируем сообщение о зажигании факела
    light_torch_message = (
        "Зажечь факел было хорошей идеей, вы увидели ловушку, обойти ее не получится, но перепрыгнуть..."
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    jump_btn = types.InlineKeyboardButton("Перепрыгнуть", callback_data="jump_trap")
    go_left_btn = types.InlineKeyboardButton("Вернуться и пойти налево", callback_data="go_left")
    markup.add(jump_btn, go_left_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=light_torch_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "jump_trap")
def jump_trap(call):
    global debuff

    # Определяем успех перепрыгивания ловушки
    success = random.choices([True, False], weights=[0.5, 0.5], k=1)[0]

    if success:
        # Формируем сообщение об успешном перепрыгивании ловушки
        jump_success_message = (
            "Еще бы чуть-чуть и вы не допрыгнули, можно выдохнуть и продолжить путь."
        )

        # Кнопка для продолжения пути
        markup = types.InlineKeyboardMarkup()
        continue_btn = types.InlineKeyboardButton("Продвигаться по коридору", callback_data="continue_corridor")
        markup.add(continue_btn)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=jump_success_message,
            reply_markup=markup
        )
    else:
        # Уменьшаем здоровье игрока
        debuff = 5

        # Формируем сообщение о неудачном перепрыгивании ловушки
        jump_failure_message = (
            f"Вы не рассчитали свои силы и угодили в ловушку, получив легкую рану (-5 ХП). "
            "Но вы можете продолжать путь."
        )

        # Кнопка для продолжения пути
        markup = types.InlineKeyboardMarkup()
        continue_btn = types.InlineKeyboardButton("Продвигаться по коридору", callback_data="continue_corridor")
        markup.add(continue_btn)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=jump_failure_message,
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "continue_corridor")
def continue_corridor(call):
    global debuff

    # Обнуляем дебафф
    debuff = 0

    # Формируем сообщение о продолжении пути по коридору
    continue_corridor_message = (
        "Вы продолжаете свой путь по коридору."
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=continue_corridor_message
    )

@bot.callback_query_handler(func=lambda call: call.data == "sneak_past")
def sneak_past(call):
    # Формируем сообщение о входе в тронный зал
    sneak_message = (
        "Вы тихо прошли мимо волка и вошли в огромный тронный зал. "
        "На троне сидит старик в черном одеянии. Он говорит: "
        "\"Я ждал тебя, молодой воин. Ты должен помочь мне.\""
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    talk_btn = types.InlineKeyboardButton("Подойти и поговорить с ним", callback_data="talk_to_old_man")
    door_btn = types.InlineKeyboardButton("Пройти в дверь слева от него", callback_data="enter_door")
    markup.add(talk_btn, door_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=sneak_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "talk_to_old_man")
def talk_to_old_man(call):
    # Формируем сообщение о разговоре со старцем
    talk_message = (
        "\"Я был когда-то молод, как ты, и искал приключения. В этом месте я столкнулся с небывалой силой. "
        "С драконом, который дышит огнем и плюется лавой. Мне почти удалось победить его, "
        "но мой меч застрял в его твердой, как камень, чешуе. Мне пришли на помощь мои братья по оружию, "
        "я был весь избит, они спасли меня и отнесли к лекарю в ближайшую деревню. "
        "Мои раны остались со мной на всю жизнь. Мои дни сочтены, но я не могу умереть со спокойной душой "
        "без моего оружия, это позор для воина. Помоги старцу, принеси мне мое оружие.\""
    )

    # Кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    accept_btn = types.InlineKeyboardButton("Принять просьбу", callback_data="accept_request")
    refuse_btn = types.InlineKeyboardButton("Отказать", callback_data="refuse_request")
    markup.add(accept_btn, refuse_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=talk_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "accept_request")
def accept_request(call):
    # Формируем сообщение о принятии просьбы
    accept_message = (
        "Вы благородный воин и принимаете просьбу старца, он указывает вам на дверь слева от него."
    )

    # Кнопка для входа в дверь
    markup = types.InlineKeyboardMarkup()
    enter_door_btn = types.InlineKeyboardButton("Войти в дверь", callback_data="enter_door")
    markup.add(enter_door_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=accept_message,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "refuse_request")
def refuse_request(call):
    global debuff

    # Уменьшаем здоровье игрока
    debuff = 20

    # Формируем сообщение об отказе
    refuse_message = (
        "Вы отказали старцу, он в прошлом учился в Академии чародеев. "
        "Он вас проклинает, и вы теряете 20 ХП.ПРОДОЛЖЕНИЕ СЛЕДУЕТ"
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=refuse_message
    )

@bot.callback_query_handler(func=lambda call: call.data == "enter_door")
def enter_door(call):
    # Формируем сообщение о входе в дверь
    enter_door_message = (
        "Вы вошли в дверь и слышите истовый рев дракона, "
        "по вашему телу пробегает дрожь. ПРОДОЛЖЕНИЕ СЛЕДУЕТ."
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=enter_door_message
    )

bot.polling()

