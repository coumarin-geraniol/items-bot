# Это файл для глобальных переменных
# Глобальные переменные
user_current_order = {}
available_items_title = []
item_quantity = {}
user_current_item = {}  # ключ: user_id, значение: информация о продукте

# Геттеры и сеттеры
def get_user_current_order(user_id):
    return user_current_order.get(user_id, None)

def set_user_current_order(user_id, order):
    user_current_order[user_id] = order

def get_available_items_title():
    return available_items_title

def set_available_items_title(titles):
    global available_items_title
    available_items_title = titles

def get_item_quantity(item_id):
    return item_quantity.get(item_id, 0)

def set_item_quantity(item_id, quantity):
    item_quantity[item_id] = quantity

def get_user_current_item(user_id):
    return user_current_item.get(user_id, None)

def set_user_current_item(user_id, item_info):
    user_current_item[user_id] = item_info

# Пример использования
# set_user_current_order(123, {'item1': 2, 'item2': 3})
# order = get_user_current_order(123)


