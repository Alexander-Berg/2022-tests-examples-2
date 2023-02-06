import datetime

from sber_int_api.email_api import types
from sber_int_api.email_api import xml


def test_get_requests(load_binary):
    xml_file = load_binary('request.xml')
    assert xml.parse_requests(xml_file) == (
        [
            types.NewRequest(
                external_id='SD100039314',
                start_date=datetime.datetime(2017, 11, 30, 9, 30),
                phone='+71111111111',
                route_point_names=[
                    'Москва, улица Вавилова, 19',
                    'Москва, Кутузовский проспект, 32',
                    'Москва, 2-й Южнопортовый проезд',
                    'Москва, улица Вавилова, 19',
                ],
                initiator='Сергей Николаевич',
                comment='Москва, улица Вавилова, 19 - Посадка '
                'Сергей Николаевич, тел. 7 111 111 11 11, '
                'Комментарий: Тест нового шаблона; Москва, '
                'Кутузовский проспект, 32 - Посадка Семен '
                'Семенович, тел. 7 111 222 33 44, '
                'Комментарий: Тест тест',
                working_group='ввб нгосб/транспорт',
            ),
        ],
        [
            types.InProgressRequest(
                external_id='SD100057746', internal_id='perev61366',
            ),
        ],
        [
            types.RejectRequest(
                external_id='SD100057746', internal_id='perev61366',
            ),
        ],
    )


def test_create_xml_file(load_binary):
    expected_xml_file = load_binary('response.xml').decode('utf-8')
    response_xml_file = xml.create_xml_file(
        [
            types.InProgressResponse(
                external_id='external_id_1',
                internal_id='internal_id_1',
                status=types.Status.accept,
            ),
            types.InProgressResponse(
                external_id='external_id_2',
                internal_id='internal_id_2',
                status=types.Status.accept,
            ),
            types.DoneResponse(
                external_id='external_id_3',
                internal_id='internal_id_3',
                status=types.Status.accept,
                created_at=datetime.datetime(2020, 7, 21, 21, 58, 17),
                due=datetime.datetime(2020, 7, 21, 21, 58, 18),
                done=datetime.datetime(2020, 7, 21, 21, 58, 19),
                close_status=types.CloseStatus.complete,
                details='',
                price=33.3,
                distance=5.5,
                waiting_time=datetime.timedelta(minutes=1),
                travel_time=datetime.timedelta(minutes=33),
                start_transporting_time=datetime.datetime(
                    2020, 7, 21, 21, 58, 20,
                ),
                complete_time=datetime.datetime(2020, 7, 21, 21, 59, 19),
                timestamps=[
                    datetime.datetime(2020, 7, 21, 21, 58, 21),
                    datetime.datetime(2020, 7, 21, 21, 58, 22),
                ],
                route=[
                    types.Location(lat=33.3, lon=55.5),
                    types.Location(lat=33.3, lon=55.6),
                ],
            ),
        ],
        pretty_print=True,
    ).decode('utf-8')
    assert response_xml_file == expected_xml_file
