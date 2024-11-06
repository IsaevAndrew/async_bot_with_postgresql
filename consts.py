import os

TOKEN = os.getenv('TOKEN')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
HYGGE_PAINT_CHANNEL = int(os.getenv('HYGGE_PAINT_CHANNEL'))
SURGAZ_CHANNEL = int(os.getenv('SURGAZ_CHANNEL'))
ARTSIMPLE_CHANNEL = int(os.getenv('ARTSIMPLE_CHANNEL'))
DB_HOST = str(os.getenv('DB_HOST'))
DB_USER = str(os.getenv('DB_USER'))
DB_PASSWORD = str(os.getenv('DB_PASSWORD'))
DB_NAME = str(os.getenv('DB_NAME'))
videos = {
    "paint": "BAACAgIAAxkBAAMLZnsrO8fhLXTaVS2h4yhgi8CDTAEAAkVMAAKP5tlLmTh6X2_eSkU1BA",
    "wallpaper": "BAACAgIAAxkBAAICU2bQ4thTJiTdXLxUhrY4uemIoA-PAAJKUQACekOJShsKjCsmza-ONQQ",
    "main": "BAACAgIAAxkBAAICUmbQ4kUcLs2qORfngjbsA3-21IgwAAJFUQACekOJSnoMP3kAAbeMQjUE"}

url = "https://portal.surgaz.ru/local/crmbot/crmbot.php"
url_for_update = "https://portal.surgaz.ru/local/crmbot/crmdealupdate.php"
LOG_FILE = "bot_errors.log"
SEND_LOG_FILE = "error.log"
ERRORS_CHAT_ID = int(os.getenv('ERRORS_CHAT_ID'))
ADMIN_ID = int(os.getenv('ADMIN_ID'))