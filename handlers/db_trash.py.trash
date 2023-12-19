def finalize_order(user_id, product, user_value):
    # Получаем текущую дату
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_type = cur.execute("SELECT * FROM users WHERE id == {key}".format(key=user_id)).fetchone()
    # Создаем заказ
    cur.execute("INSERT INTO orders (user_id, order_date, type) VALUES (?, ?, ?)", (user_id, order_date, user_type[4]))
    order = cur.fetchone()  # Получаем ID созданного заказа
    order_id = order[0]

    # Добавляем товары в заказ
    if order[5] == 1:  # Если упаковка - box
        total_price = user_value * product[4] * product[7]
    elif order[5] == 2:  # Если упаковка - bag
        total_price = user_value * product[4] * product[8]

    cur.execute("INSERT INTO order_items (order_id, item_id, quantity, price_per_item) VALUES (?, ?, ?, ?)",
                (order_id, product[0], user_value, product[4]))

    # Обновляем общую сумму заказа
    cur.execute("UPDATE orders SET total_price = ? WHERE id = ?", (total_price, order_id))

    db.commit()
    return total_price

def get_user_cart(user_id):
    # Получаем товары из корзины пользователя и их индивидуальную стоимость
    cur.execute("""
        SELECT oi.item_id, oi.order_id, oi.quantity, oi.price_per_item, i.name, o.total_price
        FROM order_items oi 
        JOIN items i ON oi.item_id = i.i_id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.user_id = ? AND o.is_finalized = 0
    """, (user_id,))
    items = cur.fetchall()

    # Расчет общей стоимости заказа
    total_price = sum(item[-1] for item in items)  # Суммируем total_price для каждой записи

    return items, total_price
