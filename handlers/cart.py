import os
from contextlib import suppress
from aiogram import F, Router, Bot
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from config import GROUP_ID, EXPORT_ID
from database.database import get_user_id, update_item_quantity_in_cart, \
    get_order_quantity, finalize_order, get_user_info_from_tg
from export.excel import create_excel_file
from handlers.fsm import UserActions
from handlers.main import get_type_name_grammar
from keyboards.keyboards import get_main_kb, get_cart_kb, ItemsCallbackFactory
from database.database import get_user_cart

router = Router()


@router.message(F.text == 'Cart', UserActions.is_type)
async def cmd_cart(message: types.Message, state: FSMContext):
    user_id = await get_user_id(message.from_user.id)
    cart_items, total_price, total_dimension = get_user_cart(user_id)
    if not cart_items:
        await message.answer('Cart is empty.', reply_markup=get_main_kb())
    else:
        response = f"<b>Your Cart:</b>\n"
        for item in cart_items:
            items_per_pack = item['box_qty'] if item['order_type'] == 1 else item['bag_qty']
            total_item_qty = items_per_pack * item['quantity']
            response += f"<b>{item['name']} - </b>" \
                        f"{item['quantity']} {get_type_name_grammar(item['order_type'], item['quantity']).capitalize()} " \
                        f"({total_item_qty} items at {item['price_per_item']}$ each) - " \
                        f"Total: ${item['item_total_price']}\n"
        response += f"\n<b>Total volume: {total_dimension}</b>"
        response += f"\n<b>Total price: {total_price}</b>"
        await message.answer(response, parse_mode='HTML', reply_markup=get_cart_kb(cart_items))
        await state.set_state(UserActions.is_cart)


async def update_cart_text(message: types.Message, user_id):
    with suppress(TelegramBadRequest):
        cart_items, total_price, total_dimension = get_user_cart(user_id)
        if not cart_items:
            await message.edit_text('Cart is empty.')
            await message.answer("Redirecting to main page", reply_markup=get_main_kb())
        else:
            response = f"<b>Your Cart:</b>\n"
            for item in cart_items:
                items_per_pack = item['box_qty'] if item['order_type'] == 1 else item['bag_qty']
                total_item_qty = items_per_pack * item['quantity']
                response += f"<b>{item['name']} - </b>" \
                            f"{item['quantity']} {get_type_name_grammar(item['order_type'], item['quantity']).capitalize()} " \
                            f"({total_item_qty} items at {item['price_per_item']}$ each) - " \
                            f"Total: ${item['item_total_price']}\n"

            response += f"\n<b>Total volume: {total_dimension}</b>"
            response += f"\n<b>Total price: {total_price}</b>"
            await message.edit_text(response, parse_mode='HTML', reply_markup=get_cart_kb(cart_items))


@router.callback_query(ItemsCallbackFactory.filter(), UserActions.is_cart)
async def callbacks_num_change_cart(
        callback: types.CallbackQuery,
        callback_data: ItemsCallbackFactory,
        state: FSMContext,
        bot: Bot):
    user_info = get_user_info_from_tg(callback.from_user.id)
    user_id = user_info['id']

    item_id = callback_data.item_id
    order_id = callback_data.order_id
    current_quantity = get_order_quantity(order_id)  # функция для получения текущего количества

    cart_items, total_price, total_dimension = get_user_cart(user_id)

    if callback_data.action == "change" and callback_data.value is not None:
        new_quantity = max(current_quantity + callback_data.value, 0)
        update_item_quantity_in_cart(item_id, new_quantity, order_id)
        await update_cart_text(callback.message, user_id)

        await callback.answer(f"Quantity updated: {new_quantity}")

    elif callback_data.action == "finish":
        # Логика для оформления
        order_ids = [item['order_id'] for item in cart_items]
        cargo_id = await finalize_order(user_info, order_ids, total_price)

        filename = await create_excel_file(user_id, cargo_id, cart_items, total_price)

        excel_file = FSInputFile(filename)
        await bot.send_document(chat_id=GROUP_ID, document=excel_file,
                                caption=f"Order from @{user_info['tg_username']}")
        await bot.send_document(chat_id=EXPORT_ID, document=excel_file,
                                caption=f"Order from @{user_info['tg_username']}")

        await callback.message.edit_text("Your order has been received and sent to the administrators.")
        await state.set_state(UserActions.is_type)
        await callback.answer("Your order has been successfully placed.", reply_markup=get_main_kb())


    elif callback_data.action == "continue":
        await callback.message.edit_text("Please select an option below.")
        await callback.answer("Redirecting to main page.", reply_markup=get_main_kb())
        await state.set_state(UserActions.is_type)
    else:
        await state.set_state(UserActions.is_type)
        await callback.answer("No action performed", reply_markup=get_main_kb())


@router.callback_query(UserActions.is_cart)
async def callbacks_none(
        callback: types.CallbackQuery
):
    await callback.answer()
