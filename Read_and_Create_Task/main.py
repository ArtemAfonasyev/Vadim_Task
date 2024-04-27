import datetime
import time
import parser_lessons
import read_sheets
import update_sheets

while True:
    timezone_offset = +3.0  # Pacific Standard Time (UTC−08:00)
    tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))
    date_now = datetime.datetime.now(tzinfo)
    day_end = date_now - datetime.timedelta(1)
    try:
        read_sheets.read_info_lessons()

        parser_lessons.main_parser()

        update_sheets.update_info_lessons()
        print('Завершил програму')
        time.sleep(60*60*24)
    except Exception as ex:
        print('erorr Main',ex)
        time.sleep(60*45)

    