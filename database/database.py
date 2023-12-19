import sqlite3 as sq


async def db_start():
    global db, cur
    db = sq.connect('items_bot.db')
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            tg_id INTEGER,
            username TEXT UNIQUE, 
            'password' TEXT,
            tg_username TEXT,
            type INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            'code' TEXT UNIQUE, 
            'name' TEXT UNIQUE, 
            'desc' TEXT, 
            price REAL, 
            photo TEXT, 
            dimension REAL,
            box_qty INTEGER,
            bag_qty INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS promotions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            'name' TEXT UNIQUE, 
            new_price REAL,
            user_id INTEGER,
            item_id INTEGER,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cargos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_date TEXT,
            'status' INTEGER DEFAULT 0, 
            total_price REAL,
            type INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            cargo_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            type INTEGER,
            is_finalized INTEGER DEFAULT 0,
            FOREIGN KEY (cargo_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    db.commit()


def register_user(username, password, tg_id, tg_username):
    status = True
    message = "Пользователь успешно зарегистрирован."
    try:
        # Проверяем, существует ли уже пользователь с таким username
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            status = False
            message = "A user with that username already exists. Please try again."
            return status, message

        # Формирование запроса на добавление нового пользователя
        cur.execute("""
            INSERT INTO users (username, 'password', tg_id, tg_username, type)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password, tg_id, tg_username, 0))  # type установлен в 0 по умолчанию

        # Сохранение изменений в базе данных
        db.commit()
        return status, message
    except Exception as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        status = False
        message = "Error during user registration. Please try again."
        return status, message



def check_credentials_and_update_tg_id(username, password, tg_id, tg_username):
    cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if user and user[1] == password:
        # Проверяем, совпадает ли tg_id с сохраненным в базе данных
        if user[0] != tg_id:
            cur.execute("UPDATE users SET tg_id = ? WHERE id = ?", (tg_id, user[0]))
            cur.execute("UPDATE users SET tg_username = ? WHERE id = ?", (tg_username, user[0]))
            db.commit()
        return True
    return False


async def is_user_registered(tg_id):
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    return cur.fetchone() is not None


async def is_user_typed(tg_id):
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    return cur.fetchone() is not None


def update_user_type(tg_id, type):
    # Обновляем количество товара в заказе
    cur.execute("""
        UPDATE users 
        SET type = ? 
        WHERE tg_id = ?
    """, (type, tg_id))
    db.commit()

def get_total_orders_count(user_id):
    # Подготовка SQL-запроса для подсчета количества заказов пользователя
    query = """
        SELECT COUNT(*) FROM cargos WHERE user_id = ?
    """

    # Выполнение запроса и получение результата
    cur.execute(query, (user_id,))
    result = cur.fetchone()

    # Возвращаем количество заказов или 0, если результат отсутствует
    return result[0] if result else 0

async def get_user_id(tg_id):
    user = cur.execute("SELECT * FROM users WHERE tg_id == {key}".format(key=tg_id)).fetchone()
    return user[0]


def get_user_info(user_id):
    cur.execute("SELECT id, tg_id, username, type, tg_username FROM users WHERE id = ?", (user_id,))
    user_info = cur.fetchone()
    if user_info:
        return {'id': user_info[0], 'tg_id': user_info[1],
                'username': user_info[2], 'type': user_info[3], 'tg_username': user_info[4]}
    return None


def get_user_info_from_tg(tg_id):
    cur.execute("SELECT id, tg_id, username, tg_username , type FROM users WHERE tg_id = ?", (tg_id,))
    user_info = cur.fetchone()
    if user_info:
        return {'id': user_info[0], 'tg_id': user_info[1], 'username': user_info[2], 'tg_username': user_info[3], 'type': user_info[3]}
    return None


async def get_all_items():
    items = cur.execute("SELECT * FROM items").fetchall()
    return items


async def get_one_item(item_name, user_id):
    query = """
    SELECT 
        i.id AS item_id, 
        i.'code' AS item_code, 
        i.'name' AS item_name, 
        i.'desc' AS item_description, 
        i.photo AS item_photo, 
        i.dimension AS item_dimension, 
        i.box_qty AS item_box_qty, 
        i.bag_qty AS item_bag_qty,
        COALESCE(p.new_price, i.price) AS item_price
    FROM 
        items i
    LEFT JOIN 
        promotions p ON i.id = p.item_id AND p.user_id = ?
    WHERE 
        i.'name' LIKE ?
    """
    cur.execute(query, (user_id, item_name))
    result = cur.fetchone()
    if result:
        # Преобразование результата запроса в словарь
        item = dict(zip(['item_id', 'item_code', 'name', 'item_description', 'item_photo', 'item_dimension',
                         'item_box_qty', 'item_bag_qty', 'item_price'], result))
        return item
    else:
        return None


def add_to_order(user_id, item, qty):
    # Получение типа пользователя
    user_type = cur.execute("SELECT type FROM users WHERE id == {key}".format(key=user_id)).fetchone()

    # Проверка, есть ли результат запроса (т.е., существует ли пользователь)
    if user_type is not None:
        # Получение type из результата запроса (предполагаем, что это первый элемент в результате)
        user_type = user_type[0]

        # Проверка, существует ли уже такой заказ
        existing_order = cur.execute(
            "SELECT id, quantity FROM orders WHERE user_id = ? AND item_id = ? AND type = ? AND is_finalized = 0",
            (user_id, item['item_id'], user_type)).fetchone()

        if existing_order:
            # Если заказ существует, обновляем его количество
            order_id, existing_quantity = existing_order
            new_quantity = qty
            cur.execute("UPDATE orders SET quantity = ? WHERE id = ?", (new_quantity, order_id))
        else:
            # Если заказа нет, добавляем новый
            query = """
                    INSERT INTO orders (user_id, item_id, quantity, type, cargo_id, is_finalized)
                    VALUES (?, ?, ?, ?, NULL, 0)
                    """
            cur.execute(query, (user_id, item['item_id'], qty, user_type))

        total_price = None
        if user_type == 1:
            total_price = qty * item['item_price'] * item['item_box_qty']
        elif user_id == 2:
            total_price = qty * item['item_price'] * item['item_bag_qty']

        # Сохранение изменений в базе данных
        db.commit()
        return total_price
    else:
        # Обработка случая, когда пользователь не найден
        print("Пользователь с таким ID не найден.")
        return None


def get_user_cart(user_id):
    # Запрос для получения товаров из корзины пользователя
    query = """
    SELECT 
        o.id AS order_id,    
        o.quantity,
        o.type,
        i.id AS item_id,
        i.name,
        i.dimension,
        i.desc,
        i.box_qty,
        i.bag_qty,
        i.code,
        COALESCE(p.new_price, i.price) AS price
    FROM 
        orders o
    JOIN 
        items i ON o.item_id = i.id
    LEFT JOIN 
        promotions p ON i.id = p.item_id AND p.user_id = ?
    JOIN 
        users u ON o.user_id = u.id
    WHERE 
        o.user_id = ? AND o.is_finalized = 0 AND o.type = u.type
    """

    # Получение данных о товарах в корзине
    cart_items_raw = cur.execute(query, (user_id, user_id)).fetchall()

    # Подготовка списка словарей для товаров в корзине
    cart_items = []
    total_price = 0
    total_dimension = 0
    for item in cart_items_raw:
        order_id, quantity, order_type, item_id, name, dimension, desc, box_qty, bag_qty, code, price = item
        item_total_price = box_qty * quantity * price if order_type == 1 else bag_qty * quantity * price

        items_per_pack = box_qty if order_type == 1 else bag_qty
        item_total_dimension = dimension * items_per_pack * quantity

        # Добавление информации о каждом товаре
        cart_item = {
            'order_id': order_id,
            'item_id': item_id,
            'order_type': order_type,
            'box_qty': box_qty,
            'bag_qty': bag_qty,
            'name': name,
            'dimension': dimension,
            'item_total_dimension': item_total_dimension,
            'desc': desc,
            'code': code,
            'price_per_item': price,
            'item_total_price': item_total_price,
            'quantity': quantity
        }
        cart_items.append(cart_item)

        # Добавление стоимости товара к общей стоимости
        total_dimension += item_total_dimension
        total_price += item_total_price

    return cart_items, total_price, total_dimension


def get_order_quantity(order_id: int) -> int:
    # Получаем текущее количество товара
    cur.execute("""
        SELECT quantity FROM orders WHERE id = ? AND is_finalized = 0
    """, (order_id,))
    quantity = cur.fetchone()
    return quantity[0] if quantity else 0


def get_current_quantity(user_id: int, item_id: int) -> int:
    user_type = cur.execute("SELECT type FROM users WHERE id == {key}".format(key=user_id)).fetchone()
    user_type = user_type[0]

    # Получаем текущее количество товара
    cur.execute("""
        SELECT quantity FROM orders WHERE user_id = ? AND item_id = ? AND type = ? AND is_finalized = 0
    """, (user_id, item_id, user_type))
    quantity = cur.fetchone()
    return quantity[0] if quantity else 1  # Возвращаем 1, если запись отсутствует


def update_item_quantity_in_cart(item_id: int, new_quantity: int, order_id: int):
    if new_quantity > 0:
        # Обновляем количество товара в заказе
        cur.execute("""
            UPDATE orders 
            SET quantity = ? 
            WHERE id = ? AND item_id = ?
        """, (new_quantity, order_id, item_id))
    else:
        # Удаляем товар из корзины, если его количество равно 0
        cur.execute("""
            DELETE FROM orders WHERE id = ? AND is_finalized = 0
        """, (order_id, ))
    db.commit()


async def finalize_order(user_info, order_ids, total_price):
    # Шаг 1: Создание новой записи в таблице cargos
    cur.execute("""
        INSERT INTO cargos (user_id, order_date, total_price, type)
        VALUES (?, datetime('now'), ?, ?)
    """, (user_info['id'], total_price, user_info['type']))

    # Шаг 2: Получение ID только что созданного cargo
    cargo_id = cur.lastrowid

    # Шаг 3: Обновление записей в таблице orders
    cur.executemany("""
        UPDATE orders 
        SET is_finalized = 1, cargo_id = ?
        WHERE id = ? AND user_id = ?
    """, [(cargo_id, order_id, user_info['id']) for order_id in order_ids])

    # Сохранение изменений в базе данных
    db.commit()
    return cargo_id
