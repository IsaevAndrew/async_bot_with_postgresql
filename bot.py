import asyncio
import re
from datetime import datetime
from urllib.parse import urlencode

import aioschedule
import phonenumbers
from aiogram.types import InputFile, ContentType
from pyrogram import Client, filters

from consts import API_ID, API_HASH, HYGGE_PAINT_CHANNEL, SURGAZ_CHANNEL, \
    ARTSIMPLE_CHANNEL

from consts import TOKEN, videos

from aiogram import Dispatcher, executor, types, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import texts
import keyboards
from db.base import Base
from db.engine import create_async_engine, get_session_maker, proceed_schema
from db.user import User, get_or_create_user, update_user_info, \
    check_registration_status, check_agrees_to_video, update_agrees_to_video, \
    get_users_agreeing_to_video, get_users_webinar_registered, update_webinar_registered, \
    get_user_info

memory = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=memory)
app = Client("SURGAZ", api_id=API_ID, api_hash=API_HASH)
session_maker = None
import requests

url = "https://portal.surgaz.ru/local/crmbot/crmbot.php"


async def init_db():
    DATABASE_URL = "postgresql+asyncpg://user:password@db/botdb"
    async_engine = create_async_engine(DATABASE_URL)
    global session_maker
    session_maker = get_session_maker(async_engine)
    await proceed_schema(async_engine, User.metadata)


async def send_one_day_before():
    users = await get_users_webinar_registered(session_maker=session_maker)
    for user in users:
        try:
            await bot.send_photo(user[0], photo=InputFile("./photos/Aster.png"),
                                 caption=f'Здравствуйте, {user[1]}!\n\nДо вебинара "[Тема вебинара]" остался всего один день! 🕒 Еще можно скорректировать свои планы, чтобы успеть на вебинар. \n\nЖдем вас [дата] в [время] по московскому времени. Мы подготовили для вас много интересного и полезного контента. Ссылка для участия: [Вставьте ссылку]. До встречи завтра!',
                                 parse_mode="html")
        except Exception as e:
            print(e)


async def send_one_hour_before():
    users = await get_users_webinar_registered(session_maker=session_maker)
    for user in users:
        try:
            await bot.send_message(user[0],
                                   f'Здравствуйте, {user[1]}!\n\nНапоминаем, что наш вебинар: "[Тема вебинара]" начнется уже через час! ⏰ Приготовьте блокнот и ручку, чтобы записать важные моменты. Не забудьте перейти по ссылке ниже. \nДо встречи на вебинаре!',
                                   parse_mode="html", reply_markup=keyboards.join_link)
        except Exception as e:
            print(e)


async def send_five_minute_before():
    users = await get_users_webinar_registered(session_maker=session_maker)
    for user in users:
        try:
            await bot.send_message(user[0],
                                   f'Здравствуйте, {user[1]}!\n\nВебинар: "[Тема вебинара]" уже начинается! 🚀 Самое время налить себе чашку кофе или чая и подготовиться к продуктивному часу.',
                                   parse_mode="html", reply_markup=keyboards.join_link)
        except Exception as e:
            print(e)


async def send_one_day_after():
    users = await get_users_webinar_registered(session_maker=session_maker)
    for user in users:
        try:
            await bot.send_message(user[0],
                                   f'Здравствуйте!\n\nСпасибо всем, кто присоединился к нашему вебинару: "[Тема вебинара]"! Если вы пропустили трансляцию или хотите пересмотреть, у нас есть отличные новости — запись вебинара уже доступна в нашем сообществе в Контакте.\n\nМы надеемся, что вебинар был полезным. Если у вас возникнут вопросы или вам потребуется дополнительная информация, вы можете задать их вашему персональному менеджеру. До новых встреч на наших мероприятиях! 🚀\n\nВы можете посмотреть запись по этой ссылке: [Ссылка на запись вебинара].',
                                   parse_mode="html")
        except Exception as e:
            print(e)


async def sch():
    aioschedule.every().thursday.at("").do(send_one_day_before)
    aioschedule.every().thursday.at("").do(send_one_hour_before)
    aioschedule.every().thursday.at("").do(send_five_minute_before)
    aioschedule.every().thursday.at("").do(send_one_day_after)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    await init_db()
    await app.start()
    # asyncio.create_task(sch())
    print("Бот успешно запущен!", datetime.now())


@app.on_message(filters=filters.channel)
async def main_parser(client, message):
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
                    print(e)
    else:
        return


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message, state: FSMContext):
    tag = ""
    if " " in message.text:
        tag = message.text.split()[-1]
    user_id = message.from_user.id
    name = message.from_user.username if message.from_user.username else '-'
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


@dp.callback_query_handler(text="main_retail")
async def retail(call: types.CallbackQuery):
    await call.message.answer(texts.retail_message,
                              reply_markup=keyboards.retail,
                              parse_mode="HTML")


@dp.callback_query_handler(text="main")
async def main_callback(call: types.CallbackQuery):
    await call.message.answer_video(video=videos["main"],
                                    caption=texts.welcome_message,
                                    reply_markup=keyboards.main,
                                    parse_mode="HTML")


async def get_last_video():
    async with Client("last_video_from_channel", api_id=API_ID,
                      api_hash=API_HASH) as get_video:
        async for post in get_video.get_chat_history(HYGGE_PAINT_CHANNEL):
            if post.video and post.caption and "#surgaz_видео" in post.caption:
                return post.id


@dp.callback_query_handler(text="new_videos")
async def new_videos(call: types.CallbackQuery):
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


@dp.callback_query_handler(text="partner")
async def partner(call: types.CallbackQuery):
    await call.message.answer_video(video=videos["main"],
                                    caption=texts.partner_message,
                                    reply_markup=keyboards.partner,
                                    parse_mode="HTML")


@dp.callback_query_handler(
    lambda call: call.data in ["business1", "business2", "business3",
                               "business4", "business5", "business6",
                               "business7"])
async def business(call: types.CallbackQuery, state: FSMContext):
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
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


@dp.callback_query_handler(text="main_paints")
async def main_paints(call: types.CallbackQuery):
    await call.message.answer_video(video=videos["paint"],
                                    reply_markup=keyboards.paints_main,
                                    parse_mode="HTML")


class Quiz(StatesGroup):
    what = State()
    requirements = State()
    matte = State()


@dp.callback_query_handler(text="quiz")
async def quiz(call: types.CallbackQuery):
    await call.message.answer(texts.quiz_message, parse_mode="HTML",
                              reply_markup=keyboards.quiz_first)
    await Quiz.what.set()


@dp.callback_query_handler(state=Quiz.what, text="out")
async def out_home(call: types.CallbackQuery):
    await call.message.answer(
        "Какие требования к фасадной матовой краске с 7% блеска?",
        reply_markup=keyboards.quiz_out)
    await Quiz.next()


@dp.callback_query_handler(state=Quiz.what, text="in")
async def in_home(call: types.CallbackQuery):
    await call.message.answer(
        "Какие требования к краске?",
        reply_markup=keyboards.quiz_in)
    await Quiz.next()


@dp.callback_query_handler(state=Quiz.requirements, text="1")
async def requirement_1(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Вам подходят краски:")
    await call.message.answer_photo(
        photo=types.InputFile("./photos/Sapphire.png"),
        caption=texts.sapphire, parse_mode="HTML")
    await call.message.answer_photo(
        photo=types.InputFile('./photos/Snefald.png'),
        caption=texts.snefald, parse_mode="HTML")
    await state.finish()
    await call.message.answer("Наш менеджер свяжется свами в ближайшее время!",
                              reply_markup=keyboards.back_main)


@dp.callback_query_handler(state=Quiz.requirements, text="2")
async def requirement_2(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Вам больше всего подходит краска:")
    await call.message.answer_photo(
        photo=types.InputFile("./photos/Sapphire.png"),
        caption=texts.sapphire, parse_mode="HTML")
    await call.message.answer("Вам также подходит краска:")
    await call.message.answer_photo(
        photo=types.InputFile('./photos/Snefald.png'),
        caption=texts.snefald, parse_mode="HTML")
    await state.finish()
    await call.message.answer("Наш менеджер свяжется свами в ближайшее время!",
                              reply_markup=keyboards.back_main)


@dp.callback_query_handler(state=Quiz.requirements)
async def requirement_in(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["requirement_text"] = call.data
    await call.message.answer(
        "С какой степенью матовости Вы бы хотели приобрести краску?",
        reply_markup=keyboards.matte, parse_mode="HTML")
    await Quiz.next()


@dp.callback_query_handler(state=Quiz.matte, text="20")
async def matte20(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Вам больше всего подходит краска:")
    await call.message.answer_photo(
        photo=types.InputFile('./photos/Snefald.png'),
        caption=texts.snefald, parse_mode="HTML")
    await call.message.answer("Вам также подходит краска:")
    await call.message.answer_photo(
        photo=types.InputFile('./photos/Shimmering sea.png'),
        caption=texts.shimmering_sea, parse_mode="HTML")
    await state.finish()
    await call.message.answer("Наш менеджер свяжется свами в ближайшее время!",
                              reply_markup=keyboards.back_main)


@dp.callback_query_handler(state=Quiz.matte, text="3")
async def matte3(call: types.CallbackQuery, state: FSMContext):
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
    await call.message.answer("Наш менеджер свяжется свами в ближайшее время!",
                              reply_markup=keyboards.back_main)


@dp.callback_query_handler(state=Quiz.matte, text="7")
async def matte7(call: types.CallbackQuery, state: FSMContext):
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
    await call.message.answer("Наш менеджер свяжется свами в ближайшее время!",
                              reply_markup=keyboards.back_main)


@dp.callback_query_handler(text="main_wallpaper")
async def main_wallpaper(call: types.CallbackQuery):
    await call.message.answer_video(video=videos["wallpaper"],
                                    reply_markup=keyboards.wallpapers_main,
                                    parse_mode="HTML")


@dp.callback_query_handler(text="oboi_partner")
async def oboi_partner(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["teg"] = "oboi_partner"
        if await check_registration_status(call.message.chat.id,
                                           session_maker=session_maker):
            await call.message.answer(
                "Персональный менеджер свяжется с Вами в течении 30 мин.",
                reply_markup=keyboards.back_main2)
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


@dp.callback_query_handler(text="oboi_katalog")
async def oboi_katalog(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["teg"] = "oboi_katalog"
        if await check_registration_status(call.message.chat.id,
                                           session_maker=session_maker):
            await call.message.answer(
                "Персональный менеджер свяжется с Вами в течении 30 мин.",
                reply_markup=keyboards.back_main2)
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


@dp.callback_query_handler(text="oboi_mobile")
async def oboi_mobile(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["teg"] = "oboi_mobile"
        if await check_registration_status(call.message.chat.id,
                                           session_maker=session_maker):
            await call.message.answer(
                "Персональный менеджер свяжется с Вами в течении 30 мин.",
                reply_markup=keyboards.back_main2)
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


class Question(StatesGroup):
    fio = State()
    phone = State()
    question = State()


@dp.callback_query_handler(text="oboi_question1")
async def oboi_question1(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите, пожалуйста, Ваше Ф.И.О.",
                              reply_markup=keyboards.back_main2)
    await Question.fio.set()
    async with state.proxy() as data:
        data["teg"] = "oboi_question1"


@dp.message_handler(state=Question.fio)
async def company(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["fio"] = message.text
    await message.answer("Введите Ваш действующий номер телефона через +",
                         reply_markup=keyboards.share_phone)
    await Question.next()


@dp.message_handler(state=Question.phone,
                    content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    async with state.proxy() as data:
        data["phone"] = phone
    await message.answer(
        "Напишите пожалуйста ваш вопрос в произвольной форме.",
        reply_markup=keyboards.back_main2,
        parse_mode='HTML')
    await Question.next()


@dp.message_handler(state=Question.phone)
async def enter_phone(message: types.Message, state: FSMContext):
    phone = message.text
    try:
        _phone = ''.join(filter(str.isdigit, phone))
        _phone = phonenumbers.parse(f'+{_phone}')
        if phonenumbers.is_valid_number(_phone):
            async with state.proxy() as data:
                data["phone"] = phone
                await message.answer(
                    "Напишите пожалуйста ваш вопрос в произвольной форме.",
                    reply_markup=keyboards.back_main2,
                    parse_mode='HTML')
                await Question.next()
        else:
            await message.answer(
                "Некорректный формат телефонного номера. Пожалуйста, введите корректный номер.")
    except Exception as e:
        await message.answer(
            "Некорректный формат телефонного номера. Пожалуйста, введите корректный номер.")


@dp.callback_query_handler(text="paint_question1")
async def paint_question1(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите, пожалуйста, Ваше Ф.И.О.",
                              reply_markup=keyboards.back_main2)
    await Question.fio.set()
    async with state.proxy() as data:
        data["teg"] = "paint_question1"


@dp.message_handler(state=Question.question)
async def question_handler(message: types.Message, state: FSMContext):
    question = message.text
    await message.answer(
        "Персональный менеджер свяжется с Вами в течении 30 мин.",
        reply_markup=keyboards.back_main2)
    await state.finish()


@dp.callback_query_handler(text="paint_engining")
async def paint_engining(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["teg"] = "paint_engining"
        if await check_registration_status(call.message.chat.id,
                                           session_maker=session_maker):
            await call.message.answer(
                "Персональный менеджер свяжется с Вами в течении 30 мин.",
                reply_markup=keyboards.back_main2)
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


@dp.callback_query_handler(text="cards")
async def cards(call: types.CallbackQuery):
    await call.message.answer("Технические карты маляра",
                              reply_markup=keyboards.cards)


@dp.callback_query_handler(text="pdf")
async def pdf(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["teg"] = "paint_partner"
        if await check_registration_status(call.message.chat.id,
                                           session_maker=session_maker):
            await call.message.answer(
                "Персональный менеджер свяжется с Вами в течении 30 мин.",
                reply_markup=keyboards.back_main2)
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


class Consulting(StatesGroup):
    agree = State()
    fio = State()
    company = State()
    phone = State()
    email = State()
    city = State()


@dp.callback_query_handler(text="paint_partner")
async def paint_partner(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["teg"] = "paint_partner"
        if await check_registration_status(call.message.chat.id,
                                           session_maker=session_maker):
            await call.message.answer(
                "Персональный менеджер свяжется с Вами в течении 30 мин.",
                reply_markup=keyboards.back_main2)
            user_info = await get_user_info(call.message.chat.id, session_maker)
            if user_info:
                info = {
                    "user_id": call.message.chat.id,
                    "username": call.message.chat.username,
                    "fio": user_info["fio"],
                    "company": user_info["company"],
                    "phone": user_info["phone"],
                    "email": user_info["email"],
                    "city": user_info["city"],
                    "comment": data["business"],
                    "teg": data['teg']
                }
                query_string = urlencode(info)
                full_url = f"{url}?{query_string}"
                requests.get(full_url)
        else:
            await Consulting.agree.set()
            await call.message.answer(texts.consultation_message,
                                      reply_markup=keyboards.yes_no,
                                      parse_mode="HTML")


@dp.callback_query_handler(state=Consulting.agree, text="no")
async def no_agree(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer_video(video=videos["main"],
                                    caption=texts.welcome_message,
                                    reply_markup=keyboards.main,
                                    parse_mode="HTML")
    await state.finish()


@dp.message_handler(state='*', text="Вернуться в меню")
async def back_main(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Вы будете возвращены в меню",
                         reply_markup=types.ReplyKeyboardRemove())
    await message.answer_video(video=videos["main"],
                               caption=texts.welcome_message,
                               reply_markup=keyboards.main,
                               parse_mode="HTML")


@dp.callback_query_handler(state=Consulting.agree, text="yes")
async def yes_agree(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите, пожалуйста, Ваше Ф.И.О.",
                              reply_markup=keyboards.back_main2)
    await Consulting.next()


@dp.message_handler(state=Consulting.fio)
async def fio(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["fio"] = message.text
    await message.answer("Введите название Вашей организации")
    await Consulting.next()


@dp.message_handler(state=Consulting.company)
async def company(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["company"] = message.text
    await message.answer("Введите Ваш действующий номер телефона через +",
                         reply_markup=keyboards.share_phone)
    await Consulting.next()


@dp.message_handler(state=Consulting.phone,
                    content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    async with state.proxy() as data:
        data["phone"] = phone
    await message.answer("Введите Ваш e-mail для работы с нами",
                         reply_markup=keyboards.back_main2,
                         parse_mode='HTML')
    await Consulting.next()


@dp.message_handler(state=Consulting.phone)
async def enter_phone(message: types.Message, state: FSMContext):
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
    except Exception as e:
        await message.answer(
            "Некорректный формат телефонного номера. Пожалуйста, введите корректный номер.")


@dp.message_handler(state=Consulting.email)
async def city(message: types.Message, state: FSMContext):
    if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                message.text):
        async with state.proxy() as data:
            data["email"] = message.text
        await message.answer("Введите Ваш город.")
        await Consulting.next()
    else:
        await message.answer(
            "Некорректный формат адреса почты. Пожалуйста, введите корректный адрес почты.")


@dp.message_handler(state=Consulting.city)
async def city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["city"] = message.text
        await update_user_info(message.from_user.id, data["fio"],
                               data["company"], data["phone"], data["email"],
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
        info = {
            "user_id": message.chat.id,
            "username": message.chat.username,
            "fio": data['fio'],
            "company": data['company'],
            "phone": data['phone'],
            "email": data['email'],
            "city": data['city'],
            "comment": data["business"],
            "teg": data['teg']
        }
        request = requests.post(url, data=info)
        print(request.text)
        await state.finish()


@dp.message_handler(content_types=ContentType.ANY)
async def error(message: types.Message):
    print(message)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
