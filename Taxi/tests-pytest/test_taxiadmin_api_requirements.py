# -*- encoding: utf-8 -*-
import json

import pytest
from django import test as django_test

TRANSLATIONS = [
    ('client_messages', 'requirement.bicycle', 'ru',
     'Перевозка велосипеда, лыж'),
    ('client_messages', 'requirement.bicycle', 'ka',
     'ველოსიპედის, თხილამურების გადატანა'),
    ('client_messages', 'requirement.bicycle', 'hy',
     'Հեծանիվի, դահուկների տեղափոխում'),
    ('client_messages', 'requirement.bicycle', 'kk',
     'Велосипедті тасымалдау'),
    ('client_messages', 'requirement.bicycle', 'en', 'Bicycle rack'),
    ('client_messages', 'requirement.bicycle', 'uk',
     'Перевезення велосипеда, лиж'),
    ('client_messages', 'requirement.bicycle', 'az',
     'Velosipedin daşınması'),
    ('client_messages', 'requirement.ski', 'ru',
     'Перевозка лыж или сноуборда'),
    ('client_messages', 'requirement.ski', 'ka',
     'თხილამურის ან სნოუბორდის ტრანსპორტირება'),
    ('client_messages', 'requirement.ski', 'hy',
     'Դահուկների կամ սնոուբորդի տեղափոխում'),
    ('client_messages', 'requirement.ski', 'kk',
     'Шаңғыларды немесе сноубордты тасымалдау'),
    ('client_messages', 'requirement.ski', 'en', 'Ski carrier'),
    ('client_messages', 'requirement.ski', 'uk', 'Перевезення лиж або сноуборду'),
    ('client_messages', 'requirement.ski', 'az',
     'Xizəklərin və ya snoubordun daşınması '),
    ('client_messages', 'requirement.childchair', 'ru', 'Детское кресло'),
    ('client_messages', 'requirement.childchair', 'ka', 'საბავშვო სავარძელი'),
    ('client_messages', 'requirement.childchair', 'hy', 'Մանկական բազկաթոռ'),
    ('client_messages', 'requirement.childchair', 'kk', 'Балалар креслосы'),
    ('client_messages', 'requirement.childchair', 'en', 'Child safety seat'),
    ('client_messages', 'requirement.childchair', 'uk', 'Дитяче крісло'),
    ('client_messages', 'requirement.childchair', 'az', 'Uşaq oturacağı'),
    ('client_messages', 'requirement.childchair_moscow', 'ru',
     'Детское кресло'),
    ('client_messages', 'requirement.childchair_moscow', 'ka',
     'საბავშვო სავარძელი'),
    ('client_messages', 'requirement.childchair_moscow', 'hy',
     'Մանկական բազկաթոռ'),
    ('client_messages', 'requirement.childchair_moscow', 'kk',
     'Балалар креслосы'),
    ('client_messages', 'requirement.childchair_moscow', 'en',
     'Child safety seat'),
    ('client_messages', 'requirement.childchair_moscow', 'uk', 'Дитяче крісло'),
    ('client_messages', 'requirement.childchair_moscow', 'az',
     'Uşaq oturacağı'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'ru',
     '9-18 кг, от 9 месяцев до 4 лет'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'ka',
     '9-18 კგ, 9 თვიდან 4 წლამდე'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'hy',
     '9-18 կգ, 9 ամսեկանից մինչև 4 տարեկան'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'kk',
     '9-18 кг, 9 айдан бастап 4 жасқа дейін'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'en',
     '9-18 kg, 9 months to 4 years'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'uk',
     '9–18 кг, від 9 місяців до 4 років'),
    ('client_messages', 'requirement.childchair_moscow.infant', 'az',
     '9-18 kq,  9 aydan 4 yaşadək'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'ru',
     '15-25 кг, от 3 до 7 лет'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'ka',
     '15-25 კგ, 3-დან 7 წლამდე'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'hy',
     '15-25 կգ, 3-ից մինչև 7 տարեկան'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'kk',
     '15-25 кг, 3 бастап 7 жасқа дейін'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'en',
     '15-25 kg, 3-7 years'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'uk',
     '15–25 кг, від 3 до 7 років'),
    ('client_messages', 'requirement.childchair_moscow.chair', 'az',
     '15-25 kq, 3 yaşdan 7-yədək'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'ru',
     '22-36 кг, от 7 до 12 лет'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'ka',
     '22-36 კგ, 7-დან 12 წლამდე'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'hy',
     '22-36 կգ, 7-ից մինչև 12 տարեկան'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'kk',
     '22-36 кг, 7 бастап 12 жасқа дейін'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'en',
     '22-36 kg, 7-12 years'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'uk',
     '22–36 кг, від 7 до 12 років'),
    ('client_messages', 'requirement.childchair_moscow.booster', 'az',
     '22-36 kq, 7 yaşdan 12-yədək'),
    ('color', '0A7679', 'ru', 'серебристый сине-зелёный'),
    ('color', '0A7679', 'ka', 'მოვერცხლისფრო ლურჯ-მწვანე'),
    ('color', '0A7679', 'hy', 'արծաթափայլ կապտականաչ'),
    ('color', '0A7679', 'kk', 'күміс түсті көк-жасыл'),
    ('color', '0A7679', 'az', 'gümüşü göyümtül yaşıl'),
    ('color', '0A7679', 'en', 'silver teal'),
    ('color', '0A7679', 'uk', 'сріблястий синьо-зелений'),
    ('color', '0A7679', 'ro', 'verde-argintiu'),
    ('geoareas', 'cherepovets', 'ru', 'Череповец'),
    ('geoareas', 'cherepovets', 'ka', 'ჩერეპოვეცი'),
    ('geoareas', 'cherepovets', 'hy', 'Չերեպովեց'),
    ('geoareas', 'cherepovets', 'kk', 'Череповец'),
    ('geoareas', 'cherepovets', 'az', 'Çerepovets'),
    ('geoareas', 'cherepovets', 'en', 'Cherepovets'),
    ('geoareas', 'cherepovets', 'uk', 'Череповець'),
    ('geoareas', 'cherepovets', 'ro', 'Cerepoveț'),
    ('notify', 'apns.on_autoreorder_timeout', 'ru',
     'К сожалению, водитель не смог выполнить заказ. '
     'Мы продолжаем поиск и сообщим, как только найдём замену'),
    ('notify', 'apns.on_autoreorder_timeout', 'ka',
     'სამწუხაროდ, მძღოლმა ვერ შეძლო შეკვეთის შესრულება. '
     'ჩვენ ვაგრძელებთ ძიებას და შეგატყობინებთ, როგორც კი შემცვლელს ვიპოვით'),
    ('notify', 'apns.on_autoreorder_timeout', 'hy',
     'Ցավոք, վարորդը չկարողացավ կատարել պատվերը: '
     'Մենք շարունակում ենք փնտրել և փոխարինող գտնելուն պես՝ կտեղեկացնենք'),
    ('notify', 'apns.on_autoreorder_timeout', 'kk',
     'Өкінішке орай, жүргізуші тапсырысты орындай алмады. '
     'Біз іздеуді жалғастырудамыз және'
     ' алмастырылатын жүргізушіні тапқан бойда хабарлаймыз'),
    ('notify', 'apns.on_autoreorder_timeout', 'en',
     'Unfortunately, your driver was unable to make the pickup. '
     'We are continuing to search, and will let you know when we '
     'find another one'),
    ('notify', 'apns.on_autoreorder_timeout', 'uk',
     'На жаль, водій не зміг виконати замовлення. '
     'Ми продовжуємо пошук і повідомимо, щойно знайдемо заміну.'),
    ('notify', 'apns.on_autoreorder_timeout', 'az',
     'Təəssüf ki, sürücü sifarişi yerinə yetirə bilmədi. '
     'Biz axtarışı davam edirik, əvəzini tapsaq sizə xəbər edəcəyik.'),
    ('tariff', 'service_name.bicycle', 'ru', 'Перевозка велосипеда, лыж'),
    ('tariff', 'service_name.bicycle', 'ka',
     'ველოსიპედის, თხილამურების გადატანა'),
    ('tariff', 'service_name.bicycle', 'hy', 'Հեծանիվի, դահուկների տեղափոխում'),
    ('tariff', 'service_name.bicycle', 'kk', 'Велосипедті тасымалдау'),
    ('tariff', 'service_name.bicycle', 'en', 'Bicycle/ski transport'),
    ('tariff', 'service_name.bicycle', 'uk', 'Перевезення велосипеда, лиж'),
    ('tariff', 'service_name.bicycle', 'az', 'Velosipedin daşınması'),
    ('tariff', 'service_name.no_smoking', 'ru', 'Некурящий водитель'),
    ('tariff', 'service_name.no_smoking', 'ka', 'არამწეველი მძღოლი'),
    ('tariff', 'service_name.no_smoking', 'hy', 'Չծխող վարորդ'),
    ('tariff', 'service_name.no_smoking', 'kk', 'Темекі шектейтін жүргізуші'),
    ('tariff', 'service_name.no_smoking', 'en', 'Non-smoking driver'),
    ('tariff', 'service_name.no_smoking', 'uk', 'Водій-некурець'),
    ('tariff', 'service_name.no_smoking', 'az', 'Siqaret çəkməyən sürücü'),
    ('tariff', 'service_name.childchair', 'ru', 'Детское кресло'),
    ('tariff', 'service_name.childchair', 'ka', 'საბავშვო სავარძელი'),
    ('tariff', 'service_name.childchair', 'hy', 'Մանկական բազկաթոռ'),
    ('tariff', 'service_name.childchair', 'kk', 'Балалар креслосы'),
    ('tariff', 'service_name.childchair', 'en', 'Child safety seat'),
    ('tariff', 'service_name.childchair', 'uk', 'Дитяче крісло'),
    ('tariff', 'service_name.childchair', 'az', 'Uşaq oturacağı'),
    ('tariff', 'service_name.childchair_moscow', 'ru', 'Детское кресло'),
    ('tariff', 'service_name.childchair_moscow', 'ka', 'საბავშვო სავარძელი'),
    ('tariff', 'service_name.childchair_moscow', 'hy', 'Մանկական բազկաթոռ'),
    ('tariff', 'service_name.childchair_moscow', 'kk', 'Балалар креслосы'),
    ('tariff', 'service_name.childchair_moscow', 'en', 'Child safety seat'),
    ('tariff', 'service_name.childchair_moscow', 'uk', 'Дитяче крісло'),
    ('tariff', 'service_name.childchair_moscow', 'az', 'Uşaq oturacağı'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'ru', 'Чтобы продолжить работать, обновите Таксометр.'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'ka', 'მუშაობის გასაგრძელებლად განაახლეთ ტაქსომეტრი უახლეს ვერსიამდე.'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'hy',
     'Աշխատանքը շարունակելու համար թարմացրեք Տաքսոմետրը վերջին տարբերակով:'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'kk',
     'Жұмысты жалғастыру үшін Таксометрді соңғы нұсқаға дейін жаңартыңыз.'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'en',
     'To continue working, please update Taximeter to the newest version.'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'uk', 'Щоб продовжити роботу, оновіть Таксометр до останньої версії.'),
    ('taximeter_messages', 'drivercheck.DriverTaximeterVersionDisabledMessage',
     'az', 'İşə davam etmək üçün Taksi sayğacını son versiyayadək yeniləyin.'),
]


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=[
        'ru', 'en', 'hy', 'ka', 'kk', 'uk', 'az'
    ],
    FORBID_STRING_REQUIREMENTS=True,
)
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.parametrize('parameters, name, expected_code', [
    ({
        'default': False,
        'position': 4,
        'type': 'boolean',
     }, 'bicycle', 200),
    ({
         'default': None,
         'position': 1,
         'type': 'select',
         'select': {
             'type': 'number',
             'options': [
                 {
                     'name': 'infant',
                     'value': 1,
                     'independent_tariffication': False
                 },
                 {
                     'name': 'chair',
                     'value': 3,
                     'independent_tariffication': False
                 },
                 {
                     'name': 'booster',
                     'value': 7,
                     'independent_tariffication': False
                 }
             ]
         },
         'driver_name': 'childchair',
         'multiselect': False
     }, 'childchair_moscow', 200),
    ({
         'default': None,
         'position': 1,
         'type': 'select',
         'select': {
             'type': 'string',
             'options': [
                 {
                     'name': 'infant',
                     'value': '1',
                     'independent_tariffication': False
                 },
                 {
                     'name': 'chair',
                     'value': '3',
                     'independent_tariffication': False
                 },
                 {
                     'name': 'booster',
                     'value': '7',
                     'independent_tariffication': False
                 }
             ]
         },
         'driver_name': 'childchair',
         'multiselect': False
     }, 'childchair_moscow', 406),
    # no translations in client_messages
    ({
         'default': 0,
         'position': 10,
         'type': 'number',
     }, 'no_smoking', 406),
    # no translations in tariff
    ({
        'default': False,
        'position': 4,
        'type': 'boolean',
     }, 'ski', 406),
    # no translations for subcategories
    ({
         'default': None,
         'position': 1,
         'type': 'select',
         'select': {
             'type': 'number',
             'options': [
                 {
                     'name': 'infant',
                     'value': 1,
                     'independent_tariffication': False
                 },
                 {
                     'name': 'chair',
                     'value': 3,
                     'independent_tariffication': False
                 },
                 {
                     'name': 'booster',
                     'value': 7,
                     'independent_tariffication': False
                 }
             ]},
         'driver_name': 'childchair',
         'multiselect': False
     }, 'childchair', 406)
])
@pytest.mark.filldb()
def test_set_requirement(parameters, name, expected_code):
    client = django_test.Client()
    url = '/api/requirements/{}/set/'.format(name)
    response = client.post(
        url, json.dumps(parameters), content_type='application/json'
    )
    assert response.status_code == expected_code
