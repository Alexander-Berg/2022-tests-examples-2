# coding: utf-8

from mylib import hahn, send_mail
import pandas as pd
import StringIO
import pymongo
import requests
from datetime import datetime, timedelta
import os
from openpyxl import load_workbook

from startrek_client import Startrek


hahn.base_path = 'home/taxi-analytics/iafilimonov/{}'

url = 'https://st-api.yandex-team.ru'
client = Startrek(useragent='python client', base_url=url, token='AQAD-qJSJwKvAAADvpOrl2idpkNcvOlEp2UNeVU')
issue = client.issues['TAXIANALYTICS-3963']


deal_owners = pd.DataFrame([
#     {'name': u'Марина Абгарян', 'email': 'abgaryan@yandex-team.ru'},
#     {'name': u'Татьяна Алешина', 'email': 'aleshinat@yandex-team.ru'},
#     {'name': u'Олеся Амосова', 'email': 'amosova@yandex-team.ru'},
#     {'name': u'Светлана Ацеховская', 'email': 'svetlana-ats@yandex-team.ru'},
#     {'name': u'Ксения Блощинская', 'email': 'ksbl@yandex-team.ru'},
#     {'name': u'Ольга Бокова', 'email': 'bokova@yandex-team.ru'},
#     {'name': u'Виктор Борзенко', 'email': 'vborzenko@yandex-team.ru'},
#     {'name': u'Юрий Бочкарев', 'email': 'bochkariov@yandex-team.ru'},
#     {'name': u'Вера Ветютнева', 'email': 'vetyutneva@yandex-team.ru'},
#     {'name': u'Александра Гончарова', 'email': 'aleksandra-g@yandex-team.ru'},
#     {'name': u'Анастасия Гончарова', 'email': 'av-goncharova@yandex-team.ru'},
#     {'name': u'Татьяна Григорьева', 'email': 'tatiana-gr@yandex-team.ru'},
#     {'name': u'Эльдар Даутов', 'email': 'dautov@yandex-team.ru'},
#     {'name': u'Ольга Демьянова', 'email': 'demianova@yandex-team.ru'},
#     {'name': u'Анна Денисенко', 'email': 'denisenko-an@yandex-team.ru'},
#     {'name': u'Андрей Долгий', 'email': 'dolgiy@yandex-team.ru'},
#     {'name': u'Роман Евстратов', 'email': 'evstratov@yandex-team.ru'},
#     {'name': u'Ольга Замула', 'email': 'ozamula@yandex-team.ru'},
#     {'name': u'Роман Захаров', 'email': 'zakharovr@yandex-team.ru'},
#     {'name': u'Анастасия Калинина', 'email': 'aikalinina@yandex-team.ru'},
#     {'name': u'Татьяна Камышникова', 'email': 'kamyshnikova@yandex-team.ru'},
#     {'name': u'Ирина Князева', 'email': 'irinakniazeva@yandex-team.ru'},
#     {'name': u'Анастасия Копылова', 'email': 'afkop@yandex-team.ru'},
#     {'name': u'Екатерина Королева', 'email': 'koroleva-e@yandex-team.ru'},
#     {'name': u'Наталия Ларионова', 'email': 'natalia-lar@yandex-team.ru'},
#     {'name': u'Карина Липовка', 'email': 'klipovka@yandex-team.ru'},
#     {'name': u'Екатерина Мауль', 'email': 'ekaterinamaul@yandex-team.ru'},
#     {'name': u'Ольга Микутис', 'email': 'mikutis@yandex-team.ru'},
#     {'name': u'Вадим Миличников', 'email': 'v-milichnikov@yandex-team.ru'},
#     {'name': u'Михаил Никоноров', 'email': 'mnikonorov@yandex-team.ru'},
#     {'name': u'Мария Новичкова', 'email': 'mnovichkova@yandex-team.ru'},
#     {'name': u'Марина Парамонова', 'email': 'paramonovama@yandex-team.ru'},
#     {'name': u'Вячеслав Погорелый', 'email': 'pogorelyy@yandex-team.ru'},
#     {'name': u'Татьяна Рыбакова', 'email': 'rybakovatu@yandex-team.ru'},
#     {'name': u'Илья Семенов', 'email': 'ilya-semenov@yandex-team.ru'},
#     {'name': u'Екатерина Сергеева', 'email': 'eksergeeva@yandex-team.ru'},
#     {'name': u'Алёна Серова', 'email': 'alserova@yandex-team.ru'},
#     {'name': u'Владимир Синицын', 'email': 'sinitsynvu@yandex-team.ru'},
#     {'name': u'Виктория Сотник', 'email': 'vvsotnik@yandex-team.ru'},
#     {'name': u'Радион Татиев', 'email': 'tatiev@yandex-team.ru'},
#     {'name': u'Максим Тиканов', 'email': 'mtikanov@yandex-team.ru'},
#     {'name': u'Алена Титова', 'email': 'alena-titova@yandex-team.ru'},
#     {'name': u'Дмитрий Федулов', 'email': 'fedulov@yandex-team.ru'},
#     {'name': u'Руслан Хабибуллин', 'email': 'ruslankhab@yandex-team.ru'},
#     {'name': u'Дмитрий Чусов', 'email': 'dchusov@yandex-team.ru'},
#     {'name': u'Наталья Шелест', 'email': 'shelestnp@yandex-team.ru'},
#     {'name': u'Павел Шишкарев', 'email': 'shishkarev-pv@yandex-team.ru'},
#     {'name': u'Анастасия Щеблякова', 'email': 'anashche@yandex-team.ru'},
#     {'name': u'Мария Щелчкова', 'email': 'mareda@yandex-team.ru'},
#     {'name': u'Marina Cherkasova', 'email': 'cherkas@yandex-team.ru'},
    
    
    
    
    
    {'name': u'Павел Астафьев', 'email': 'astafiev@yandex-team.ru'},
    {'name': u'Эраст Афлятунов', 'email': 'erast@yandex-team.ru'},
    {'name': u'Алена Горбунова', 'email': 'goral@yandex-team.ru'},
    {'name': u'Владимир Зудилин', 'email': 'zudilin@yandex-team.ru'}, 
    
])


# функция для изменения формата названия столбцоы с датой, т.к. при скачивании из файла они меняются
def date_format(x):
    try:
        return x.strftime('%d-%m-%Y')
    except:
        return x
        
        
today = str(datetime.strftime(datetime.now(), '%d-%m-%Y')).replace('-','.')


n = 0
text = ''
for attachment in issue.attachments:
    if attachment.name.find(today + '.xlsm') >= 0:
        n+=1
        new_file = attachment

# Если файла нет или есть несоклько        
if n == 0:
    text = u'Ошибка! Нет файла в нужном формате: ...' + today + '.xlsm'
elif n > 1:
    text = u'Ошибка! Больше чем один файл в нужном формате: ...'+ today + '.xlsm'

# Если есть один файл,

else:
    try:
        # начинаем рассылку
        
        new_file.download_to('')
        text = u'Отчет о рассылке\n'
        
        #читаем файл из приложения
        
        x = pd.read_excel(new_file.name, 
                  sheet_name = u'Исходные', 
                  #sheet_name = 'data', 
                  #skiprows = [0,1]
                 )
        
        # правим форматы колонок с датами
        
        col = pd.DataFrame(x.columns.values)
        x.columns = col[0].apply(date_format)
        
        report = pd.DataFrame([]) # отчет буду отправлять на почту себе

        for i in range(len(deal_owners)): # для каждого менеджера из списка ищу его фамилию во владельцах
            name = deal_owners.loc[i][1] # имя менеджера
            email = deal_owners.loc[i][0] # его почта
            data = x[x[u'Deal - Владелец'] == name].reset_index(drop = True)
            if len(data) > 0:
                #filename = name + '_' + today +'.xlsx'
                filename = 'report_' + today +'.xlsx'
                data.to_excel(filename, encoding = 'CP1251',  header = True, index = False)

                report = report.append([{'name': name, 'rows': len(data)}])

                send_mail(
                'iafilimonov@yandex-team.ru',
                [u'iafilimonov@yandex-team.ru'
#                  ,email
                ],
                subject='daily report TEST for ' + name.encode('utf-8'),
                text='report for ' + email + ' ' + name.encode('utf-8'),
                files=[filename])
                os.remove(filename)
#             print u'Имя агента: ', name, u', Всего строк: ', len(data)
#             text = text + u'Имя агента: ' + name + u', Всего строк: ' + str(len(data)) + '\n'

        os.remove(new_file.name)
    except:
        # если произошла какая-то ошибка, отписываем в тикет
        
        text = u'Ошибка! Произошла ошибка при рассылке файлов'
        

# comment = issue.comments.create(text = text)
