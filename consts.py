import os

TOKEN = os.getenv('TOKEN')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
HYGGE_PAINT_CHANNEL = int(os.getenv('HYGGE_PAINT_CHANNEL'))
SURGAZ_CHANNEL = int(os.getenv('SURGAZ_CHANNEL'))
ARTSIMPLE_CHANNEL = int(os.getenv('ARTSIMPLE_CHANNEL'))
videos = {
    "paint": "BAACAgIAAxkBAAMLZnsrO8fhLXTaVS2h4yhgi8CDTAEAAkVMAAKP5tlLmTh6X2_eSkU1BA",
    "wallpaper": "BAACAgIAAxkBAAICU2bQ4thTJiTdXLxUhrY4uemIoA-PAAJKUQACekOJShsKjCsmza-ONQQ",
    "main": "BAACAgIAAxkBAAICUmbQ4kUcLs2qORfngjbsA3-21IgwAAJFUQACekOJSnoMP3kAAbeMQjUE"}
