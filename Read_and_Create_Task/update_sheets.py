import datetime
import gspread
import json
import password as password
import time
def update_info_lessons():

    gc = gspread.service_account(filename=password.path_key_google)
    sh = gc.open("Alarm Lessons")
    worksheet = sh.worksheet("Analytics")

    with open(fr'C:\Work\Parser_lessons\Server_Code\home\Alarm_Lessons\Json\read_alarm_new.json', encoding='utf-8') as fh:
        json_links = json.load(fh)

        
        
    count = 0
    for link in json_links:
        if 'type' in json_links[link] and json_links[link]['type'] != None:
            cell_list = worksheet.findall(json_links[link]["Ссылка на сообщение"])
            a = f'M{cell_list[0].row}:O{cell_list[0].row}'
           
            worksheet.update(f'M{cell_list[0].row}:O{cell_list[0].row}', [json_links[link]['type']])
        if count % 80 == 0:
            time.sleep(60)
        count += 1
        print(count)