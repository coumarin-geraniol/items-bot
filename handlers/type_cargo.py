from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from database.database import update_user_type
from handlers.fsm import UserActions
from keyboards.keyboards import get_main_kb, get_type_kb

router = Router()


@router.message(F.text == 'Box', UserActions.is_auth)
async def contacts(message: types.Message, state: FSMContext):
    update_user_type(message.from_user.id, 1)
    await state.set_state(UserActions.is_type)
    await message.answer("Redirecting to main page", reply_markup=get_main_kb())


@router.message(F.text == 'Bag', UserActions.is_auth)
async def contacts(message: types.Message, state: FSMContext):
    update_user_type(message.from_user.id, 2)
    await state.set_state(UserActions.is_type)
    await message.answer("Redirecting to main page", reply_markup=get_main_kb())


@router.message(UserActions.is_auth)
async def contacts(message: types.Message, state: FSMContext):
    await message.answer("Please select the package type", reply_markup=get_type_kb())


@router.message(F.text == 'Change the delivery type', UserActions.is_type)
async def change_type(message: types.Message, state: FSMContext):
    await state.set_state(UserActions.is_auth)
    await message.answer("Please select the package type", reply_markup=get_type_kb())
