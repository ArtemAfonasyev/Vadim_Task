
import time
from typing import KeysView
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import password as password 
import json

class Selenium_test():
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0')
        options.add_argument('log-level=INT')
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(
            options=options
        )
        self.run = True
        self.counter = 0
        self.all_info_teacher = {}

    
    def start(self):
        self.driver.get('https://rtschool.s20.online/company/1/dashboard/index')
        time.sleep(1)
        email_input = self.driver.find_element(by=By.ID, value="loginform-username")
        email_input.clear()
        email_input.send_keys(password.login_alfa_samat)
        time.sleep(0.2)
        password_input = self.driver.find_element(by=By.ID, value="loginform-password")
        password_input.clear()
        password_input.send_keys(password.password_alfa_samat)
        time.sleep(0.2)
        password_input.send_keys(Keys.ENTER)
        time.sleep(1) 

    def create_task(self,json_link,type,type_lesson):
        
        self.driver.execute_script(f"window.scrollBy(0,200)","")
        time.sleep(2)
        if type_lesson == 3:
            self.driver.find_element(by=By.XPATH, value=f'//*[@id="customer-pjax"]/div[3]/div[1]/div[2]/div/ul/li[3]/a').click() #кнопка задач
        else:
            self.driver.find_element(by=By.XPATH, value=f'//*[@id="group-pjax"]/div[2]/div[1]/div[2]/ul/li[2]/a').click() #кнопка задач
        time.sleep(2)
        if type_lesson == 3:
            self.driver.find_element(by=By.XPATH, value=f'//*[@id="taskhistory"]/div/div[2]/a').click() #кнопка добавить задачу
        else:
            self.driver.find_element(by=By.XPATH, value=f'//*[@id="tasks"]/div/div[2]/a').click() #кнопка задач
        time.sleep(2)
        self.driver.find_element(by=By.XPATH, value=f'//*[@id="w0"]/div[2]/div[2]/a').click() #кнопка выбрать из шаблона
        time.sleep(2)
        for i in range(40):
            if self.driver.find_element(by=By.XPATH, value=f'//*[@id="task-templates"]/li[{5+i}]/a').text == 'Teacher TOP: Страховка (менее 4 часов)':
                time.sleep(2)
                self.driver.find_element(by=By.XPATH, value=f'//*[@id="task-templates"]/li[{5+i}]/a').click() #кнопка с рокет коинами
                break
        time.sleep(2)
        note_tr = self.driver.find_element(by=By.XPATH, value=f'//*[@id="task-text"]') #обращение к тект полю
        time.sleep(2)
        note_text_tr = note_tr.get_attribute("value")#получение текста который был в поле
        note_tr.clear()
        time.sleep(2)

        note_tr.send_keys(f'''  
Страховка {type}

{note_text_tr}   

"Ссылка на сообщение": "{json_link['Ссылка на сообщение']}",
"Дата урока": "{json_link['Дата урока']}",
"Время урока": "{json_link['Время урока']}",
"Предмет": "{json_link['Предмет']}",
"Тип урока": "{json_link['Тип урока']}",
"Язык урока": "{json_link['Язык урока']}",
"Карточка": "{json_link['Карточка']}",
"Дата ответа педагога": "{json_link['Дата ответа педагога']}",
"Discord никнейм Педагога": "{json_link['Discord никнейм Педагога']}",
"Разница времени ответа к времени урока (минуты)": "{json_link['Разница времени ответа к времени урока (минуты)']}",
"Разница времени ответа к времени создания поста (минуты)": "{json_link['Разница времени ответа к времени создания поста (минуты)']}",
        ''')
        time.sleep(3)
        self.driver.find_element(by=By.XPATH, value=f'//*[@id="w0"]/div[3]/button[2]').click() #сохранить
        if type_lesson == 3:
            return self.driver.find_element(by=By.XPATH, value=f'//*[@id="taskhistory"]/div/div[3]/div[1]/div/table/tbody/tr[1]/td[1]/a').get_attribute('href') #кнопка задач
        else:
            return self.driver.find_element(by=By.XPATH, value=f'//*[@id="tasks"]/div/div[3]/div[1]/div/table/tbody/tr[1]/td[1]/a').get_attribute('href') #кнопка задач
        

    def check_status_lesson(self,json_link):
        try:
            if json_link['Тип урока'] == 'Рег - ГРУППА' or 'group' in json_link['Карточка']:
                for j in range(1,40): 
                    check_date = self.driver.find_element(by=By.XPATH, value=f'//*[@id="group-pjax"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/span[{j}]/small').text.split('\n')[-1]
                    if check_date == json_link['Дата урока']:
                        check_status = check_date = self.driver.find_element(by=By.XPATH, value=f'//*[@id="group-pjax"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/span[{j}]/small').get_attribute("class")
                    
                        if 'text-success' in check_status:
                            if json_link['Разница времени ответа к времени урока (минуты)'] != '':
                                if float(json_link['Разница времени ответа к времени урока (минуты)']) <= 60:
                                    return ['Урок был',self.create_task(json_link,'X2 Price',2),'Ставка * 2']
                                    # return ['Урок был','Test_link','Ставка * 2']
                                elif float(json_link['Разница времени ответа к времени урока (минуты)']) <= 240:
                                    return ['Урок был',self.create_task(json_link,'Price +2$',2),'Ставка +2$']
                                    # return ['Урок был','Test_link','Ставка +2$']
                                elif float(json_link['Разница времени ответа к времени создания поста (минуты)']) <= 15:
                                    return ['Урок был',self.create_task(json_link,'Price +1$',2),'Ставка +1$']
                                    # return ['Урок был','Test_link','Ставка +1$']
                                else:
                                    return ['Урок был','не аларм','не аларм']
                            else:
                                return ['Урок был','не прописан /set_teacher','']
                        elif 'text-muted' in check_status:
                            return ['Отмена урока','Отмена урока','Отмена урока']
                        
            for j in range(1,40):
                check_date = self.driver.find_element(by=By.XPATH, value=f'//*[@id="spongebob-container"]/div/div/form/div[3]/div[{j}]').get_attribute("data-date")
                a = f"2024-{json_link['Дата урока'].split('.')[1]}-{json_link['Дата урока'].split('.')[0]}"
                if check_date == f"2024-{json_link['Дата урока'].split('.')[1]}-{json_link['Дата урока'].split('.')[0]}":
                    check_status = self.driver.find_element(by=By.XPATH, value=f'//*[@id="spongebob-container"]/div/div/form/div[3]/div[{j}]').get_attribute("class")
                    if 'planned_paid' in check_status:
                        return ['Неотмеченный урок','Неотмеченный урок','Неотмеченный урок']
                    elif 'done' in check_status:
                        if json_link['Разница времени ответа к времени урока (минуты)'] != '':
                            if float(json_link['Разница времени ответа к времени урока (минуты)']) <= 60:
                                return ['Урок был',self.create_task(json_link,'X2 Price',3),'Ставка * 2']
                                # return ['Урок был','Test_link','Ставка * 2']
                            elif float(json_link['Разница времени ответа к времени урока (минуты)']) <= 240:
                                return ['Урок был',self.create_task(json_link,'Price +2$',3),'Ставка +2$']
                                # return ['Урок был','Test_link','Ставка +2$']
                            elif float(json_link['Разница времени ответа к времени создания поста (минуты)']) <= 15:
                                return ['Урок был',self.create_task(json_link,'Price +1$',3),'Ставка +1$']
                                # return ['Урок был','Test_link','Ставка +1$']
                            else:
                                return ['Урок был','не аларм','не аларм']
                        else:
                            return ['Урок был','не прописан /set_teacher','']
                    elif 'absence_free' in check_status:  
                        return ['Бесплатная Отмена урока','Бесплатная Отмена урока','Бесплатная Отмена урока']
                    elif 'absence_paid' in check_status:  
                        return ['Платная Отмена урока','Платная Отмена урока','Платная Отмена урока']
                    
                    elif 'archive cancelled' in check_status:
                        return ['Отмена урока','Отмена урока','Отмена урока']
        except Exception as ex:
            print('erorr',json_link['Карточка'],ex)
                
                
    def client_page(self,json_link):
        self.driver.get(json_link['Карточка'])
        time.sleep(1)
        return self.check_status_lesson(json_link)


def main_parser():
    '''
    Основной код для запуска Парсинга Альфы, возвращает список с данными, НО еще и json вам дает гавсякий случай

    Attributes
    ----------   
    link: str 
        default = https://rtschool.s20.online/company/1/lesson/index
        Ссылка для парсинга, если хотите данные по отдельному педагогу то кидайте ссылку сюда, иначе можно оставить без изменений
    '''
    selenium = Selenium_test()
    selenium.start()

    with open(fr'C:\Work\Parser_lessons\Server_Code\home\Alarm_Lessons\Json\read_alarm.json', encoding='utf-8') as fh:
        json_links = json.load(fh)
        for json_link in json_links:
            if json_links[json_link]['Статус урока'] == '' or json_links[json_link]['Статус урока'] == 'Неотмеченный урок' or json_links[json_link]['Ссылка на задачу '] == 'не прописан /set_teacher':
                try:
                    json_links[json_link]['type'] = selenium.client_page(json_links[json_link])
                except Exception as ex:
                    print('erorr main_parser',ex)

    with open(rf'C:\Work\Parser_lessons\Server_Code\home\Alarm_Lessons\Json\read_alarm_new.json', 'w', encoding='utf-8') as f:
        json.dump(json_links, f, ensure_ascii=False, indent=4)
        print('Закончил')

    

