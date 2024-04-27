import datetime
import gspread
import json
import password as password
from gspread_formatting import *

def read_info_lessons():

    gc = gspread.service_account(filename=password.path_key_google)
    sh = gc.open("Alarm Lessons")
    worksheet = sh.worksheet("Analytics")
    all_values = worksheet.get_all_values()
    return_json = {}
    for lesson in all_values[1:]:
        return_json[lesson[6]] = {
            all_values[0][0] : lesson[0],
            all_values[0][1] : lesson[1],
            all_values[0][2] : lesson[2],
            all_values[0][3] : lesson[3],
            all_values[0][4] : lesson[4],
            all_values[0][5] : lesson[5],
            all_values[0][6] : lesson[6].replace('teacher','company'),
            all_values[0][7] : lesson[7],
            all_values[0][8] : lesson[8],
            all_values[0][9] : lesson[9].split('.')[0],
            all_values[0][10] : lesson[10],
            all_values[0][11] : lesson[11],
            all_values[0][12] : lesson[12],
            all_values[0][12] : lesson[12],
            all_values[0][13] : lesson[13],
            all_values[0][14] : lesson[14],
        }
    with open(r'C:\Work\Parser_lessons\Server_Code\home\Alarm_Lessons\Json\read_alarm.json', 'w', encoding='utf-8') as f:
        json.dump(return_json, f, ensure_ascii=False, indent=4)
        print('Закончил')
    return return_json  

