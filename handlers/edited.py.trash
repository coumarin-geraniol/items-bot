
async def get_available_product_titles():
    products = await get_all_products()
    return [product[1] for product in products]


async def start_bot(bot: Bot):
    global available_product_titles
    await db.db_start()
    available_product_titles = await get_available_product_titles()
    await bot.send_message(ID, text='Bot started')
    print('Бот успешно запущен!')


class NewOrder(StatesGroup):
    type = State()
    name = State()
    desc = State()
    price = State()
    photo = State()


async def show_all_products(message: types.Message, products: list) -> None:
    for product in products:
        photo = FSInputFile('tmp/' + product[4] + '.jpg')
        await message.answer_photo(photo=photo,
                                   caption=f'<b>{product[1]}</b>',
                                   parse_mode=ParseMode.HTML)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await db.cmd_start_db(message.from_user.id)
    await message.answer_sticker('CAACAgIAAxkBAAMpZBAAAfUO9xqQuhom1S8wBMW98ausAAI4CwACTuSZSzKxR9LZT4zQLwQ')
    await message.answer(f'{message.from_user.first_name}, добро пожаловать в магазин кроссовок!',
                         reply_markup=kb.main)
    if message.from_user.id == ID:
        await message.answer('Вы авторизовались как администратор!', reply_markup=kb.main_admin)


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f'{message.from_user.id}')


@dp.message(F.text == 'Каталог')
async def catalog(message: types.Message):
    await message.answer('Выберите категорию', reply_markup=kb.catalog_list)


@dp.message(F.text == 'Корзина')
async def cart(message: types.Message):
    account_id = await get_account_id(message.from_user.id)
    cart_items = get_user_cart(account_id)

    if not cart_items:
        await message.answer('Корзина пуста!')
    else:
        response = "Ваша корзина:\n"
        for item_id, quantity, price_per_item, name in cart_items:
            response += f"{name} - {quantity} шт. по {price_per_item} каждая.\n"
        await message.answer(response)


@dp.message(F.text == 'Отмена')
async def cart(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.clear()
    if message.from_user.id == ID:
        await message.answer('Вы отменили заказ', reply_markup=kb.main_admin)
    else:
        await message.answer('Вы отменили заказ', reply_markup=kb.main)


@dp.message(F.text == 'Отправить все продукты')
async def contacts(message: types.Message):
    products = await db.get_all_products()
    if not products:
        if message.from_user.id == ID:
            await message.answer('База пуста', reply_markup=kb.main_admin)
        else:
            await message.answer('База пуста', reply_markup=kb.main)
    else:
        await show_all_products(message, products)


@dp.message(F.text == 'Показать все продукты')
async def contacts(message: types.Message):
    products = await db.get_all_products()
    if not products:
        if message.from_user.id == ID:
            await message.answer('База пуста', reply_markup=kb.main_admin)
        else:
            await message.answer('База пуста', reply_markup=kb.main)
    else:
        product_kb = await product_keyboard()  # Используем await здесь
        await message.answer(f'{available_product_titles}', reply_markup=product_kb)


@dp.message(lambda message: message.text in available_product_titles)
async def handle_product_selection(message: types.Message):
    product = await get_one_product(message.text)
    user_current_product[message.from_user.id] = product
    photo = FSInputFile('tmp/' + product[4] + '.jpg')
    kb_quantity = await get_keyboard_quantity()
    user_data[message.from_user.id] = 1
    await message.answer_photo(photo=photo,
                               caption=f'<b>{product[1]} - {user_data[message.from_user.id]}</b>',
                               parse_mode=ParseMode.HTML,
                               reply_markup=kb_quantity)


async def update_num_text_quantity(message: types.Message, new_value: int, product):
    with suppress(TelegramBadRequest):
        kb_quantity = await get_keyboard_quantity()
        await message.edit_caption(caption=f'<i>{product[1]} - {new_value}</i>',
                                   parse_mode=ParseMode.HTML,
                                   reply_markup=kb_quantity)


@dp.callback_query(NumbersCallbackFactory.filter())
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory,
):
    global available_product_titles
    user_id = callback.from_user.id
    product = user_current_product.get(user_id)  # Получаем текущий продукт пользователя
    if not product:
        await callback.answer("Продукт не найден.")
        return
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)
    # Если число нужно изменить
    if callback_data.action == "change":
        user_data[callback.from_user.id] = user_value + callback_data.value
        await update_num_text_quantity(callback.message, user_value + callback_data.value, product)
    elif callback_data.action == "finish":
        account_id = await get_account_id(user_id)
        total_price = finalize_order(user_id, account_id, product, user_value)
        available_product_titles = await get_available_product_titles()
        cart_items = get_user_cart(account_id)
        response = "Ваша корзина:\n"
        for item_id, quantity, price_per_item, name in cart_items:
            response += f"{name} - {quantity} шт. по {price_per_item} каждая.\n"
        await callback.answer()
        await bot.send_message(user_id, response)

    else:
        await callback.answer()








@dp.message(F.text == 'Админ-панель')
async def contacts(message: types.Message):
    if message.from_user.id == ID:
        await message.answer('Вы вошли в админ-панель', reply_markup=kb.admin_panel)
    else:
        await message.reply('Я тебя не понимаю.')


@dp.message(StateFilter(None), F.text == 'Добавить товар')
async def add_item(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        await state.set_state(NewOrder.type)
        await message.answer('Выберите тип товара', reply_markup=kb.catalog_list)
    else:
        await message.reply('Я тебя не понимаю.', reply_markup=kb.catalog_list)


@dp.callback_query(NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=call.data)
    await call.message.answer('Напишите название товара', reply_markup=kb.cancel)
    await state.set_state(NewOrder.name)


@dp.message(NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Напишите описание товара', reply_markup=kb.cancel)
    await state.set_state(NewOrder.desc)


@dp.message(NewOrder.desc)
async def add_item_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer('Напишите цену товара', reply_markup=kb.cancel)
    await state.set_state(NewOrder.price)


@dp.message(NewOrder.price)
async def add_item_desc(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('Отправьте фотографию товара', reply_markup=kb.cancel)
    await state.set_state(NewOrder.photo)


@dp.message(lambda message: not message.photo, NewOrder.photo)
async def add_item_photo_check(message: types.Message):
    await message.answer('Это не фотография!', reply_markup=kb.cancel)


@dp.message(F.photo, NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    await bot.download(
        message.photo[-1],
        destination=f"tmp/{message.photo[-1].file_id}.jpg"
    )
    await state.update_data(photo=message.photo[-1].file_id)
    user_data = await state.get_data()
    await db.add_item(user_data)
    await message.answer('Товар успешно создан!', reply_markup=kb.main_admin)
    await state.clear()


@dp.message()
async def answer(message: types.Message):
    if message.from_user.id == ID:
        await message.reply('Я тебя не понимаю.', reply_markup=kb.main_admin)
    else:
        await message.reply('Я тебя не понимаю.', reply_markup=kb.main)


@dp.callback_query()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == 't-shirt':
        await callback_query.message.answer(f'Вы выбрали футболки')
    elif callback_query.data == 'shorts':
        await callback_query.message.answer(f'Вы выбрали шорты')
    elif callback_query.data == 'sneakers':
        await callback_query.message.answer(f'Вы выбрали кроссовки')
    elif callback_query.data == 'cancel':
        if callback_query.from_user.id == ID:
            await callback_query.reply('Я тебя не понимаю.', reply_markup=kb.main_admin)
        else:
            await callback_query.reply('Я тебя не понимаю.', reply_markup=kb.main)
        await callback_query.answer("Вы отменили")
    await callback_query.answer('Вы выбрали бренд')
