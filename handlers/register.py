from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from database.database import is_user_registered, register_user
from handlers.fsm import UserActions
from keyboards.keyboards import get_type_kb, get_cancel_kb, get_main_kb, get_login_kb

router = Router()


@router.message(UserActions.reg_username, F.text)
async def cmd_reg_password(message: Message, state: FSMContext):
    await state.update_data(reg_username=message.text.lower())
    await message.answer(
        text=f"Now enter password for user: {message.text.lower()}",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(UserActions.reg_password)

@router.message(UserActions.reg_password, F.text)
async def cmd_reg_password(message: Message, state: FSMContext):
    await state.update_data(reg_password=message.text.lower())
    await message.answer(
        text=f"Now confirm your password",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(UserActions.reg_confirm)



@router.message(UserActions.reg_confirm, F.text)
async def cmd_reg_auth(message: Message, state: FSMContext):
    await state.update_data(reg_confirm=message.text.lower())

    user_data = await state.get_data()
    username = user_data['reg_username']
    password = user_data['reg_password']
    confirm = message.text.lower()

    if confirm != password:
        await message.answer(
            text=f"Passwords do NOT match for user: {username}. Please enter password",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(UserActions.reg_password)
    else:
        tg_id = message.from_user.id
        tg_username = message.from_user.username
        status, reg_message = register_user(username, password, tg_id, tg_username)

        if status:
            await message.answer(
                "You are successfully registered"
            )
            await message.answer(
                "Please select the package type",
                reply_markup=get_type_kb()
            )
            await state.set_state(UserActions.is_auth)
        else:
            await message.answer(
                reg_message,
                reply_markup=get_login_kb()
            )
            await state.clear()



@router.message(UserActions.username)
async def reg_username_incorrectly(message: Message):
    await message.answer(
        text="Please correctly enter username",
        reply_markup=get_cancel_kb()

    )
@router.message(UserActions.password)
async def reg_password_incorrectly(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Please correctly enter password for {user_data['reg_username']}",
        reply_markup=get_cancel_kb()
    )
@router.message(UserActions.reg_confirm)
async def reg_password_incorrectly(message: Message):
    await message.answer(
        text=f"Please correctly confirm your password",
        reply_markup=get_cancel_kb()
    )


