from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton, KeyboardButton

# main = ReplyKeyboardMarkup()
# main.add(KeyboardButton('Стать оптовым партнёром')).add(
#     KeyboardButton('Направление КРАСКИ'),
#     KeyboardButton('Направление ОБОИ')).add(
#     KeyboardButton('Где купить в розницу?')).add(
#     KeyboardButton('Подписаться на видео о наших новинках.'))

main = InlineKeyboardMarkup()
main.add(InlineKeyboardButton('Стать оптовым партнёром',
                              callback_data="partner")).add(
    InlineKeyboardButton('Направление КРАСКИ',
                         callback_data="main_paints")).add(
    InlineKeyboardButton('Направление ОБОИ',
                         callback_data="main_wallpaper")).add(
    InlineKeyboardButton('Где купить в розницу?',
                         callback_data="main_retail")).add(
    InlineKeyboardButton('Подписаться на видео о наших новинках.',
                         callback_data="new_videos"))

videos = InlineKeyboardMarkup()
videos.row(
    InlineKeyboardButton("HYGGE Paint в VK", url="https://vk.com/hyggepaint"),
    InlineKeyboardButton("SURGAZ в VK", url="https://vk.com/surgaz")).row(
    InlineKeyboardButton("HYGGE Paint в Телеграм",
                         url="https://t.me/hyggepaint"),
    InlineKeyboardButton("SURGAZ в Телеграм",
                         url="https://t.me/surgaz")).row(
    InlineKeyboardButton("Вернуться в меню", callback_data="main"))

partner = InlineKeyboardMarkup()
partner.add(
    InlineKeyboardButton('Торговля обоями', callback_data="business1")).add(
    InlineKeyboardButton('Торговля красками', callback_data="business2")).add(
    InlineKeyboardButton('Отделочные работы', callback_data="business3")).add(
    InlineKeyboardButton('Дизайн интерьеров', callback_data="business4")).add(
    InlineKeyboardButton('Малярные работы', callback_data="business5")).add(
    InlineKeyboardButton('Строительная компания',
                         callback_data="business6")).add(
    InlineKeyboardButton('Другое..', callback_data="business7")).add(
    InlineKeyboardButton("Вернуться в меню и задать вопрос",
                         callback_data="main"))

yes_no = InlineKeyboardMarkup()
yes_no.row(InlineKeyboardButton("Да", callback_data="yes"),
           InlineKeyboardButton("Нет", callback_data="no"))

retail = InlineKeyboardMarkup()
retail.row(InlineKeyboardButton("Краски",
                                url="https://yandex.ru/maps/?ll=54.232452%2C53.157332&mode=usermaps&source=constructorLink&um=constructor%3A4df9cec37902e744c55095b6769efba8978894d277fcd023767ff2a2188999d3&z=5"),
           InlineKeyboardButton("Обои",
                                url="https://yandex.ru/maps/?ll=37.962640%2C56.309586&mode=usermaps&source=constructorLink&um=constructor%3A3ee9693e4b7f70d30a4532c16e7a9e935494c88f5302309ef6784d3d5589a7f1&z=6")).add(
    InlineKeyboardButton("Вернуться в меню", callback_data="main"))

back_main = InlineKeyboardMarkup()
back_main.add(InlineKeyboardButton("Вернуться в меню", callback_data="main"))

paints_main = InlineKeyboardMarkup()
paints_main.add(InlineKeyboardButton("Стать оптовым партнёром",
                                     callback_data="paint_partner")).add(
    InlineKeyboardButton(
        "Задать вопрос",
        callback_data="paint_question1")).add(
    InlineKeyboardButton("Заказать инженерные услуги",
                         callback_data="paint_engining")).add(
    InlineKeyboardButton("Подобрать краску", callback_data="quiz")).add(
    InlineKeyboardButton("Технические карты маляра",
                         callback_data="cards")).add(
    InlineKeyboardButton("Вступить в группу в VK",
                         url="https://vk.com/hyggepaint")).add(
    InlineKeyboardButton("HYGGE Paint в Телеграм",
                         url="https://t.me/hyggepaint")).add(
    InlineKeyboardButton("Вернуться в меню", callback_data="main"))

quiz_first = InlineKeyboardMarkup()
quiz_first.add(InlineKeyboardButton("Для интерьера", callback_data="in")).add(
    InlineKeyboardButton("Для экстерьера", callback_data="out"))

quiz_in = InlineKeyboardMarkup()
quiz_in.add(InlineKeyboardButton("Устойчивость к высоким температурам",
                                 callback_data="temp")).add(
    InlineKeyboardButton("Для металлических поверхностей",
                         callback_data="metal")).add(
    InlineKeyboardButton("Для деревянных поверхностей",
                         callback_data="wood")).add(
    InlineKeyboardButton("Для сухих поверхностей", callback_data="wet")).add(
    InlineKeyboardButton("Для влажных поверхностей", callback_data="dry"))

quiz_out = InlineKeyboardMarkup()
quiz_out.add(InlineKeyboardButton("Для стен и кровли", callback_data="1")).add(
    InlineKeyboardButton("Устойчивость к высоким температурам",
                         callback_data="2")).add(
    InlineKeyboardButton("Для металлических поверхностей",
                         callback_data="2")).add(
    InlineKeyboardButton("Для деревянных поверхностей",
                         callback_data="2")).add(
    InlineKeyboardButton("Для сухих поверхностей", callback_data="1")).add(
    InlineKeyboardButton("Для влажных поверхностей", callback_data="1"))

matte = InlineKeyboardMarkup()
matte.add(
    InlineKeyboardButton("Глубокоматовая 3% блеска", callback_data="3")).add(
    InlineKeyboardButton("Матовая 7% блеска", callback_data="7")).add(
    InlineKeyboardButton("Полуматовая 20 % блеска", callback_data="20"))

wallpapers_main = InlineKeyboardMarkup()
wallpapers_main.add(InlineKeyboardButton("Стать оптовым партнёром",
                                         callback_data="oboi_partner")).add(
    InlineKeyboardButton(
        "Задать вопрос",
        callback_data="oboi_question1")).add(
    InlineKeyboardButton("Получить каталог",
                         callback_data="oboi_katalog")).add(
    InlineKeyboardButton("Зарегистрироваться в приложении SURGAZ",
                         callback_data="oboi_mobile")).add(
    InlineKeyboardButton("Вступить в группу в VK",
                         url="https://vk.com/surgaz")).add(
    InlineKeyboardButton("SURGAZ в Телеграм",
                         url="https://t.me/surgaz")).add(
    InlineKeyboardButton("Вернуться в меню", callback_data="main"))

cards = InlineKeyboardMarkup()
cards.add(
    InlineKeyboardButton("Видео-формат", url="https://clck.ru/3ASBTX")).add(
    InlineKeyboardButton("PDF-формат", callback_data="pdf"))

share_phone = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
share_phone.add(
    KeyboardButton(
        text="Отправить номер телефона привязанный к этому telegram аккаунту",
        request_contact=True))
