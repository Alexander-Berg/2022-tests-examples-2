import hashlib

import pytest

PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.50',
    'X-Request-Version-Type': 'uber',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
}
NOW_ISO = '2020-08-28T17:00:00+03:00'


def _hash(sss: str):
    return hashlib.md5(sss.encode('utf-8')).hexdigest()


@pytest.mark.config(
    RANDOM_BONUS_TAGS_INFO={
        'tags_info': [
            {
                'tag': 'tag1',
                'type': 'timer',
                'title_key': 'tag1_title',
                'subtitle_key': 'tag1_subtitle',
                'description_key': 'tag1_description',
                'duration': 180,
            },
            {
                'tag': 'tag2',
                'type': 'order_count',
                'title_key': 'tag2_title',
                'subtitle_key': 'tag2_subtitle',
                'description_key': 'tag2_description',
                'duration': 24 * 60,
                'rides': 5,
            },
            {
                'tag': 'tag3',
                'type': 'simple',
                'title_key': 'tag3_title',
                'subtitle_key': 'tag3_subtitle',
                'description_key': 'tag3_description',
                'meta_title_key': 'tag3_metatitle',
                'duration': 60,
            },
        ],
    },
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'tag1_title': {'ru': 'title_1'},
        'tag2_title': {'ru': 'title_2'},
        'tag3_title': {'ru': 'title_3'},
        'tag1_subtitle': {'ru': 'subtitle_1'},
        'tag2_subtitle': {'ru': 'subtitle_2'},
        'tag3_subtitle': {'ru': 'subtitle_3'},
        'tag1_description': {'ru': 'description_1'},
        'tag2_description': {'ru': 'description_2'},
        'tag3_description': {'ru': 'description_3'},
        'tag3_metatitle': {'ru': 'metatitle_3'},
        'RandomBonus.rides_meta_title': {'ru': 'Bonus for %(rides)s rides'},
        'RandomBonus.progress_task_title': {'ru': 'task_title'},
        'RandomBonus.progress_task_subtitle': {'ru': 'task_subtitle'},
        'RandomBonus.progress_task_description': {'ru': 'task_description'},
    },
)
@pytest.mark.parametrize('is_uberdriver', [True, False])
@pytest.mark.parametrize('has_progress', [True, False])
async def test_random_bonus_polling(
        taxi_contractor_random_bonus,
        mockserver,
        is_uberdriver,
        has_progress,
        pgsql,
):
    @mockserver.json_handler('/driver-tags/v2/drivers/match/profile')
    def _tags(request):
        return {
            'tags': {
                'tag1': {
                    'ttl': '2020-08-28T15:00:00.000000Z',
                    'topics': ['random_bonus_topic'],
                },
                'tag2': {
                    'ttl': '2020-08-29T12:00:00.000000Z',
                    'topics': ['random_bonus_topic'],
                },
                'tag3': {
                    'ttl': '2020-08-29T12:00:00.000000Z',
                    'topics': ['random_bonus_topic'],
                },
            },
        }

    if has_progress:
        with pgsql['random-bonus-db'].cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO random_bonus.progress
                  (park_id, driver_id, progress, is_first,
                   last_status,
                   status_updated_at, last_online_at,
                   last_bonus_at)
                VALUES
                  ('{PARK_ID}', '{DRIVER_ID}', 35.478, FALSE,
                   'online'::random_bonus.STATUS,
                   '{NOW_ISO}'::TIMESTAMPTZ, '{NOW_ISO}'::TIMESTAMPTZ,
                   '{NOW_ISO}'::TIMESTAMPTZ);
                """,
            )

    headers = dict(HEADERS)
    headers['X-Request-Version-Type'] = 'uber' if is_uberdriver else ''

    response = await taxi_contractor_random_bonus.get(
        '/driver/v1/random-bonus/v1/polling', headers=headers,
    )

    if not is_uberdriver:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == '300'

    response_json = response.json()
    assert response_json['items'] == [
        {
            'id': _hash('tag1' + '2020-08-28T15:00:00.000000Z'),
            'title': 'title_1',
            'subtitle': 'subtitle_1',
            'description': 'description_1',
            'begin_time': '2020-08-28T12:00:00.000000Z',
            'end_time': '2020-08-28T15:00:00.000000Z',
            'type': {'type_id': 'timer'},
            'is_new': True,
        },
        {
            'id': _hash('tag2' + '2020-08-29T12:00:00.000000Z'),
            'title': 'title_2',
            'subtitle': 'subtitle_2',
            'description': 'description_2',
            'begin_time': '2020-08-28T12:00:00.000000Z',
            'end_time': '2020-08-29T12:00:00.000000Z',
            'type': {
                'type_id': 'order_count',
                'meta_title': 'Bonus for 5 rides',
            },
            'is_new': True,
        },
        {
            'id': _hash('tag3' + '2020-08-29T12:00:00.000000Z'),
            'title': 'title_3',
            'subtitle': 'subtitle_3',
            'description': 'description_3',
            'begin_time': '2020-08-29T11:00:00.000000Z',
            'end_time': '2020-08-29T12:00:00.000000Z',
            'type': {'type_id': 'simple', 'meta_title': 'metatitle_3'},
            'is_new': True,
        },
    ]

    if has_progress:
        assert response_json['task'] == {
            'title': 'task_title',
            'subtitle': 'task_subtitle',
            'description': 'task_description',
            'progress': 35,
        }
    else:
        assert 'task' not in response_json
