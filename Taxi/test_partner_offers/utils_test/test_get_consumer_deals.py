import datetime

import pytest

from taxi.util import performance

from partner_offers import data_for_consumer
from partner_offers import models
from partner_offers.generated.service.swagger.models import api


@pytest.mark.now('2019-11-29T15:00+00:00')
def test_work_time_filter():
    tz_offsets = [3600 * x for x in (3, 4, 5, 2, 5)]
    work_times = [
        [
            ('2019-11-29T12:00+00:00', '2019-11-29T13:00+00:00'),
            ('2019-11-29T14:00+00:00', '2019-11-29T19:00+00:00'),
        ],
        [
            ('2019-11-29T15:20+00:00', '2019-11-30T00:00+00:00'),
            ('2019-11-30T14:00+00:00', '2019-11-30T19:00+00:00'),
        ],
        [('2019-11-29T15:20+00:00', '2019-12-30T00:00+00:00')],
        [('2019-11-29T17:20+00:00', '2019-12-30T00:00+00:00')],
        [('2019-11-29T12:00+00:00', '2019-12-01T13:00+00:00')],
    ]
    timestamps = [
        [
            tuple(datetime.datetime.fromisoformat(x).timestamp() for x in y)
            for y in wt
        ]
        for wt in work_times
    ]

    locations = {
        i: models.Location(
            business_oid=i,
            partner_id=5,
            longitude=7,
            latitude=8,
            name='test',
            country='test',
            city='test',
            address='test',
            work_time_intervals=wt,
            timezone_offset=tz_offsets[i],
        )
        for i, wt in enumerate(timestamps)
    }

    # pylint: disable=protected-access
    current, filtered = data_for_consumer._process_work_times(
        locations, 30, 24 * 60,
    )
    # pylint: enable=protected-access
    assert current == datetime.datetime.fromisoformat(
        '2019-11-29T15:00+00:00',
    ), current.toisoformat()
    keys = sorted(filtered)
    assert keys == [0, 1, 2, 4], sorted(filtered)
    assert [filtered[x][0] for x in keys] == [True, False, False, True]
    dt_ = datetime
    tz_ = dt_.timezone(dt_.timedelta(seconds=10800))
    assert filtered[0][1] == [dt_.datetime(2019, 11, 29, 22, 0, tzinfo=tz_)]
    tz_ = dt_.timezone(dt_.timedelta(seconds=14400))
    assert filtered[1][1] == [
        dt_.datetime(2019, 11, 29, 19, 20, tzinfo=tz_),
        dt_.datetime(2019, 11, 30, 4, 0, tzinfo=tz_),
        dt_.datetime(2019, 11, 30, 18, 0, tzinfo=tz_),
    ]
    tz_ = dt_.timezone(dt_.timedelta(seconds=18000))
    assert filtered[2][1] == [dt_.datetime(2019, 11, 29, 20, 20, tzinfo=tz_)]
    assert filtered[4][1] == []


TRANSLATIONS = {
    'Food': {'ru': 'Еда'},
    'Service': {'ru': 'Сервис'},
    'Help': {'ru': 'Помощь'},
    'VAT': {'ru': 'Ват'},
}

CATEGORIES_DATA = [
    {
        'category': 'food',
        'name': 'Food',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 15,
    },
    {
        'category': 'service',
        'name': 'Service',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 5,
    },
    {
        'category': 'help',
        'name': 'Help',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 15,
    },
    {
        'category': 'vat',
        'name': 'VAT',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 15,
        'priority': 1,
    },
]

WORK_TIME_CONF = {
    'must_open_in_near_minutes': 30,
    'how_long_schedule_to_send_minutes': 24 * 60,
}


@pytest.mark.pgsql('partner_offers', files=['simple_case.sql'])
@pytest.mark.now('2019-11-29T15:00+00:00')
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_build_full_response(web_context):
    result = await data_for_consumer.get_deals_and_locations(
        models.Consumer.DRIVER,
        ['bronze'],
        frozenset(),
        37.49,
        55.05,
        'ru',
        performance.TimeStorage(''),
        web_context,
    )

    assert result.calculated_at == datetime.datetime.fromisoformat(
        '2019-11-29T15:00+00:00',
    )
    expected: list = [
        api.CategoryForConsumer(
            id='vat',
            name='Ват',
            icon_url='https://example.com/im.png',
            icon_url_night='https://example.com/im.png',
            pins_limit=15,
            rebate='20%',
        ),
        api.CategoryForConsumer(
            icon_url='https://example.com/im.png',
            icon_url_night='https://example.com/im.png',
            id='food',
            name='Еда',
            pins_limit=15,
            rebate='15%',
        ),
        api.CategoryForConsumer(
            icon_url='https://example.com/im.png',
            icon_url_night='https://example.com/im.png',
            id='service',
            name='Сервис',
            pins_limit=5,
            rebate=None,
        ),
    ]
    assert repr(result.categories) == repr(expected), result.categories

    expected = [
        api.DealForConsumer(
            id='11',
            category_id='food',
            locations=['11'],
            title='Some title',
            subtitle=None,
            description=api.DealForConsumer.Description(
                title='Some desc title', text=None, icon_url=None,
            ),
            type='discount',
            terms=api.ConsumerTermsDiscount(text=None, percent='15%'),
        ),
        api.DealForConsumer(
            id='22',
            category_id='service',
            locations=['21', '22'],
            title='Some title',
            subtitle=None,
            description=api.DealForConsumer.Description(
                title='Some desc title', text=None, icon_url=None,
            ),
            type='coupon',
            terms=api.ConsumerTermsCoupon(text=None, price='700₽'),
        ),
        api.DealForConsumer(
            id='41',
            category_id='vat',
            locations=['41', '43'],
            title='Some title',
            subtitle=None,
            description=api.DealForConsumer.Description(
                title='Some desc title', text=None, icon_url=None,
            ),
            type='discount',
            terms=api.ConsumerTermsDiscount(text=None, percent='20%'),
        ),
        api.DealForConsumer(
            id='42',
            category_id='vat',
            locations=['41', '42', '43'],
            title='Some title',
            subtitle=None,
            description=api.DealForConsumer.Description(
                title='Some desc title', text=None, icon_url=None,
            ),
            type='coupon',
            terms=api.ConsumerTermsCoupon(text=None, price='700₽'),
        ),
        api.DealForConsumer(
            id='43',
            category_id='vat',
            locations=['43'],
            title='Some title',
            subtitle=None,
            description=api.DealForConsumer.Description(
                title='Some desc title', text=None, icon_url=None,
            ),
            type='coupon',
            terms=api.ConsumerTermsCoupon(text=None, price='700₽'),
        ),
    ]
    assert repr(result.deals) == repr(expected), result.deals

    expected = [
        api.LocationForConsumer(
            id='11',
            name='Грибница1',
            icon_url='https://example.com/image.jpg',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Simple test address',
            is_open=True,
            is_open_changes_at=['2019-11-30T02:10:00+03:00'],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='food', rebate='15%',
                ),
            ],
        ),
        api.LocationForConsumer(
            id='21',
            name='Радиоволна1',
            icon_url='http://bronevik.com/im.png',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Simple test address',
            is_open=True,
            is_open_changes_at=['2019-11-30T05:10:00+06:00'],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='service', rebate=None,
                ),
            ],
        ),
        api.LocationForConsumer(
            id='22',
            name='Радиоволна2',
            icon_url='http://bronevik.com/im.png',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Simple test address',
            is_open=True,
            is_open_changes_at=['2019-11-30T05:10:00+06:00'],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='service', rebate=None,
                ),
            ],
        ),
        # Pins tests
        api.LocationForConsumer(
            id='41',
            name='Мак1',
            icon_url='http://mac.more.ru/im.png',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Simple test address',
            is_open=True,
            is_open_changes_at=['2019-11-30T05:10:00+06:00'],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='vat',
                    rebate='20%',  # Have discount but not override
                ),
            ],
        ),
        api.LocationForConsumer(
            id='42',
            name='Мак2',
            icon_url='http://mac.more.ru/im.png',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Simple test address',
            is_open=True,
            is_open_changes_at=['2019-11-30T05:10:00+06:00'],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='vat',
                    rebate=None,  # Haven't discount and override
                ),
            ],
        ),
        api.LocationForConsumer(
            id='43',
            name='Мак3',
            icon_url='http://mac.more.ru/im.png',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Simple test address',
            is_open=True,
            is_open_changes_at=['2019-11-30T05:10:00+06:00'],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='vat',
                    rebate='Other map text',  # Have override
                ),
            ],
        ),
    ]
    assert repr(result.locations) == repr(expected), result.locations
