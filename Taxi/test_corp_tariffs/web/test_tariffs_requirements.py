import pytest


@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'business': 'name.business'},
    },
)
@pytest.mark.parametrize(
    [
        'taxi_categories',
        'corp_classes',
        'filter_categories',
        'expected_requirements',
    ],
    [
        pytest.param(
            [
                {
                    'id': '111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 50, 'type': 'yellowcarnumber'},
                    ],
                },
                {
                    'id': '111',
                    'category_name': 'business',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                },
            ],
            [
                {
                    'name': 'econom',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
                {
                    'name': 'business',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
            ],
            None,
            {
                'econom': [{'max_price': 50, 'type': 'yellowcarnumber'}],
                'business': [],
            },
            id='single',
        ),
        pytest.param(
            [
                {
                    'id': '111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 50, 'type': 'yellowcarnumber'},
                    ],
                },
                {
                    'id': '1111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 100, 'type': 'yellowcarnumber'},
                    ],
                },
            ],
            [
                {
                    'name': 'econom',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
            ],
            None,
            {'econom': [{'max_price': 50, 'type': 'yellowcarnumber'}]},
            id='warning',
        ),
        pytest.param(
            [
                {
                    'id': '111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 50, 'type': 'yellowcarnumber'},
                    ],
                },
                {
                    'id': '1111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 50, 'type': 'yellowcarnumber'},
                    ],
                },
            ],
            [
                {
                    'name': 'econom',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
            ],
            None,
            {'econom': [{'max_price': 50, 'type': 'yellowcarnumber'}]},
            id='equal',
        ),
        pytest.param(
            [
                {
                    'id': '111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                },
            ],
            [
                {
                    'name': 'econom',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
            ],
            None,
            {'econom': []},
            id='without',
        ),
        pytest.param(
            [
                {
                    'id': '111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 50, 'type': 'yellowcarnumber'},
                        {'max_price': 50, 'type': 'waiting_in_transit'},
                    ],
                },
            ],
            [
                {
                    'name': 'econom',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                            'summable_requirements': [
                                {
                                    'max_price': 100,
                                    'type': 'waiting_in_transit',
                                },
                            ],
                        },
                    ],
                },
            ],
            None,
            {
                'econom': [
                    {'max_price': 100, 'type': 'waiting_in_transit'},
                    {'max_price': 50, 'type': 'yellowcarnumber'},
                ],
            },
            id='merge',
        ),
        pytest.param(
            [
                {
                    'id': '111',
                    'category_name': 'econom',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                    'summable_requirements': [
                        {'max_price': 50, 'type': 'yellowcarnumber'},
                    ],
                },
                {
                    'id': '1111',
                    'category_name': 'business',
                    'category_type': 'application',
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'name_key': 'name_key',
                    'day_type': 2,
                    'currency': '$',
                    'minimal': 1,
                },
            ],
            [
                {
                    'name': 'econom',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
                {
                    'name': 'business',
                    'inherited': False,
                    'intervals': [
                        {
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'id': '05156a5d865a429a960ddb4dde20e735',
                            'minimal': 129,
                            'name_key': 'interval.always',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                },
            ],
            ['business'],
            {'business': []},
            id='filter categories',
        ),
    ],
)
async def test_requirements(
        web_app,
        taxi_categories,
        corp_classes,
        filter_categories,
        expected_requirements,
):
    from corp_tariffs.api.common import corp_tariffs_manager

    response = corp_tariffs_manager.make_tariff_corp(
        web_app['context'],
        driver_tariff={
            '_id': 'driver_tariff_id',
            'home_zone': 'test',
            'categories': taxi_categories,
        },
        corp_tariff={
            '_id': 'corp_tariff_id',
            'home_zone': 'test',
            'name': 'test_name',
            'country': 'rus',
            'inherited': False,
            'classes': corp_classes,
            'disable_paid_supply_price': False,
        },
        tariff_plan={'_id': 'corp_tariff_plan', 'disable_fixed_price': False},
        country='rus',
        filter_categories=filter_categories,
    )
    categories = response['tariff']['categories']
    requirements = {
        category['category_name']: category.get('summable_requirements')
        for category in categories
    }
    assert requirements == expected_requirements
