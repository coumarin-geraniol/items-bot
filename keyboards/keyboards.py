from aiogram.filters.callback_data import CallbackData
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import Optional

from database.database import get_all_items

type_kb = [
    [KeyboardButton(text='Box'),
     KeyboardButton(text='Bag')]
]
main_kb = [
    [KeyboardButton(text='Catalog'),
     KeyboardButton(text='Cart')],
    [KeyboardButton(text='Change the delivery type')]
]
login_kb = [
    [KeyboardButton(text='Login'),
     KeyboardButton(text='Register')]
]


def get_type_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for row in type_kb:
        kb.add(*[KeyboardButton(text=button.text) for button in row])
    return kb.as_markup(resize_keyboard=True, input_field_placeholder='Please select the type of cargo')


def get_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for row in main_kb:
        kb.add(*[KeyboardButton(text=button.text) for button in row])
    return kb.as_markup(resize_keyboard=True, input_field_placeholder='Please select an option below.')


def get_login_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for row in login_kb:
        kb.add(*[KeyboardButton(text=button.text) for button in row])
    return kb.as_markup(resize_keyboard=True)


admin_kb = [
    [KeyboardButton(text='Каталог'),
     KeyboardButton(text='Корзина'),
     KeyboardButton(text='Админ-панель')],
    [
        KeyboardButton(text='Отправить все продукты'),
        KeyboardButton(text='Показать все продукты'),

    ]
]
main_admin = ReplyKeyboardMarkup(keyboard=admin_kb,
                                 resize_keyboard=True,
                                 input_field_placeholder='Please select an option below.')

admin_panel_kb = [
    [KeyboardButton(text='Добавить товар'),
     KeyboardButton(text='Удалить товар'),
     KeyboardButton(text='Сделать рассылку')]
]
admin_panel = ReplyKeyboardMarkup(keyboard=admin_panel_kb,
                                  resize_keyboard=True,
                                  input_field_placeholder='Please select an option below.')

catalog_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Футболки', callback_data='t-shirt')],
    [InlineKeyboardButton(text='Шорты', callback_data='shorts')],
    [InlineKeyboardButton(text='Кроссовки', callback_data='sneakers')]
])


# cancel_kb = [
#     [KeyboardButton(text='Отмена')]
# ]
# cancel = ReplyKeyboardMarkup(keyboard=cancel_kb,
#                              resize_keyboard=True,
#                              input_field_placeholder='Please select an option below.')


def get_cancel_kb() -> InlineKeyboardMarkup:
    cancel = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    ])
    return cancel


async def product_keyboard() -> ReplyKeyboardMarkup:
    products = await get_all_items()
    product_buttons = [[KeyboardButton(text='Назад')]]

    for product in products:
        product_buttons.append([KeyboardButton(text=product[1])])

    keyboard = ReplyKeyboardMarkup(keyboard=product_buttons, resize_keyboard=True,
                                   input_field_placeholder='Please select an item below.')
    return keyboard


async def get_catalog_kb() -> ReplyKeyboardMarkup:
    products = await get_all_items()  # Получение списка всех продуктов
    catalog_buttons = [[KeyboardButton(text='Back')]]  # Кнопка возврата в главное меню на отдельной строке

    # Создаем кнопки продуктов в две колонки
    row = []
    for product in products:
        row.append(KeyboardButton(text=product[2]))  # Добавление названия продукта в строку
        if len(row) == 2:  # Если в строке уже две кнопки, добавляем строку в catalog_buttons
            catalog_buttons.append(row)
            row = []  # Начинаем новую строку

    if row:  # Добавляем последнюю строку, если в ней есть кнопки
        catalog_buttons.append(row)

    keyboard = ReplyKeyboardMarkup(keyboard=catalog_buttons, resize_keyboard=True,
                                   input_field_placeholder='Please select an item below.')
    return keyboard


class NumbersCallbackFactory(CallbackData, prefix="quantity"):
    action: str
    value: Optional[int] = None


async def get_quantity_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="Add to cart", callback_data=NumbersCallbackFactory(action="finish")
    )
    builder.adjust(2)
    return builder.as_markup()


class ItemsCallbackFactory(CallbackData, prefix="cart"):
    action: str
    value: Optional[int] = None
    item_id: int
    order_id: int


def get_cart_kb(cart_items) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in cart_items:
        items_per_pack = item['box_qty'] if item['order_type'] == 1 else item['bag_qty']
        total_item_qty = items_per_pack * item['quantity']
        # Добавление кнопок для уменьшения и увеличения количества
        builder.add(
            InlineKeyboardButton(text="-1", callback_data=ItemsCallbackFactory(action="change", value=-1,
                                                                               item_id=item['item_id'],
                                                                               order_id=item['order_id']).pack()),
            InlineKeyboardButton(text=f"{item['name']} ({total_item_qty} pc.)", callback_data="noop"),
            InlineKeyboardButton(text="+1", callback_data=ItemsCallbackFactory(action="change", value=1,
                                                                               item_id=item['item_id'],
                                                                               order_id=item['order_id']).pack())
        )
        # После каждой добавленной группы кнопок делаем переход на новую строку
        builder.adjust(3)

    # Последние две кнопки размещаем в отдельной строке
    builder.row(
        InlineKeyboardButton(text="Back to main", callback_data=ItemsCallbackFactory(action="continue", item_id=0, order_id=0).pack()),
        InlineKeyboardButton(text="Submit Order", callback_data=ItemsCallbackFactory(action="finish", item_id=0, order_id=0).pack())
    )

    return builder.as_markup()

