import json
import requests
from bs4 import BeautifulSoup
import fake_useragent
from datetime import datetime, timedelta

import gspread
from google.oauth2 import service_account
import re
import csv
import threading

import time
import concurrent.futures
header = {
        'user-agent': fake_useragent.UserAgent().random
    }
data = {
        'LoginForm[username]': 'rtschool.data@gmail.com',
        'LoginForm[password]': '40VDAwu3P4'
    }

session = requests.Session()

def get_html(link):
    response = session.get(link)
    return response.text

def get_data_col_seq(response, target_text):
    # Создаем объект BeautifulSoup
    soup = BeautifulSoup(response, 'lxml')

    # Находим элемент с указанным текстом внутри тега "th"
    target_th = soup.find('th', string=target_text)
    data_col_seq = None

    if target_th:
        # Получаем значение атрибута data-col-seq
        data_col_seq = target_th.get('data-col-seq')
    return data_col_seq

def get_country_stud(link):
    response = session.get(link).text
    soup = BeautifulSoup(response, "lxml")
    rows = soup.find_all('div', class_='row')
    country_text = ""
    # Проходим по найденным элементам и проверяем, содержат ли они текст "Страна"
    for row in rows:
        if "Страна" in row.get_text():
            # Если текст "Страна" найден, вытаскиваем текст из соответствующего <div>
            country_element = row.find('div', class_='col-xs-7')
            country_text = country_element.get_text(strip=True)
    return country_text

def get_old_stud(link):
    response = session.get(link).text
    soup = BeautifulSoup(response, "lxml")
    rows = soup.find_all('div', class_='row')
    country_text = ""
    # Проходим по найденным элементам и проверяем, содержат ли они текст "Возраст"
    for row in rows:
        if "Возраст" in row.get_text():
            # Если текст "Возраст" найден, вытаскиваем текст из соответствующего <div>
            country_element = row.find('div', class_='col-xs-7')
            country_text = country_element.get_text(strip=True)
    return country_text

def get_name_stud(link):
    response = session.get(link).text
    soup = BeautifulSoup(response, "lxml")
    rows = soup.find_all('div', class_='row')
    country_text = ""
    # Проходим по найденным элементам и проверяем, содержат ли они текст "ИМЯ ребёнка"
    for row in rows:
        if "ИМЯ ребёнка" in row.get_text():
            # Если текст "ИМЯ ребёнка" найден, вытаскиваем текст из соответствующего <div>
            country_element = row.find('div', class_='col-xs-7')
            country_text = country_element.get_text(strip=True)
    return country_text

def get_language_stud(link):
    response = session.get(link).text
    soup = BeautifulSoup(response, "lxml")
    rows = soup.find_all('div', class_='row')
    country_text = ""
    # Проходим по найденным элементам и проверяем, содержат ли они текст "Язык (проведения урока)"
    for row in rows:
        if "Язык (проведения урока)" in row.get_text():
            # Если текст "ИМЯ ребёнка" найден, вытаскиваем текст из соответствующего <div>
            country_element = row.find('div', class_='col-xs-7')
            country_text = country_element.get_text(strip=True)
    return country_text

def init_gs(sheet_id, sheet_name):
    # Путь к вашему JSON-файлу с ключом аутентификации
    credentials = service_account.Credentials.from_service_account_file(
        'config/key2.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets'])
    # Авторизация с использованием учетных данных
    client = gspread.authorize(credentials)
    # Определение идентификатора таблицы и листа
    # Открытие нужного листа по названию
    worksheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    return worksheet

def is_session_valid(response_text):
    return 'Мои данные | ALFACRM' in response_text

def keep_alive_session(session, data, headers):
    while True:
        response = session.post("https://rtschool.s20.online/login", data=data, headers=headers)
        if is_session_valid(response.text):
            print("Session is still alive!")
        else:
            print("Session expired! Logging in again...")
            alfa_login(session, data, headers)
        time.sleep(300)  # проверка каждые 5 минут

def alfa_login(session, data, headers):
    print("Attempting to log in...")  # Отладочный вывод
    response = session.post("https://rtschool.s20.online/login", data=data, headers=headers)
    if is_session_valid(response.text):

        print("Login successful")
    else:
        print('Wrong')
    return response.text

def cut_name(name):
    pattern = r'П[^,]*'
    matches = re.findall(pattern, name)
    result = ', '.join(matches)
    if result == "":
        return "НЕ СТОИТ П"
    else:
        return result

#дата за day до сегодняшненей. Пример: day = 3 Сегодня 12.08, day_before = 9.08
def day_before(day):
    current_date = datetime.now()
    before_date = current_date - timedelta(days=day)
    day_before = before_date.strftime("%d.%m.%Y")
    return day_before

#Получаем строчку со всеми полями
def get_teacher(name):
    link = f"https://rtschool.s20.online/company/1/employee/index"
    data = {
        "TeacherSearch[f_name]": f"{name}"
    }
    response = session.get(link, params=data, headers=header).text
    soup = BeautifulSoup(response, "lxml")
    return soup

def get_column(soup, num):
    column = soup.find('td', {'data-col-seq': str(num)})
    if column is not None:
        return column
    else:
        return None


def save_to_csv(data_list, filename="output.csv", headers_type="feedback"):
    # Заголовки для CSV
    headers_mapping = {
        "feedback": ["Дата", "Номер урока", "Педагог", "Имя клиента", "Ссылка", "Тимлид"],
        "unmarked": ["Дата", "Время", "Педагог", "Имя клиента", "Ссылка", "Тимлид"],
        "cancel": ["Дата", "Время", "Предмет", "Педагог", "Клиент", "Ссылка", "Причина отмены", "Тимлид"]
    }
    headers = headers_mapping.get(headers_type)
    if headers is None:
        raise ValueError("Invalid headers_type specified.")

    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Запись заголовков
        writer.writerows(data_list)  # Запись данных
    return filename


def save_to_json(data_list, file_path, format_type="feedback"):
    # Определение словарей форматов
    formats = {
        "feedback": ["Дата", "Номер урока", "Педагог", "Имя клиента", "Ссылка", "Тимлид"],
        "unmarked": ["Дата", "Время", "Педагог", "Клиент", "Ссылка", "Тимлид"],
        "cancel": ["Дата", "Время", "Предмет", "Педагог", "Клиент", "Ссылка", "Причина отмены", "Тимлид"]
    }

    chosen_format = formats[format_type]
    data_dicts = [{key: value for key, value in zip(chosen_format, row)} for row in data_list]

    # Сохранение в JSON-файл
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_dicts, json_file, ensure_ascii=False, indent=4)

def json_to_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_username(name):
    teacher = get_teacher(name)
    username = get_column(teacher, alfa_username_ds)
    if username is not None:
        return username.text
    else:
        return name + " is not valid"

def not_feedback(lesson_num, ot, do = 1):
    link = "https://rtschool.s20.online/company/1/lesson/index"
    data = {
        "LessonSearch[f_date_from]": f"{day_before(ot)}",#от
        "LessonSearch[f_date_to]": f"{day_before(do)}", #до (вкл)
        "LessonSearch[f_status]": '3', #проведен
        "LessonSearch[f_is_customer_attend]": '2', #посетил урок (да)
        "LessonSearch[f_custom_tema]": f'{lesson_num}', #номер урока
        "LessonSearch[f_custom_obratnayasvyaz]": '0',   #галочка ОС не поставлена
        "pageSize": 5000 #5к результатов
    }

    response = session.get(link, params=data, headers=header).text
    soup = BeautifulSoup(response, "lxml")


    tbody = soup.find('tbody')
    if tbody is not None:
        block = tbody.find_all('tr')
    else:
        print("No lesson data found for the specified date.")
        return

    data_list = []

    for row in block:
        date_td = get_column(row, alfa_date)
        if date_td is not None:
            date = date_td.text.strip()
        else:
            continue

        client_td = get_column(row, alfa_student_name)
        if client_td is not None:
            client_name_element = client_td.find('span', {'class': 'text-primary'})
            if client_name_element is not None:
                client_name = client_name_element.text.strip()
            else:
                client_name = "N/A"

            client_link = client_td.find('a', {'class': 'm-r-xs'})
            if client_link is not None:
                client_link = client_link['href']
                end_index = client_link.find("&", client_link.find("/company/1/customer/view?id="))
                desired_part = client_link[:end_index].replace("/company", "https://rtschool.s20.online/company")
            else:
                desired_part = "N/A"
        else:
            client_name = "N/A"
            desired_part = "N/A"

        lesson_number = get_column(row, alfa_number_lesson)
        if lesson_number is not None:
            lesson_number =  lesson_number.text.strip()
        teacher_info = get_column(row, alfa_teacher)
        if teacher_info is not None:
            teacher_info = teacher_info.text.strip()

        timlid = get_column(get_teacher(teacher_info), alfa_team_lead)
        if timlid is not None:
            timlid = timlid.text.strip()

        data_list.append([date, lesson_number, teacher_info, client_name, desired_part, timlid])
    return data_list

def unmarked_lessons(ot, do = 1):
    link = "https://rtschool.s20.online/company/1/lesson/index"
    data = {
        "LessonSearch[f_date_from]": f"{day_before(ot)}",#от
        "LessonSearch[f_date_to]": f"{day_before(do)}",#до (вкл)
        "LessonSearch[f_status]": '1', # статус урока (запланирован(1), проведен(3), отменен(2))
        "pageSize": 5000 #количество строк
    }

    response = session.get(link, params=data, headers=header).text
    soup = BeautifulSoup(response, "lxml")

    tbody = soup.find('tbody')
    if tbody is not None:
        block = tbody.find_all('tr')
    else:
        print("No lesson data found for the specified date.")
        return

    data_list = []

    for row in block:

        date_td = get_column(row, alfa_date)
        if date_td is not None:
            date = date_td.text.strip()
        else:
            continue

        time_td = get_column(row, alfa_time)
        if time_td is not None:
            time = time_td.text.strip()
        else:
            continue

        client_td = get_column(row, alfa_student_name)
        if client_td is not None:
            client_name_element = client_td.find('span', {'class': 'text-warning'})
            if client_name_element is not None:
                client_name = client_name_element.text.strip()
            else:
                client_name = "N/A"

            client_link = client_td.find('a', {'class': 'm-r-xs'})
            if client_link is not None:
                client_link = client_link['href']
                end_index = client_link.find("&", client_link.find("/company/1/customer/view?id="))
                desired_part = client_link[:end_index].replace("/company", "https://rtschool.s20.online/company")
            else:
                continue
        else:
            client_name = "N/A"
            desired_part = "N/A"

        teacher_info = get_column(row, alfa_teacher)
        if teacher_info is not None:
            teacher_info = cut_name(teacher_info.text.strip())

        timlid = get_column(get_teacher(teacher_info), alfa_team_lead)
        if timlid is not None:
            timlid = timlid.text.strip()

        data_list.append([date, time, teacher_info, client_name, desired_part, timlid])

    return data_list

def cancel_lessons(ot, do = 1):
    link = "https://rtschool.s20.online/company/1/lesson/index"
    data = {
        "LessonSearch[f_date_from]": f"{day_before(ot)}",#от
        "LessonSearch[f_date_to]": f"{day_before(do)}",#до (вкл)
        "LessonSearch[f_status]": '2', # статус урока (запланирован(1), проведен(3), отменен(2))
        "pageSize": 5000
    }

    response = session.get(link, params=data, headers=header).text
    soup = BeautifulSoup(response, "lxml")
    tbody = soup.find('tbody')

    if tbody is not None:
        block = tbody.find_all('tr')
    else:
        print("No lesson data found for the specified date.")
        return

    data_list = []
    date= ""
    time= ""
    subj= ""
    desired_part= ""

    for row in block:
        date_td = get_column(row, alfa_date)
        if date_td is not None:
            date = date_td.text.strip()

        time_td = get_column(row, alfa_time)
        if time_td is not None:
            time = time_td.text.strip()


        subj_td = get_column(row, alfa_subj_ls)
        if subj_td is not None:
            subj = subj_td.text.strip()


        client_td = get_column(row, alfa_student_name)
        if client_td is not None:
            client_name_element = client_td.find('span', {'class': 'text-warning'})
            if client_name_element is not None:
                client_name = client_name_element.text.strip()
            else:
                client_name = "N/A"

            client_link = client_td.find('a', {'class': 'm-r-xs'})
            if client_link is not None:
                client_link = client_link['href']
                end_index = client_link.find("&", client_link.find("/company/1/customer/view?id="))
                desired_part = client_link[:end_index].replace("/company", "https://rtschool.s20.online/company")
        else:
            client_name = "N/A"
            desired_part = "N/A"

        teacher_info = get_column(row, alfa_teacher)
        if teacher_info is not None:
            teacher_info = cut_name(teacher_info.text)

        timlid = get_column(get_teacher(teacher_info), alfa_team_lead)
        if timlid is not None:
            timlid = timlid.text.strip()

        cancel_cause_td = get_column(row, alfa_reason_cancel_text)
        cancel_cause = ""
        if cancel_cause_td is not None:
            cancel_cause = cancel_cause_td.text.strip()

        data_list.append([date, time, subj,  teacher_info, client_name, desired_part, cancel_cause, timlid])

    return data_list


def not_feedback_cmd(ot, do=1):
    numbers = [2] + list(range(4, 33, 4))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda number: not_feedback(number, ot, do), numbers)

    return [item for sublist in results for item in sublist]


def unloading(period="DAILY"):

    sheet_id = '1dKp6_903LI9uoR-X4ndImDtoHIeRqK2VRP4_Xti-7eg'

    days = 1 if period == "DAILY" else 7

    headers_mapping = {
        "feedback": ["Дата", "Номер урока", "Педагог", "Имя клиента", "Ссылка", "Тимлид"],
        "unmarked": ["Дата", "Время", "Педагог", "Клиент", "Ссылка", "Тимлид"],
        "cancel": ["Дата", "Время", "Предмет", "Педагог", "Клиент", "Ссылка", "Причина отмены", "Тимлид"]
    }

    data_mappings = [
        {"list_name": f"OC {period}", "data_function": not_feedback_cmd, "file_type": "feedback"},
        {"list_name": f"unmarked {period}", "data_function": unmarked_lessons, "file_type": "unmarked"},
        {"list_name": f"cancel {period}", "data_function": cancel_lessons, "file_type": "cancel"}
    ]

    for mapping in data_mappings:
        worksheet = init_gs(sheet_id, mapping["list_name"])
        worksheet.clear()

        # Добавляем заголовки
        headers = headers_mapping[mapping["file_type"]]
        worksheet.append_row(headers)

        # Добавляем данные
        data_list = mapping["data_function"](days)
        if period == "DAILY":
            save_to_json(data_list, mapping["file_type"] + ".json", mapping["file_type"])
        worksheet.append_rows(data_list)

def get_teacher_ds(discord):
    link = f"https://rtschool.s20.online/company/1/employee/index"
    data = {
        "TeacherSearch[f_custom_nikvdiscord]" : f"{discord}"
    }
    response = session.get(link, params=data, headers=header).text
    soup = BeautifulSoup(response, "lxml")
    return soup

def get_teamlead(discord):
    timlid = get_column(get_teacher_ds(discord), alfa_team_lead)
    if timlid is not None:
        return timlid.text.strip()
    else:
        return None

def restart_session():
    alfa_login(session, data, header)  # Первоначальный вход в систему
    link_teacher = get_html("https://rtschool.s20.online/company/1/employee/index?page=10&sort=branch_ids")
    # teachers column
    global alfa_alfa_id
    alfa_alfa_id = get_data_col_seq(link_teacher, "ID")
    global alfa_name
    alfa_name = get_data_col_seq(link_teacher, "ФИО")  # 2
    global alfa_subj
    alfa_subj = get_data_col_seq(link_teacher, "Квалификация")  # 6
    global alfa_contact
    alfa_contact = get_data_col_seq(link_teacher, "Контакты")  # 7
    global alfa_notion
    alfa_notion = get_data_col_seq(link_teacher, "Примечание")  # 8
    global alfa_username_ds
    alfa_username_ds = get_data_col_seq(link_teacher, "Тег в Discord")  # 10
    global alfa_mentor
    alfa_mentor = get_data_col_seq(link_teacher, "Наставник")  # 11
    global alfa_ovz
    alfa_ovz = get_data_col_seq(link_teacher, "Готов работать с ОВЗ")  # 12
    global alfa_team_lead
    alfa_team_lead = get_data_col_seq(link_teacher, "Teacher Team lead")  # 13
    global alfa_english_lvl
    alfa_english_lvl = get_data_col_seq(link_teacher, "English")  # 20
    global alfa_work_begin
    alfa_work_begin = get_data_col_seq(link_teacher, "Начало работы")  # 2
    # lessons column
    link_lessons = get_html("https://rtschool.s20.online/company/1/lesson/index?sort=custom_otmenameneechasov")
    global alfa_date
    alfa_date = get_data_col_seq(link_lessons, "Дата")  # 2
    global alfa_gpu_count
    alfa_gpu_count = get_data_col_seq(link_lessons, "ГПУ. Кол-во уч")  # 2
    global alfa_time
    alfa_time = get_data_col_seq(link_lessons, "Время")  # 3
    global alfa_number_lesson
    alfa_number_lesson = get_data_col_seq(link_lessons, "№ темы")  # 4
    global alfa_subj_ls
    alfa_subj_ls = get_data_col_seq(link_lessons, "Предмет")  # 5
    global alfa_comment_ls
    alfa_comment_ls = get_data_col_seq(link_lessons, "Комментарий")  # 6
    global alfa_student_name
    alfa_student_name = get_data_col_seq(link_lessons, "Участники")  # 7
    global alfa_teacher
    alfa_teacher = get_data_col_seq(link_lessons, "Педагог(и)")  # 8
    global alfa_status
    alfa_status = get_data_col_seq(link_lessons, "Статус")  # 9
    global alfa_alfa_course
    alfa_alfa_course = get_data_col_seq(link_lessons, "Курс")  # 10
    global alfa_video_ls
    alfa_video_ls = get_data_col_seq(link_lessons, "Запись урока")  # 11
    global alfa_lang
    alfa_lang = get_data_col_seq(link_lessons, "Язык")  # 12
    global alfa_reason_cancel_text
    alfa_reason_cancel_text = get_data_col_seq(link_lessons, "Причина отмены")  # 13
    global alfa_feedback_do
    alfa_feedback_do = get_data_col_seq(link_lessons, "Обратная связь родителю дана")  # 17
    global alfa_homework_do
    alfa_homework_do = get_data_col_seq(link_lessons, "Сдал ДЗ за прошлый урок")  # 18
    global alfa_homework_text
    alfa_homework_text = get_data_col_seq(link_lessons, "Домашнее задание")  # 21
    print("Перезагрузил короче, должно быть гуд")

alfa_login(session, data, header)  # Первоначальный вход в систему
  # Первоначальный вход в систему

# Затем запускайте keep_alive_session в фоновом режиме
thread = threading.Thread(target=keep_alive_session, args=(session, data, header))
thread.daemon = True
thread.start()

link_teacher = get_html("https://rtschool.s20.online/company/1/employee/index?page=10&sort=branch_ids")
#teachers column
alfa_alfa_id = get_data_col_seq(link_teacher, "ID") #1
alfa_name = get_data_col_seq(link_teacher,"ФИО") #2
alfa_subj = get_data_col_seq(link_teacher, "Квалификация") #6
alfa_contact = get_data_col_seq(link_teacher, "Контакты") #7
alfa_notion = get_data_col_seq(link_teacher, "Примечание") #8
alfa_username_ds = get_data_col_seq(link_teacher, "Тег в Discord") #10
alfa_mentor = get_data_col_seq(link_teacher, "Наставник") #11
alfa_ovz = get_data_col_seq(link_teacher, "Готов работать с ОВЗ") #12
alfa_team_lead = get_data_col_seq(link_teacher, "Teacher Team lead") #13
alfa_english_lvl = get_data_col_seq(link_teacher, "English") #20
alfa_work_begin = get_data_col_seq(link_teacher, "Начало работы") #23

#lessons column
link_lessons = get_html("https://rtschool.s20.online/company/1/lesson/index?sort=custom_otmenameneechasov")
alfa_date = get_data_col_seq(link_lessons,"Дата") #2
alfa_gpu_count = get_data_col_seq(link_lessons,"ГПУ. Кол-во уч") #2
alfa_time = get_data_col_seq(link_lessons,"Время") #3
alfa_number_lesson = get_data_col_seq(link_lessons,"№ темы") #4
alfa_subj_ls = get_data_col_seq(link_lessons,"Предмет") #5
alfa_comment_ls = get_data_col_seq(link_lessons,"Комментарий") #6
alfa_student_name = get_data_col_seq(link_lessons,"Участники") #7
alfa_teacher = get_data_col_seq(link_lessons,"Педагог(и)") #8
alfa_status = get_data_col_seq(link_lessons,"Статус") #9
alfa_alfa_course = get_data_col_seq(link_lessons,"Курс") #10
alfa_video_ls = get_data_col_seq(link_lessons,"Запись урока") #11
alfa_lang = get_data_col_seq(link_lessons,"Язык") #12
alfa_reason_cancel_text = get_data_col_seq(link_lessons,"Причина отмены") #13
alfa_feedback_do = get_data_col_seq(link_lessons,"Обратная связь родителю дана") #17
alfa_homework_do = get_data_col_seq(link_lessons,"Сдал ДЗ за прошлый урок") #18
alfa_homework_text = get_data_col_seq(link_lessons,"Домашнее задание") #21

print("Start")



