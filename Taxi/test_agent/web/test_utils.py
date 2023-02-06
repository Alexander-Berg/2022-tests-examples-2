import datetime

import pytest

from agent import utils
from agent.internal import shop

GOOD_HEADERS: dict = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'}
GOOD_EN_HEADERS: dict = {
    'X-Yandex-Login': 'webalex',
    'Accept-Language': 'en-en',
}

EMPTY_HEADERS: dict = {}


@pytest.mark.parametrize(
    'input_region,normilized_region,timezone',
    [
        ('Владимир', 'Владимирская область', 'Europe/Moscow'),
        ('Томская', 'Томская область', 'Asia/Tomsk'),
        ('Омская', 'Омская область', 'Asia/Omsk'),
    ],
)
async def test_find_region_and_timezone(
        input_region, normilized_region, timezone,
):
    assert utils.find_timezone(input_region) == (normilized_region, timezone)


@pytest.mark.parametrize(
    'now_date,piece,start,end',
    [
        (
            datetime.datetime(2021, 1, 1),
            True,
            datetime.date(2021, 1, 1),
            datetime.date(2021, 1, 16),
        ),
        (
            datetime.datetime(2021, 1, 15),
            True,
            datetime.date(2021, 1, 1),
            datetime.date(2021, 1, 16),
        ),
        (
            datetime.datetime(2021, 1, 16),
            True,
            datetime.date(2021, 1, 16),
            datetime.date(2021, 2, 1),
        ),
        (
            datetime.datetime(2021, 1, 10),
            False,
            datetime.date(2021, 1, 1),
            datetime.date(2021, 2, 1),
        ),
        (
            datetime.datetime(2021, 1, 20),
            False,
            datetime.date(2021, 1, 1),
            datetime.date(2021, 2, 1),
        ),
    ],
)
async def test_check_date_period(now_date, piece, start, end):
    assert utils.get_range_period(piece=piece, date=now_date) == (start, end)


@pytest.mark.parametrize(
    'headers,body,expected_data,status',
    [
        (EMPTY_HEADERS, {}, {}, 400),
        (GOOD_HEADERS, {}, {}, 400),
        (
            GOOD_HEADERS,
            {'login': 'webalex'},
            [{'key': 'test1', 'name': 'Тестовая команда 1'}],
            200,
        ),
        (
            GOOD_EN_HEADERS,
            {'login': 'webalex'},
            [{'key': 'test1', 'name': 'Test team 1'}],
            200,
        ),
    ],
)
async def test_get_teams(web_app_client, headers, body, expected_data, status):
    res = await web_app_client.post(
        '/utils/teams_list', headers=headers, json=body,
    )
    assert res.status == status
    content = await res.json()
    if status == 200:
        assert content == expected_data


async def test_upload_promocode(web_context):

    expected_data = [
        {
            'expired_date': datetime.date(2020, 1, 1),
            'id': 1,
            'promocode': 'test_1',
        },
        {
            'expired_date': datetime.date(2020, 1, 1),
            'id': 2,
            'promocode': 'test_2',
        },
        {
            'expired_date': datetime.date(2020, 1, 1),
            'id': 3,
            'promocode': 'test_3',
        },
        {
            'expired_date': datetime.date(2020, 1, 1),
            'id': 4,
            'promocode': 'test_4',
        },
        {
            'expired_date': datetime.date(2020, 1, 1),
            'id': 5,
            'promocode': 'test_5',
        },
    ]

    data = [
        {
            'promocode': 'test_1',
            'goods_detail_id': 1,
            'expired_date': datetime.date(2020, 1, 1),
        },
        {
            'promocode': 'test_2',
            'goods_detail_id': 1,
            'expired_date': datetime.date(2020, 1, 1),
        },
        {
            'promocode': 'test_3',
            'goods_detail_id': 1,
            'expired_date': datetime.date(2020, 1, 1),
        },
        {
            'promocode': 'test_4',
            'goods_detail_id': 1,
            'expired_date': datetime.date(2020, 1, 1),
        },
        {
            'promocode': 'test_5',
            'goods_detail_id': 1,
            'expired_date': datetime.date(2020, 1, 1),
        },
    ]

    result = await shop.upload_promocode(context=web_context, data=data)
    res = []
    for row in result:
        res.append(
            {
                'expired_date': row['expired_date'],
                'id': row['id'],
                'promocode': row['hash'],
            },
        )

    assert expected_data == res
