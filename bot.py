import asyncio
import re
from datetime import datetime
import logging
import aioschedule
import phonenumbers
from aiogram.types import InputFile, ContentType
from pyrogram import Client, filters
import traceback
import os

from consts import API_ID, API_HASH, HYGGE_PAINT_CHANNEL, SURGAZ_CHANNEL, \
    ARTSIMPLE_CHANNEL, url, url_for_update, LOG_FILE, TOKEN, videos, \
    ERRORS_CHAT_ID, SEND_LOG_FILE, ADMIN_ID

from consts import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import requests

from aiogram import Dispatcher, executor, types, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import texts
import keyboards
from db.engine import create_async_engine, get_session_maker, proceed_schema
from db.user import (User, get_or_create_user, update_user_info,
                     check_registration_status, check_agrees_to_video,
                     update_agrees_to_video,
                     get_users_agreeing_to_video, get_users_webinar_registered,
                     update_webinar_registered, get_user_info)

memory = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=memory)
app = Client("SURGAZ", api_id=API_ID, api_hash=API_HASH)
session_maker = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def log_and_send_error(context, exception):
    error_message = (
        f"Error Context: {context}\n"
        f"Error Type: {type(exception).__name__}\n"
        f"Error Message: {exception}\n"
    )
    traceback = f"Traceback: {get_traceback_info()}"
    logger.error(error_message + traceback)
    with open(SEND_LOG_FILE, 'w') as log_file:
        log_file.write(error_message + traceback)
    await bot.send_document(ERRORS_CHAT_ID, InputFile(SEND_LOG_FILE),
                            caption=error_message)
    os.remove(SEND_LOG_FILE)


def get_traceback_info():
    return str(traceback.format_exc())


async def init_db():
    try:
        # DATABASE_URL = "postgresql+asyncpg://user:password@db/botdb"
        DATABASE_URL = "postgresql+asyncpg://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + "/" + DB_NAME
        async_engine = create_async_engine(DATABASE_URL)
        global session_maker
        session_maker = get_session_maker(async_engine)
        await proceed_schema(async_engine, User.metadata)
    except Exception as e:
        await log_and_send_error("Ошибка при инициализации базы данных", e)


async def send_one_day_before():
    try:
        users = await get_users_webinar_registered(session_maker=session_maker)
        for user in users:
            try:
                await bot.send_photo(user[0],
                                     photo=InputFile("./photos/Aster.png"),
                                     caption=f'Здравствуйте, {user[1]}!\n\nДо вебинара "[Тема вебинара]" остался всего один день! 🕒 Еще можно скорректировать свои планы, чтобы успеть на вебинар. \n\nЖдем вас [дата] в [время] по московскому времени. Мы подготовили для вас много интересного и полезного контента. Ссылка для участия: [Вставьте ссылку]. До встречи завтра!',
                                     parse_mode="html")
            except Exception as e:
                await log_and_send_error("Ошибка в работе бота", e)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


async def send_one_hour_before():
    try:
        users = await get_users_webinar_registered(session_maker=session_maker)
        for user in users:
            try:
                await bot.send_message(user[0],
                                       f'Здравствуйте, {user[1]}!\n\nНапоминаем, что наш вебинар: "[Тема вебинара]" начнется уже через час! ⏰ Приготовьте блокнот и ручку, чтобы записать важные моменты. Не забудьте перейти по ссылке ниже. \nДо встречи на вебинаре!',
                                       parse_mode="html",
                                       reply_markup=keyboards.join_link)
            except Exception as e:
                await log_and_send_error("Ошибка в работе бота", e)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


async def send_five_minute_before():
    try:
        users = await get_users_webinar_registered(session_maker=session_maker)
        for user in users:
            try:
                await bot.send_message(user[0],
                                       f'Здравствуйте, {user[1]}!\n\nВебинар: "[Тема вебинара]" уже начинается! 🚀 Самое время налить себе чашку кофе или чая и подготовиться к продуктивному часу.',
                                       parse_mode="html",
                                       reply_markup=keyboards.join_link)
            except Exception as e:
                await log_and_send_error("Ошибка в работе бота", e)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


async def send_one_day_after():
    try:
        users = await get_users_webinar_registered(session_maker=session_maker)
        for user in users:
            try:
                await bot.send_message(user[0],
                                       f'Здравствуйте!\n\nСпасибо всем, кто присоединился к нашему вебинару: "[Тема вебинара]"! Если вы пропустили трансляцию или хотите пересмотреть, у нас есть отличные новости — запись вебинара уже доступна в нашем сообществе в Контакте.\n\nМы надеемся, что вебинар был полезным. Если у вас возникнут вопросы или вам потребуется дополнительная информация, вы можете задать их вашему персональному менеджеру. До новых встреч на наших мероприятиях! 🚀\n\nВы можете посмотреть запись по этой ссылке: [Ссылка на запись вебинара].',
                                       parse_mode="HTML")
            except Exception as e:
                await log_and_send_error("Ошибка в работе бота", e)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


async def sch():
    try:
        aioschedule.every().thursday.at("").do(send_one_day_before)
        aioschedule.every().thursday.at("").do(send_one_hour_before)
        aioschedule.every().thursday.at("").do(send_five_minute_before)
        aioschedule.every().thursday.at("").do(send_one_day_after)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


async def on_startup(_):
    try:
        await init_db()
        await app.start()
        # asyncio.create_task(sch())
        startup_message = f"Бот успешно запущен! Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        logger.info(startup_message)
        await bot.send_message(ERRORS_CHAT_ID, startup_message)
    except Exception as e:
        await log_and_send_error("Ошибка при запуске бота", e)


@app.on_message(filters=filters.channel)
async def main_parser(client, message):
    try:
        if message.chat.id in [HYGGE_PAINT_CHANNEL, SURGAZ_CHANNEL,
                               ARTSIMPLE_CHANNEL]:
            if (message.caption and "#surgaz_видео" in message.caption) or (
                    message.text and "#surgaz_видео" in message.text):
                users = await get_users_agreeing_to_video(
                    session_maker=session_maker)
                for user in users:
                    try:
                        await bot.forward_message(user, message.chat.id,
                                                  message.id)
                    except Exception as e:
                        await log_and_send_error("Ошибка в работе бота", e)
        else:
            return
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message, state: FSMContext):
    try:
        tag = ""
        if " " in message.text:
            tag = message.text.split()[-1]
        user_id = message.chat.id
        name = message.chat.username if message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        if not tag:
            await message.answer_video(video=videos["main"],
                                       caption=texts.welcome_message,
                                       reply_markup=keyboards.main,
                                       parse_mode="HTML")
        elif tag == "webinar":
            async with state.proxy() as data:
                data["tag"] = tag
            await Consulting.agree.set()
            await message.answer(texts.webinar_start_message,
                                 reply_markup=keyboards.yes_no,
                                 parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(commands=['check'])
async def check(message: types.Message):
    if message.chat.id == ADMIN_ID:
        await message.answer("STABLE")


@dp.callback_query_handler(text="main_retail")
async def retail(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer(texts.retail_message,
                                  reply_markup=keyboards.retail,
                                  parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="main")
async def main_callback(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer_video(video=videos["main"],
                                        caption=texts.welcome_message,
                                        reply_markup=keyboards.main,
                                        parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


async def get_last_video():
    try:
        async with Client("last_video_from_channel", api_id=API_ID,
                          api_hash=API_HASH) as get_video:
            async for post in get_video.get_chat_history(HYGGE_PAINT_CHANNEL):
                if post.video and post.caption and "#surgaz_видео" in post.caption:
                    return post.id
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="new_videos")
async def new_videos(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        if not await check_agrees_to_video(call.message.chat.id,
                                           session_maker=session_maker):
            await update_agrees_to_video(user_id=call.message.chat.id,
                                         session_maker=session_maker)
        message_id = await get_last_video()
        await bot.forward_message(chat_id=call.message.chat.id,
                                  from_chat_id=HYGGE_PAINT_CHANNEL,
                                  message_id=message_id)
        await call.message.answer(texts.videos, reply_markup=keyboards.videos,
                                  parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="partner")
async def partner(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer_video(video=videos["main"],
                                        caption=texts.partner_message,
                                        reply_markup=keyboards.partner,
                                        parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(
    lambda call: call.data in ["business1", "business2", "business3",
                               "business4", "business5", "business6",
                               "business7"])
async def business(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "partner"
            business = {"business1": "Торговля обоями",
                        "business2": "Торговля красками",
                        "business3": "Отделочные работы",
                        "business4": "Дизайн интерьеров",
                        "business5": "Малярные работы",
                        "business6": "Строительная компания",
                        "business7": "Другое.."}
            data["business"] = business[call.data]
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="main_paints")
async def main_paints(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer_video(video=videos["paint"],
                                        reply_markup=keyboards.paints_main,
                                        parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


class Quiz(StatesGroup):
    what = State()
    requirements = State()
    matte = State()


@dp.callback_query_handler(text="quiz")
async def quiz(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer(texts.quiz_message, parse_mode="HTML",
                                  reply_markup=keyboards.quiz_first)
        await Quiz.what.set()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.what, text="out")
async def out_home(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer(
            "Какие требования к фасадной матовой краске с 7% блеска?",
            reply_markup=keyboards.quiz_out)
        await Quiz.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.what, text="in")
async def in_home(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer(
            "Какие требования к краске?",
            reply_markup=keyboards.quiz_in)
        await Quiz.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.requirements, text="1")
async def requirement_1(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer("Вам подходят краски:")
        await call.message.answer_photo(
            photo=types.InputFile("./photos/Sapphire.png"),
            caption=texts.sapphire, parse_mode="HTML")
        await call.message.answer_photo(
            photo=types.InputFile('./photos/Snefald.png'),
            caption=texts.snefald, parse_mode="HTML")
        await state.finish()
        await call.message.answer(
            "Наш менеджер свяжется свами в ближайшее время!",
            reply_markup=keyboards.back_main)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.requirements, text="2")
async def requirement_2(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer("Вам больше всего подходит краска:")
        await call.message.answer_photo(
            photo=types.InputFile("./photos/Sapphire.png"),
            caption=texts.sapphire, parse_mode="HTML")
        await call.message.answer("Вам также подходит краска:")
        await call.message.answer_photo(
            photo=types.InputFile('./photos/Snefald.png'),
            caption=texts.snefald, parse_mode="HTML")
        await state.finish()
        await call.message.answer(
            "Наш менеджер свяжется свами в ближайшее время!",
            reply_markup=keyboards.back_main)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.requirements)
async def requirement_in(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["requirement_text"] = call.data
        await call.message.answer(
            "С какой степенью матовости Вы бы хотели приобрести краску?",
            reply_markup=keyboards.matte, parse_mode="HTML")
        await Quiz.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.matte, text="20")
async def matte20(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer("Вам больше всего подходит краска:")
        await call.message.answer_photo(
            photo=types.InputFile('./photos/Snefald.png'),
            caption=texts.snefald, parse_mode="HTML")
        await call.message.answer("Вам также подходит краска:")
        await call.message.answer_photo(
            photo=types.InputFile('./photos/Shimmering sea.png'),
            caption=texts.shimmering_sea, parse_mode="HTML")
        await state.finish()
        await call.message.answer(
            "Наш менеджер свяжется свами в ближайшее время!",
            reply_markup=keyboards.back_main)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.matte, text="3")
async def matte3(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            if data["requirement_text"] in ["metal", "wood", "dry"]:
                await call.message.answer("Вам больше всего подходят краски:")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Snefald.png'),
                    caption=texts.snefald, parse_mode="HTML")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Silverbloom.png'),
                    caption=texts.silverbloom, parse_mode="HTML")
            else:
                await call.message.answer("Вам больше всего подходит краска:")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Snefald.png'),
                    caption=texts.snefald, parse_mode="HTML")
            if data["requirement_text"] == "wet":
                await call.message.answer("Вам также подходят краски:")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Shimmering sea.png'),
                    caption=texts.shimmering_sea, parse_mode="HTML")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Aster.png'),
                    caption=texts.aster, parse_mode="HTML")
        await state.finish()
        await call.message.answer(
            "Наш менеджер свяжется свами в ближайшее время!",
            reply_markup=keyboards.back_main)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Quiz.matte, text="7")
async def matte7(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            if data["requirement_text"] == "dry":
                await call.message.answer("Вам больше всего подходят краски:")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Snefald.png'),
                    caption=texts.snefald, parse_mode="HTML")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Fleurs.png'),
                    caption=texts.fleurs, parse_mode="HTML")
            else:
                await call.message.answer("Вам больше всего подходит краска:")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Snefald.png'),
                    caption=texts.snefald, parse_mode="HTML")
            if data["requirement_text"] in ["temp", "dry"]:
                await call.message.answer("Вам также подходит краска:")
            else:
                await call.message.answer("Вам также подходят краски:")
            await call.message.answer_photo(
                photo=types.InputFile('./photos/Obsidian.png'),
                caption=texts.obsidian, parse_mode="HTML")
            if data["requirement_text"] == "metal":
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Fleurs.png'),
                    caption=texts.fleurs, parse_mode="HTML")
            elif data["requirement_text"] in ["wood", "wet"]:
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Fleurs.png'),
                    caption=texts.fleurs, parse_mode="HTML")
                await call.message.answer_photo(
                    photo=types.InputFile('./photos/Klover.png'),
                    caption=texts.klover, parse_mode="HTML")
        await state.finish()
        await call.message.answer(
            "Наш менеджер свяжется свами в ближайшее время!",
            reply_markup=keyboards.back_main)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="main_wallpaper")
async def main_wallpaper(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer_video(video=videos["wallpaper"],
                                        reply_markup=keyboards.wallpapers_main,
                                        parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="oboi_partner")
async def oboi_partner(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "oboi_partner"
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="oboi_katalog")
async def oboi_katalog(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "oboi_katalog"
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="oboi_mobile")
async def oboi_mobile(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "oboi_mobile"
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


class Question(StatesGroup):
    question = State()


@dp.callback_query_handler(text="oboi_question1")
async def oboi_question1(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer(
            "Напишите пожалуйста ваш вопрос в произвольной форме.",
            reply_markup=keyboards.back_main2)
        await Question.question.set()
        async with state.proxy() as data:
            data["teg"] = "oboi_question1"
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="paint_question1")
async def paint_question1(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer(
            "Напишите пожалуйста ваш вопрос в произвольной форме.",
            reply_markup=keyboards.back_main2)
        await Question.question.set()
        async with state.proxy() as data:
            data["teg"] = "paint_question1"
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Question.question)
async def question_handler(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
        name = message.chat.username if message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        question = message.text
        async with state.proxy() as data:
            data["question"] = question
            if await check_registration_status(message.chat.id,
                                               session_maker=session_maker):
                await message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(message.chat.id, session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg'],
                        "question": question
                    }
                    requests.post(url_for_update, data=info)
                    await state.finish()
            else:
                await Consulting.agree.set()
                await message.answer(texts.consultation_message,
                                     reply_markup=keyboards.yes_no,
                                     parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="paint_engining")
async def paint_engining(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "paint_engining"
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="cards")
async def cards(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await call.message.answer("Технические карты маляра",
                                  reply_markup=keyboards.cards)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(text="pdf")
async def pdf(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "paint_partner"
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


class Consulting(StatesGroup):
    agree = State()
    fio = State()
    company = State()
    phone = State()
    email = State()
    city = State()


@dp.callback_query_handler(text="paint_partner")
async def paint_partner(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name = call.message.chat.username if call.message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["teg"] = "paint_partner"
            if await check_registration_status(call.message.chat.id,
                                               session_maker=session_maker):
                await call.message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
                user_info = await get_user_info(call.message.chat.id,
                                                session_maker)
                data["business"] = data["business"] if data.get(
                    "business") else ''
                if user_info:
                    info = {
                        "user_id": call.message.chat.id,
                        "comment": data["business"],
                        "teg": data['teg']
                    }
                    requests.post(url_for_update, data=info)
            else:
                await Consulting.agree.set()
                await call.message.answer(texts.consultation_message,
                                          reply_markup=keyboards.yes_no,
                                          parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Consulting.agree, text="no")
async def no_agree(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.answer_video(video=videos["main"],
                                        caption=texts.welcome_message,
                                        reply_markup=keyboards.main,
                                        parse_mode="HTML")
        await state.finish()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state='*', text="Вернуться в меню")
async def back_main(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
        name = message.chat.username if message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        await state.finish()
        await message.answer("Вы будете возвращены в меню",
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer_video(video=videos["main"],
                                   caption=texts.welcome_message,
                                   reply_markup=keyboards.main,
                                   parse_mode="HTML")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.callback_query_handler(state=Consulting.agree, text="yes")
async def yes_agree(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.answer("Введите, пожалуйста, Ваше Ф.И.О.",
                                  reply_markup=keyboards.back_main2)
        await Consulting.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Consulting.fio)
async def fio(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
        name = message.chat.username if message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
        async with state.proxy() as data:
            data["fio"] = message.text
        await message.answer("Введите название Вашей организации")
        await Consulting.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Consulting.company)
async def company(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["company"] = message.text
        await message.answer("Введите Ваш действующий номер телефона через +",
                             reply_markup=keyboards.share_phone)
        await Consulting.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Consulting.phone,
                    content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message, state: FSMContext):
    try:
        phone = message.contact.phone_number
        async with state.proxy() as data:
            data["phone"] = phone
        await message.answer("Введите Ваш e-mail для работы с нами",
                             reply_markup=keyboards.back_main2,
                             parse_mode='HTML')
        await Consulting.next()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Consulting.phone)
async def enter_phone(message: types.Message, state: FSMContext):
    try:
        phone = message.text
        try:
            _phone = ''.join(filter(str.isdigit, phone))
            _phone = phonenumbers.parse(f'+{_phone}')
            if phonenumbers.is_valid_number(_phone):
                async with state.proxy() as data:
                    data["phone"] = phone
                    await message.answer(
                        "Введите Ваш e-mail для работы с нами",
                        reply_markup=keyboards.back_main2,
                        parse_mode='HTML')
                    await Consulting.next()
            else:
                await message.answer(
                    "Некорректный формат телефонного номера. Пожалуйста, введите корректный номер.")
        except Exception:
            await message.answer(
                "Некорректный формат телефонного номера. Пожалуйста, введите корректный номер.")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Consulting.email)
async def city(message: types.Message, state: FSMContext):
    try:
        if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                    message.text):
            async with state.proxy() as data:
                data["email"] = message.text
            await message.answer("Введите Ваш город.")
            await Consulting.next()
        else:
            await message.answer(
                "Некорректный формат адреса почты. Пожалуйста, введите корректный адрес почты.")
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(state=Consulting.city)
async def city(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["city"] = message.text
            await update_user_info(message.from_user.id, data["fio"],
                                   data["company"], data["phone"],
                                   data["email"],
                                   data["city"], session_maker=session_maker)
            if not data.get("tag"):
                await message.answer(
                    "Персональный менеджер свяжется с Вами в течении 30 мин.",
                    reply_markup=keyboards.back_main2)
            else:
                await message.answer(
                    f'Здравствуйте, {data["fio"]}!\nСпасибо, что проявили интерес к нашему вебинару: "". Этот чат-бот напомнит вам о предстоящем мероприятии. Чтобы наши сообщения не затерялись, закрепите этот чат вверху списка. Ближе к дате мы пришлем вам ссылку. \n\nДля комфортного просмотра вебинара и возможности задавать вопросы, подпишитесь на наше сообщество в Контакте.',
                    reply_markup=keyboards.vk_link)
                await update_webinar_registered(user_id=message.chat.id,
                                                session_maker=session_maker)
            if not data.get("business"):
                data["business"] = data["tag"] if data.get("tag") else ''
            data["question"] = data["question"] if data.get("question") else ''
            user_info = await get_user_info(message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": message.chat.id,
                    "username": message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg'],
                    "question": data["question"]
                }
                requests.post(url, data=info)
            await state.finish()
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.message_handler(content_types=ContentType.ANY)
async def error(message: types.Message):
    try:
        user_id = message.chat.id
        name = message.chat.username if message.chat.username else '-'
        await get_or_create_user(user_id, name, session_maker=session_maker)
    except Exception as e:
        await log_and_send_error("Ошибка в работе бота", e)


@dp.errors_handler()
async def handle_errors(update, exception):
    await log_and_send_error("Возникла ошибка в обработке", exception)
    return True


if __name__ == "__main__":
    try:
        logger.info("Запуск бота")
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    except Exception as e:
        asyncio.run(log_and_send_error("Ошибка при запуске", e))
