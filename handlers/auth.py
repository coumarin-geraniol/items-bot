from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from database.database import check_credentials_and_update_tg_id, is_user_registered
from handlers.fsm import UserActions
from keyboards.keyboards import get_cancel_kb, get_login_kb, get_type_kb

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    if await is_user_registered(message.from_user.id):
        # Пользователь зарегистрирован, перенаправляем к каталогу
        await message.answer("Welcome back! Please select the type of cargo", reply_markup=get_type_kb())
        await state.set_state(UserActions.is_auth)
    else:
        # Пользователь не зарегистрирован, начинаем процесс регистрации
        await state.clear()
        await message.answer(
            text="Hello. First, log in or register.",
            reply_markup=get_login_kb()
        )
        await state.set_state(UserActions.username)


@router.message(F.text.lower() == "login")
@router.message(Command(commands=["login"]))
async def cmd_login(message: Message, state: FSMContext):
    if await is_user_registered(message.from_user.id):
        # Пользователь зарегистрирован, перенаправляем к каталогу
        await message.answer("Welcome back! Please select the type of cargo", reply_markup=get_type_kb())
        await state.set_state(UserActions.is_auth)
    else:
        # Пользователь не зарегистрирован, начинаем процесс регистрации
        await state.clear()
        await message.answer(
            text="Hello. First, log in. Please enter your username.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(UserActions.username)


@router.message(F.text.lower() == "register")
@router.message(Command(commands=["register"]))
async def cmd_register(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Hello. First, register in. Please enter username.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserActions.reg_username)





@router.message(UserActions.username, F.text)
async def cmd_password(message: Message, state: FSMContext):
    await state.update_data(username=message.text.lower())
    await message.answer(
        text=f"Now enter your password for user: {message.text.lower()}",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(UserActions.password)


@router.message(UserActions.username)
async def username_incorrectly(message: Message):
    await message.answer(
        text="Please enter your username",
        reply_markup=get_cancel_kb()
    )


@router.message(UserActions.password, F.text)
async def cmd_auth(message: Message, state: FSMContext):
    await state.update_data(password=message.text.lower())
    user_data = await state.get_data()
    username = user_data['username']
    password = message.text.lower()
    tg_id = message.from_user.id
    tg_username = message.from_user.username
    if check_credentials_and_update_tg_id(username, password, tg_id, tg_username):
        await message.answer(
            "You are successfully authenticated."
        )
        await message.answer(
            "Please select the package type",
            reply_markup=get_type_kb()
        )
        await state.set_state(UserActions.is_auth)
    else:
        await message.answer(
            "Incorrect username or password. Please try again.",
            reply_markup=get_login_kb()
        )
        await state.clear()


@router.message(UserActions.password)
async def password_incorrectly(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Please enter your password for user: {user_data['username']}",
        reply_markup=get_cancel_kb()
    )


@router.message(StateFilter(None))
@router.message(default_state, F.text)
async def cmd_none(message: Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text="Please press button Log in or Register.",
        reply_markup=get_login_kb()
    )