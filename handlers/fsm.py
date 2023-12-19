from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from keyboards.keyboards import get_main_kb, get_login_kb


class UserAuth(StatesGroup):
    username = State()
    password = State()
    is_auth = State()
    is_type = State()
    is_catalog = State()
    is_cart = State()

class UserActions(StatesGroup):
    username = State()
    password = State()
    reg_username = State()
    reg_password = State()
    reg_confirm = State()
    is_auth = State()
    is_type = State()
    is_catalog = State()
    is_cart = State()




router = Router()




# default_state - это то же самое, что и StateFilter(None)
@router.message(StateFilter(None), Command(commands=["back"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(
        text="Nothing to cancel.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.callback_query(F.data == 'cancel', UserActions.password)
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        text="Please press button Log in",
        reply_markup=get_login_kb()
    )
    await callback.answer()


@router.message(Command(commands=["back"]))
@router.message(F.text.lower() == "back")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.set_state(UserActions.is_type)
    await message.answer(
        text="Back to main menu.",
        reply_markup=get_main_kb()
    )