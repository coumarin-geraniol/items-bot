from contextlib import suppress
from aiogram import F, Router
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto
from database.database import get_all_items, get_one_item, get_user_cart, add_to_order, \
    get_current_quantity, get_user_info_from_tg
from global_vars import user_current_item, item_quantity, get_available_items_title
from handlers.fsm import UserActions
from handlers.main import get_type_name, format_number_with_spaces
from keyboards.keyboards import get_main_kb, get_catalog_kb, get_quantity_kb, NumbersCallbackFactory

router = Router()


@router.message(F.text == 'Catalog', UserActions.is_type)
async def catalogs(message: types.Message, state: FSMContext):
    items = await get_all_items()
    if not items:
        await message.answer('Catalog is empty.', reply_markup=get_main_kb())
    else:
        catalog_kb = await get_catalog_kb()
        await message.answer('Choose items.', reply_markup=catalog_kb)
        await state.set_state(UserActions.is_catalog)


@router.message(lambda message: message.text in get_available_items_title(), UserActions.is_catalog)
async def handle_item_selection(message: types.Message):
    user_info = get_user_info_from_tg(message.from_user.id)
    user_id = user_info['id']

    item = await get_one_item(message.text, user_id)
    user_current_item[message.from_user.id] = item
    photo = FSInputFile('resources/' + item['item_photo'] + '.jpg')
    kb_quantity = await get_quantity_kb()
    item_quantity[message.from_user.id] = get_current_quantity(user_id, item['item_id'])

    items_per_pack = item['item_box_qty'] if user_info['type'] == 1 else item['item_bag_qty']
    item_total_price = item_quantity[message.from_user.id] * item['item_price'] * items_per_pack
    price_per_box = item['item_price'] * items_per_pack
    item_total_dimension = item['item_dimension'] * items_per_pack * item_quantity[message.from_user.id]

    response = f"<b>Name:</b> {item['name']}\n"
    response += f"Code: {item['item_code']}\n" \
                f"<b>Price per {get_type_name(user_info['type']).capitalize()}:</b> ${format_number_with_spaces(price_per_box)}\n\n" \
    \
                f"<b>Packaging type:</b> {get_type_name(user_info['type'])}\n" \
                f"<b>Volume per item:</b> {item['item_dimension']}m3\n" \
                f"<b>Total Volume:</b> {item_total_dimension}m3\n\n" \
    \
                f"<b>Items per box:</b> {items_per_pack}\n" \
                f"<b>Total {get_type_name(user_info['type']).capitalize()}:</b> {item_quantity[message.from_user.id]}\n" \
                f"<b>Total Price:</b> ${format_number_with_spaces(item_total_price)}\n" \


    await message.answer_photo(photo=photo,
                               caption=response,
                               parse_mode=ParseMode.HTML,
                               reply_markup=kb_quantity)


async def update_num_text_quantity(message: types.Message, new_value: int, item, user_info):
    with suppress(TelegramBadRequest):
        kb_quantity = await get_quantity_kb()

        items_per_pack = item['item_box_qty'] if user_info['type'] == 1 else item['item_bag_qty']
        item_total_price = new_value * item['item_price'] * items_per_pack
        price_per_box = item['item_price'] * items_per_pack
        item_total_dimension = item['item_dimension'] * items_per_pack * new_value

        response = f"<b>Name:</b> {item['name']}\n"
        response += f"Code: {item['item_code']}\n" \
                    f"<b>Price per {get_type_name(user_info['type']).capitalize()}:</b> ${format_number_with_spaces(price_per_box)}\n\n" \
 \
                    f"<b>Packaging type:</b> {get_type_name(user_info['type'])}\n" \
                    f"<b>Volume per item:</b> {item['item_dimension']}m3\n" \
                    f"<b>Total Volume:</b> {item_total_dimension}m3\n\n" \
 \
                    f"<b>Items per box:</b> {items_per_pack}\n" \
                    f"<b>Total {get_type_name(user_info['type']).capitalize()}:</b> {new_value}\n" \
                    f"<b>Total Price:</b> ${format_number_with_spaces(item_total_price)}\n"

        await message.edit_caption(caption=response,
                           parse_mode=ParseMode.HTML,
                           reply_markup=kb_quantity)


@router.callback_query(NumbersCallbackFactory.filter(), UserActions.is_catalog)
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    user_id = callback.from_user.id
    item = user_current_item.get(user_id)  # Получаем текущий продукт пользователя
    if not item:
        await callback.answer("Item not found")
        return
    # Текущее значение
    item_quantity_value = item_quantity.get(callback.from_user.id, 0)

    user_info = get_user_info_from_tg(user_id)
    user_id = user_info['id']

    # Если число нужно изменить
    if callback_data.action == "change":
        item_quantity[callback.from_user.id] = item_quantity_value + callback_data.value
        if(item_quantity[callback.from_user.id] > 0):
            await update_num_text_quantity(callback.message, item_quantity_value + callback_data.value, item, user_info)
        else:
            item_quantity[callback.from_user.id] = 1
            await callback.answer()


    elif callback_data.action == "finish":
        add_to_order(user_id, item, item_quantity_value)
        # if add_to_order(user_id, item, item_quantity_value) == None:
        #     await state.clear()
        #     await callback.message.answer(
        #         text="Please log in",
        #         reply_markup=get_login_kb()
        #     )
        #     return await callback.answer("User not found")
        cart_items, total_price = get_user_cart(user_id)
        response = f"<b>Your Cart:</b>\n\n"
        for item in cart_items:
            items_per_pack = item['box_qty'] if item['order_type'] == 1 else item['bag_qty']
            total_packs = item['quantity']
            total_items = items_per_pack * total_packs
            item_total_dimension = item['dimension'] * items_per_pack * item['quantity']

            response += f"* <b>Name:</b> {item['name']} - {item['code']}\n" \
                        f"   <b>Total Volume:</b> {item_total_dimension}m3\n" \
                        f"   <b>Items per {get_type_name(item['order_type']).capitalize()}:</b> {items_per_pack}\n" \
                        f"   <b>Total Packs:</b> {total_packs}\n" \
                        f"   <b>Total Items:</b> {total_items}\n" \
                        f"   <b>Price per Item:</b> ${format_number_with_spaces(item['price_per_item'])}\n" \
                        f"   <b>Total Price for Item:</b> ${format_number_with_spaces(item['item_total_price'])}\n" \
                        f"\n"

        response += f"\n<b>Total Cart Value:</b> ${format_number_with_spaces(total_price)}"
        response += f"\n<b>Packaging type:</b> {get_type_name(user_info['type'])}"

        try:
            photo_file = FSInputFile('resources/white.png')
            photo = InputMediaPhoto(media=photo_file)
            await callback.message.edit_media(media=photo)
            await callback.message.edit_caption(caption=response, parse_mode='HTML')
        except Exception as e:
            print(f"Error sending message: {e}")
        await callback.answer()


    else:
        await callback.answer()



@router.message(lambda message: message.text not in get_available_items_title(), UserActions.is_catalog)
async def handle_item_selection(message: types.Message, state: FSMContext):
    await state.set_state(UserActions.is_type)
    await message.answer(
        text="Item not found",
        reply_markup=get_main_kb()
    )

@router.callback_query(UserActions.is_auth)
async def callbacks_none(
        callback: types.CallbackQuery
):
    await callback.answer()
