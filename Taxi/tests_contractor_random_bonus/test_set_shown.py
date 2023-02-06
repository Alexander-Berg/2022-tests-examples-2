import hashlib

import pytest

PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'uberdriver',
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
        'RandomBonus.rides_meta_title': {'ru': 'Bonus for %(rides)s rides'},
    },
)
@pytest.mark.parametrize(
    'slug, ttl_str',
    [
        ('tag1', '2020-08-28T15:00:00.000000Z'),
        ('tag2', '2020-08-29T12:00:00.000000Z'),
        ('tag3', '2020-08-29T12:00:00.000000Z'),
    ],
)
@pytest.mark.now(NOW_ISO)
async def test_set_shown(
        taxi_contractor_random_bonus, mockserver, slug, ttl_str, pgsql,
):
    @mockserver.json_handler('/driver-tags/v2/drivers/match/profile')
    def _tags(request):
        return {
            'tags': {slug: {'ttl': ttl_str, 'topics': ['random_bonus_topic']}},
        }

    bonus_id = _hash(slug + ttl_str)
    query = f"""
        SELECT shown_at
        FROM random_bonus.bonuses
        WHERE id = '{bonus_id}'
          AND park_id = '{PARK_ID}'
          AND driver_id = '{DRIVER_ID}'; """

    with pgsql['random-bonus-db'].cursor() as cursor:
        cursor.execute(query)
        assert not cursor.fetchall()

        for _ in range(2):
            response = await taxi_contractor_random_bonus.get(
                '/driver/v1/random-bonus/v1/polling', headers=HEADERS,
            )
            assert response.status_code == 200
            assert response.json()['items'][0]['is_new']

        cursor.execute(query)
        items = cursor.fetchall()
        assert len(items) == 1
        assert not items[0][0]

        response = await taxi_contractor_random_bonus.post(
            '/driver/v1/random-bonus/v1/shown',
            params={'id': bonus_id},
            headers=HEADERS,
        )
        assert response.status_code == 200

        cursor.execute(query)
        items = cursor.fetchall()
        assert len(items) == 1
        assert items[0][0]

        response = await taxi_contractor_random_bonus.get(
            '/driver/v1/random-bonus/v1/polling', headers=HEADERS,
        )
        assert response.status_code == 200
        assert not response.json()['items'][0]['is_new']
