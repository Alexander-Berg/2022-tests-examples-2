import datetime

import pytest


# Driver info test data
expected_driver_info_pictures = {
    'avatar_image': {
        'url': (
            'https://tc.mobile.yandex.net/static/images/1234/'
            '233855d702ce1c31f844544e7d979939776942849b941abc'
            '9d433a210b575ce9_cropped'
        ),
        'url_parts': {'key': '', 'path': ''},
    },
    'profile_photo': {
        'url': (
            'https://tc.mobile.yandex.net/static/images/1234/'
            '233855d702ce1c31f844544e7d979939776942849b941abc'
            '9d433a210b575ce9'
        ),
        'url_parts': {'key': '', 'path': ''},
    },
}

driver_info_test_translations = {
    'taxiontheway.driverinfo.rating': {'en': 'rating'},
    'taxiontheway.driverinfo.experience': {'en': 'years driving'},
    'taxiontheway.driverinfo.status_title_rating': {'en': '%(rating)s ☆'},
    'taxiontheway.driverinfo.distance': {'en': 'km'},
    'taxiontheway.driverinfo.rides_count': {'en': 'rides'},
    'taxiontheway.driverinfo.digits_separator': {'en': '~'},
    'feedback_choice.badge_label.pleasant_music': {'en': 'Приятная музыка'},
    'feedback_choice.badge_label.polite_driver': {'en': 'Вежливость'},
    'feedback_choice.badge_label.comfort_ride': {'en': 'Комфортное вождение'},
}
driver_info_test_settings = {
    'rating': {'min_value': 4.2, 'top_value_above': 5.0},
    'experience': {'min_value': 2, 'top_value_above': 10},
    'achievements': {'min_count': 2},
}
driver_info_test_settings_badges = {
    'rating': {'min_value': 4.2, 'top_value_above': 5.0},
    'experience': {'min_value': 2, 'top_value_above': 10},
    'distance': {'min_value': 1000.0, 'top_value_above': 5000.0},
    'rides_count': {'min_value': 200, 'top_value_above': 5000},
    'achievements': {
        'min_count': 2,
        'badges_to_show_to_user': ['music', 'polite', 'comfort_ride'],
    },
}
test_client_id = 'b300bda7d41b4bae8d58dfa93221ef16'
test_order_id = '8c83b49edb274ce0992f337061047375'
test_driver_id = '999012_a5709ce56c2740d9a536650f5390de0b'
test_driver_id_dbdrivers = 'a5709ce56c2740d9a536650f5390de0b'
test_driver_license = 'AB0254'


def _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
):
    """Internal function which actually does all the driver info's testing
    """
    # mock the tracker so it doesn't throw an error at the end of a test
    @mockserver.json_handler('/tracker/position')
    def get_position(_request):
        return {}

    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _get_rating_v2(_request):
        assert _request.headers.get('X-Ya-Service-Name') == 'protocol'
        return {'unique_driver_id': 'id', 'rating': str(expected_rating)}

    # change parameters in the DB
    db.orders.update(
        {'_id': test_order_id},
        {'$set': {'status': order_status, 'taxi_status': taxi_status}},
    )
    db.order_proc.update(
        {'_id': test_order_id},
        {
            '$set': {
                'order.status': order_status,
                'order.taxi_status': taxi_status,
            },
        },
    )
    if driver_score:
        db.unique_drivers.update(
            {'licenses.0': {'$eq': {'license': test_driver_license}}},
            {
                '$set': {
                    'new_score.unified': {
                        'total': driver_score,
                        'rating_count': driver_rating_count,
                    },
                },
            },
        )
    else:
        db.unique_drivers.update(
            {'licenses.0': {'$eq': {'license': test_driver_license}}},
            {
                '$unset': {
                    'new_score.unified.total': 1,
                    'new_score.unified.rating_count': 1,
                },
            },
        )
    if driver_stats:
        db.unique_drivers.update(
            {'licenses.0': {'$eq': {'license': test_driver_license}}},
            {'$set': {'driver_info_stats': driver_stats}},
        )
    else:
        db.unique_drivers.update(
            {'licenses.0': {'$eq': {'license': test_driver_license}}},
            {'$unset': {'driver_info_stats': 1}},
        )

    db.dbdrivers.update(
        {'driver_id': test_driver_id_dbdrivers},
        {
            '$set': {
                'license_issue_date': datetime.datetime.strptime(
                    driver_start_date, '%Y-%m-%dT%H:%M:%S%z',
                ),
            },
        },
    )

    if drivers_first_name:
        db.dbdrivers.update(
            {'driver_id': test_driver_id.split('_')[1]},
            {'$set': {'first_name': drivers_first_name}},
        )
    else:
        db.dbdrivers.update(
            {'driver_id': test_driver_id.split('_')[1]},
            {'$unset': {'first_name': 1}},
        )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': test_client_id,
            'orderid': test_order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()

    if should_return_driver_info:
        assert content['driver']['rating'] == expected_rating
        assert content['driver']['short_name'] == expected_name
        assert content['driver']['status_title'] == expected_status_title
        assert content['driver']['pictures'] == expected_pictures
        assert content['driver']['profile_facts'] == expected_profile_facts
        if expected_feedback_badges:
            assert (
                content['driver']['feedback_badges']
                == expected_feedback_badges
            )
        else:
            assert 'feedback_badges' not in content['driver']
    else:
        assert 'rating' not in content['driver']
        assert 'short_name' not in content['driver']
        assert 'status_title' not in content['driver']
        assert 'pictures' not in content['driver']
        assert 'profile_facts' not in content['driver']


driver_stats_normal = {
    'total_travel_distance': 123.25,
    'total_orders_count': 256,
    'rating_reasons': {
        'music': 100,
        'polite': 200,
        'bad_driving': 500,
        'bad_driving_1': 1000,
    },
}


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': True,
        },
        'comfort': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': False,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(unique_drivers='drivers_photos')
@pytest.mark.parametrize(
    'taxi_status,drivers_first_name,driver_score,'
    'driver_rating_count,driver_start_date,'
    'should_return_driver_info,expected_rating,expected_name,'
    'expected_status_title,'
    'expected_profile_facts,expected_pictures',
    [
        # normal execution
        (
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
        ),
        # this driver has no first_name in `drivers` collection,
        # so nothing should be returned
        (
            'waiting',
            None,
            0.95,
            1,
            '2017-12-01T00:00:00+0300',
            False,
            None,
            None,
            None,
            None,
            None,
        ),
        # this driver has 'invalid' first_name in `drivers` collection,
        # so nothing should be returned
        (
            'waiting',
            'Исак!',
            0.95,
            1,
            '2017-12-01T00:00:00+0300',
            False,
            None,
            None,
            None,
            None,
            None,
        ),
        # this driver has '' first_name in `drivers` collection,
        # so nothing should be returned
        (
            'waiting',
            '',
            0.95,
            1,
            '2017-12-01T00:00:00+0300',
            False,
            None,
            None,
            None,
            None,
            None,
        ),
        # this order has 'driving' status, which is not in the config,
        # so no driver info should be displayed
        (
            'driving',
            'Исак',
            0.95,
            1,
            '2017-12-01T00:00:00+0300',
            False,
            None,
            None,
            None,
            None,
            None,
        ),
        # this order has 'transporting' status, so rating should be returned
        # in status_title
        (
            'transporting',
            'АЛЕКСАНДР',
            0.95,
            1,
            '2017-12-01T00:00:00+0300',
            True,
            '4.8',
            'Александр',
            '4.8 ☆',
            [{'title': '4.8', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
        ),
        # this driver has low rating,
        # so we shouldn't show it in the profile_facts
        (
            'waiting',
            'Исак',
            0.75,
            1,
            '2017-12-01T00:00:00+0300',
            False,
            None,
            None,
            None,
            None,
            None,
        ),
        # this driver has absent rating,
        # so we should return additional driver info
        (
            'waiting',
            'Исак',
            None,
            1,
            '2017-12-01T00:00:00+0300',
            True,
            '4.2',
            'Исак',
            'Исак',
            [{'title': '4.2', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
        ),
        # this driver has the default rating (0 reviews),
        # so we should return additional driver info
        (
            'waiting',
            'Исак',
            0.8,
            0,
            '2017-12-01T00:00:00+0300',
            True,
            '4.2',
            'Исак',
            'Исак',
            [{'title': '4.2', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
        ),
        # 5.0 rating so is_top_value should be set
        (
            'waiting',
            'Исак',
            1.00,
            1,
            '2017-12-01T00:00:00+0300',
            True,
            '5.0',
            'Исак',
            'Исак',
            [{'title': '5.0', 'subtitle': 'rating', 'is_top_value': True}],
            expected_driver_info_pictures,
        ),
        # this driver should have just under 2 years of experience,
        # so no experience fact is returned
        (
            'waiting',
            'Исак',
            0.95,
            1,
            '2016-06-15T00:00:00+0300',
            True,
            '4.8',
            'Исак',
            'Исак',
            [{'title': '4.8', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
        ),
        # this driver should have 2 years of experience
        (
            'waiting',
            'Исак',
            0.94,
            1,
            '2016-06-14T23:59:59+0300',
            True,
            '4.76',
            'Исак',
            'Исак',
            [
                {'title': '4.76', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '2',
                    'subtitle': 'years driving',
                    'is_top_value': False,
                },
            ],
            expected_driver_info_pictures,
        ),
        # this driver should have 42 years of experience
        # because TAXIONTHEWAY_ENABLE_LICENSE_EXPERIENCE_TOTAL=True
        pytest.param(
            'waiting',
            'Исак',
            0.94,
            1,
            '2016-06-14T23:59:59+0300',
            True,
            '4.76',
            'Исак',
            'Исак',
            [
                {'title': '4.76', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '42',
                    'subtitle': 'years driving',
                    'is_top_value': True,
                },
            ],
            expected_driver_info_pictures,
            marks=pytest.mark.config(
                TAXIONTHEWAY_ENABLE_LICENSE_EXPERIENCE_TOTAL=True,
            ),
        ),
        # timezone test (license issue date is stored in UTC):
        # this driver should have just under 2 years of experience,
        # so no experience fact is returned
        (
            'waiting',
            'Исак',
            0.99,
            1,
            '2016-06-14T21:00:01+0000',
            True,
            '4.96',
            'Исак',
            'Исак',
            [{'title': '4.96', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
        ),
        # timezone test (license issue date is stored in UTC):
        # this driver should have 2 years of experience
        (
            'waiting',
            'Исак',
            0.9444,
            1,
            '2016-06-14T20:59:59+0000',
            True,
            '4.78',
            'Исак',
            'Исак',
            [
                {'title': '4.78', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '2',
                    'subtitle': 'years driving',
                    'is_top_value': False,
                },
            ],
            expected_driver_info_pictures,
        ),
        # this driver should have still 2 years of experience (just short of 3)
        (
            'waiting',
            'Исак',
            0.95,
            1,
            '2015-06-15T00:00:00+0300',
            True,
            '4.8',
            'Исак',
            'Исак',
            [
                {'title': '4.8', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '2',
                    'subtitle': 'years driving',
                    'is_top_value': False,
                },
            ],
            expected_driver_info_pictures,
        ),
        # 10 years of experience so is_top_value should be set
        (
            'waiting',
            'Исак',
            0.95,
            1,
            '2008-06-14T00:00:00+0300',
            True,
            '4.8',
            'Исак',
            'Исак',
            [
                {'title': '4.8', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '10',
                    'subtitle': 'years driving',
                    'is_top_value': True,
                },
            ],
            expected_driver_info_pictures,
        ),
        # Should return experience if hide_driver_personal_data is disabled
        pytest.param(
            'waiting',
            'Исак',
            0.95,
            1,
            '2008-06-14T00:00:00+0300',
            True,
            '4.8',
            'Исак',
            'Исак',
            [
                {'title': '4.8', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '10',
                    'subtitle': 'years driving',
                    'is_top_value': True,
                },
            ],
            expected_driver_info_pictures,
            marks=(
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='hide_driver_personal_data',
                    consumers=['protocol/taxiontheway'],
                    clauses=[
                        {
                            'title': '',
                            'value': {'enabled': False},
                            'predicate': {'type': 'true'},
                        },
                    ],
                )
            ),
        ),
        # Should hide experience if hide_driver_personal_data is enabled
        pytest.param(
            'waiting',
            'Исак',
            0.95,
            1,
            '2008-06-14T00:00:00+0300',
            True,
            '4.8',
            'Исак',
            'Исак',
            [{'title': '4.8', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
            marks=(
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='hide_driver_personal_data',
                    consumers=['protocol/taxiontheway'],
                    clauses=[
                        {
                            'title': '',
                            'value': {'enabled': True},
                            'predicate': {'type': 'true'},
                        },
                    ],
                )
            ),
        ),
    ],
)
def test_totw_drivers_photos_are_returned(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
):
    order_status = 'assigned'
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        None,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges=None,
    )


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': False,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(unique_drivers='drivers_photos')
@pytest.mark.parametrize(
    'order_status,taxi_status,drivers_first_name,driver_score,'
    'driver_rating_count,driver_start_date,'
    'should_return_driver_info,expected_rating,expected_status_title,'
    'expected_profile_facts,expected_pictures',
    [
        # return_profile_photo is False so no profile_photo should be set
        (
            'assigned',
            'waiting',
            'Исак',
            0.90,
            1,
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            {
                'avatar_image': {
                    'url': (
                        'https://tc.mobile.yandex.net/static/images/1234/'
                        '233855d702ce1c31f844544e7d979939776942849b941abc'
                        '9d433a210b575ce9_cropped'
                    ),
                    'url_parts': {'key': '', 'path': ''},
                },
            },
        ),
    ],
)
def test_totw_driver_info_profile_photo_is_not_returned_on_flag(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
):
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        None,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        'Исак',
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges=None,
    )


@pytest.mark.filldb(unique_drivers='drivers_photos')
def test_totw_drivers_info_is_not_returned_when_experiment_is_off(
        taxi_protocol, mockserver, tracker, now, db,
):
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status='assigned',
        taxi_status='waiting',
        drivers_first_name='Исак',
        driver_score=0.90,
        driver_rating_count=1,
        driver_stats=None,
        driver_start_date='2017-12-01T00:00:00+0300',
        should_return_driver_info=False,
        expected_rating=None,
        expected_name='Исак',
        expected_status_title=None,
        expected_profile_facts=None,
        expected_pictures=None,
        expected_feedback_badges=None,
    )


@pytest.mark.filldb(unique_drivers='drivers_photos')
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT='',
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED='',
    DRIVER_INFO_DISPLAY_SETTINGS={},
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings,
)
def test_totw_drivers_info_does_not_crash_on_empty_tariff_config(
        taxi_protocol, mockserver, tracker, now, db,
):
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status='assigned',
        taxi_status='waiting',
        drivers_first_name='Исак',
        driver_score=0.90,
        driver_rating_count=1,
        driver_stats=None,
        driver_start_date='2017-12-01T00:00:00+0300',
        should_return_driver_info=False,
        expected_rating=None,
        expected_name=None,
        expected_status_title=None,
        expected_profile_facts=None,
        expected_pictures=None,
        expected_feedback_badges=None,
    )


driver_stats_normal = {
    'total_travel_distance': 123.25,
    'total_orders_count': 256,
    'rating_reasons': {
        'music': 100,
        'polite': 200,
        'bad_driving': 500,
        'bad_driving_1': 1000,
    },
}


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(unique_drivers='drivers_photos')
@pytest.mark.parametrize(
    'order_status,taxi_status,drivers_first_name,driver_score,'
    'driver_rating_count,driver_stats,'
    'driver_start_date,'
    'should_return_driver_info,expected_rating,expected_name,'
    'expected_status_title,'
    'expected_profile_facts,expected_pictures, expected_feedback_badges',
    [
        # milage and rides count are both below min value so should be hidden
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 123250,
                'total_orders_count': 100,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
            None,
        ),
        # milage should be set
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 1001000.0,
                'total_orders_count': 100,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [
                {'title': '4.6', 'subtitle': 'rating', 'is_top_value': False},
                {'title': '1~001', 'subtitle': 'km', 'is_top_value': False},
            ],
            expected_driver_info_pictures,
            None,
        ),
        # milage is top value
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 5000001000.0,
                'total_orders_count': 100,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [
                {'title': '4.6', 'subtitle': 'rating', 'is_top_value': False},
                {'title': '5~000~001', 'subtitle': 'km', 'is_top_value': True},
            ],
            expected_driver_info_pictures,
            None,
        ),
        # rides count is above minimum
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 0.0,
                'total_orders_count': 3000,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [
                {'title': '4.6', 'subtitle': 'rating', 'is_top_value': False},
                {'title': '3~000', 'subtitle': 'rides', 'is_top_value': False},
            ],
            expected_driver_info_pictures,
            None,
        ),
        # rides count is top value
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 0.0,
                'total_orders_count': 5000000,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [
                {'title': '4.6', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '5~000~000',
                    'subtitle': 'rides',
                    'is_top_value': True,
                },
            ],
            expected_driver_info_pictures,
            None,
        ),
        pytest.param(
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 0.0,
                'total_orders_count': 5000000,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [
                {'title': '4.6', 'subtitle': 'rating', 'is_top_value': False},
                {
                    'title': '5~000~000',
                    'subtitle': 'rides',
                    'is_top_value': True,
                },
            ],
            expected_driver_info_pictures,
            None,
            marks=(
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='hide_driver_personal_data',
                    consumers=['protocol/taxiontheway'],
                    clauses=[
                        {
                            'title': '',
                            'value': {'enabled': False},
                            'predicate': {'type': 'true'},
                        },
                    ],
                )
            ),
        ),
        pytest.param(
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 0.0,
                'total_orders_count': 5000000,
                'rating_reasons': {},
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
            None,
            marks=(
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='hide_driver_personal_data',
                    consumers=['protocol/taxiontheway'],
                    clauses=[
                        {
                            'title': '',
                            'value': {'enabled': True},
                            'predicate': {'type': 'true'},
                        },
                    ],
                )
            ),
        ),
    ],
)
def test_totw_driver_info_distance_and_milage(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
):
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
    )


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(unique_drivers='drivers_photos')
@pytest.mark.parametrize(
    'order_status,taxi_status,drivers_first_name,driver_score,'
    'driver_rating_count,driver_stats,'
    'driver_start_date,'
    'should_return_driver_info,expected_rating,expected_name,'
    'expected_status_title,'
    'expected_profile_facts,expected_pictures, expected_feedback_badges',
    [
        # driver stat are empty, should not crash
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {},
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
            None,
        ),
    ],
)
def test_totw_driver_info_empty_drivers_stat_do_not_crash(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
):
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
    )


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'filters': {'tariffs': ['default']},
                'images': {
                    'active_image_tag': 'achievements_polite',
                    'inactive_image_tag': 'achievements_inactive_polite',
                },
                'label': 'feedback_choice.badge_label.polite_driver',
                'name': 'polite',
            },
            {
                'filters': {'tariffs': ['default']},
                'images': {
                    'active_image_tag': 'achievements_music',
                    'inactive_image_tag': 'achievements_inactive_music',
                },
                'label': 'feedback_choice.badge_label.pleasant_music',
                'name': 'music',
            },
            {
                'filters': {'tariffs': ['default']},
                'images': {
                    'active_image_tag': 'achievements_car',
                    'inactive_image_tag': 'achievements_inactive_car',
                },
                'label': 'feedback_choice.badge_label.comfort_ride',
                'name': 'comfort_ride',
            },
            {
                'filters': {'tariffs': ['default']},
                'label': 'feedback_choice.badge_label.bad_driving',
                'name': 'bad_driving_1',
            },
        ],
    },
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(unique_drivers='drivers_photos')
@pytest.mark.parametrize(
    'order_status,taxi_status,drivers_first_name,driver_score,'
    'driver_rating_count,driver_stats,'
    'driver_start_date,'
    'should_return_driver_info,expected_rating,expected_name,'
    'expected_status_title,'
    'expected_profile_facts,expected_pictures, expected_feedback_badges',
    [
        # normal execution, all in one
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 123.25,
                'total_orders_count': 99,
                'rating_reasons': {
                    'music': 1000,
                    'polite': 234567890,
                    'comfort_ride': 1,  # too low value, not showing
                    'bad_driving_1': 500,  # not allowed to show
                },
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
            [
                {
                    'label': 'Вежливость',
                    'count': '234~567~890',
                    'image_tag': 'achievements_polite',
                },
                {
                    'label': 'Приятная музыка',
                    'count': '1~000',
                    'image_tag': 'achievements_music',
                },
            ],
        ),
        # comfort_ride should be shown
        (
            'assigned',
            'waiting',
            'ИСАК оГЛЫ ВасилиЙ пЕтРович',
            0.90,
            1,
            {
                'total_travel_distance': 123.25,
                'total_orders_count': 99,
                'rating_reasons': {
                    'music': 5,
                    'polite': 100,
                    'comfort_ride': 2,
                    'bad_driving_1': 500,  # not allowed to show
                },
            },
            '2017-12-01T00:00:00+0300',
            True,
            '4.6',
            'Исак Оглы Василий Петрович',
            'Исак Оглы Василий Петрович',
            [{'title': '4.6', 'subtitle': 'rating', 'is_top_value': False}],
            expected_driver_info_pictures,
            [
                {
                    'label': 'Вежливость',
                    'count': '100',
                    'image_tag': 'achievements_polite',
                },
                {
                    'label': 'Приятная музыка',
                    'count': '5',
                    'image_tag': 'achievements_music',
                },
                {
                    'label': 'Комфортное вождение',
                    'count': '2',
                    'image_tag': 'achievements_car',
                },
            ],
        ),
    ],
)
def test_totw_drivers_badges_are_returned(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
):
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status,
        taxi_status,
        drivers_first_name,
        driver_score,
        driver_rating_count,
        driver_stats,
        driver_start_date,
        should_return_driver_info,
        expected_rating,
        expected_name,
        expected_status_title,
        expected_profile_facts,
        expected_pictures,
        expected_feedback_badges,
    )


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'enabled_only_in_zones': ['moscow', 'newyork'],
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(
    unique_drivers='drivers_photos', tariff_settings='drivers_info',
)
@pytest.mark.parametrize(
    'order_zone, should_return_driver_info',
    [
        # City is in an allowed zone - should return driver info
        ('moscow', True),
        # City is NOT in an allowed zone - no driver info should be returned
        ('abakan', False),
    ],
)
def test_totw_drivers_info_zones_restrictions(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_zone,
        should_return_driver_info,
):
    _test_totw_driver_info_zone_restrictions(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_zone,
        should_return_driver_info,
    )


@pytest.mark.translations(
    client_messages=driver_info_test_translations,
    tariff={'old_category_name.vip': {'ru': 'Бизнес', 'en': 'Business'}},
)
@pytest.mark.config(
    DRIVER_INFO_PREMIUM_TARIFFS=['vip'],
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {'waiting': 'name'},
            'return_profile_photo': True,
        },
        'vip': {
            'status_title_source': {'waiting': 'name'},
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
)
@pytest.mark.user_experiments('show_driver_info')
@pytest.mark.filldb(
    unique_drivers='drivers_photos', tariff_settings='drivers_info',
)
@pytest.mark.parametrize(
    ['tariff', 'should_return_driver_info'],
    [('econom', False), ('vip', True)],
)
@pytest.mark.now('2019-11-25T00:00:00+0300')
def test_totw_drivers_info_add_experiment_for_econom_1(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        tariff,
        should_return_driver_info,
):

    _test_totw_driver_info_check_tariff_response(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        tariff,
        should_return_driver_info,
    )


@pytest.mark.translations(
    client_messages=driver_info_test_translations,
    tariff={'old_category_name.vip': {'ru': 'Бизнес', 'en': 'Business'}},
)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {'waiting': 'name'},
            'return_profile_photo': True,
        },
        'vip': {
            'status_title_source': {'waiting': 'name'},
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(
    unique_drivers='drivers_photos', tariff_settings='drivers_info',
)
@pytest.mark.parametrize(
    ['tariff', 'should_return_driver_info'],
    [('econom', True), ('vip', False)],
)
@pytest.mark.now('2019-11-25T00:00:00+0300')
def test_totw_drivers_info_add_experiment_for_econom_2(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        tariff,
        should_return_driver_info,
):

    _test_totw_driver_info_check_tariff_response(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        tariff,
        should_return_driver_info,
    )


def _test_totw_driver_info_check_tariff_response(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        tariff,
        should_return_driver_info,
):
    # Helper test to test responses for different tariffs
    db.order_proc.update(
        {'_id': test_order_id},
        {'$set': {'order.performer.tariff.class': tariff}},
    )
    _test_totw_driver_info_zone_restrictions(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        'moscow',
        should_return_driver_info,
    )


@pytest.mark.now('2018-06-14T00:00:00+0300')
@pytest.mark.translations(client_messages=driver_info_test_translations)
@pytest.mark.config(
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT=(
        'https://tc.mobile.yandex.net/static/images/1234/{}'
    ),
    IMAGES_URL_TEMPLATE_DRIVER_INFO_EXPERIMENT_CROPPED=(
        'https://tc.mobile.yandex.net/static/images/1234/{}_cropped'
    ),
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {
            'status_title_source': {
                'waiting': 'name',
                'transporting': 'rating',
            },
            'return_profile_photo': True,
        },
    },
    DRIVER_INFO_VALUES_SETTINGS=driver_info_test_settings_badges,
)
@pytest.mark.user_experiments('show_driver_info_non_higher_class')
@pytest.mark.filldb(
    unique_drivers='drivers_photos', tariff_settings='drivers_info',
)
@pytest.mark.parametrize(
    'order_zone, should_return_driver_info',
    [
        # No zone parameters are set - return the info by default
        ('moscow', True),
        ('abakan', True),
    ],
)
def test_totw_drivers_info_zones_restrictions_no_config(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_zone,
        should_return_driver_info,
):
    _test_totw_driver_info_zone_restrictions(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_zone,
        should_return_driver_info,
    )


def _test_totw_driver_info_zone_restrictions(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_zone,
        should_return_driver_info,
):
    """Test driver info returning based on order's zone and config"""
    # Update the order's zone
    db.orders.update({'_id': test_order_id}, {'$set': {'nz': order_zone}})

    db.order_proc.update(
        {'_id': test_order_id}, {'$set': {'order.nz': order_zone}},
    )

    # Do the actual test
    _test_totw_driver_info(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        order_status='assigned',
        taxi_status='waiting',
        drivers_first_name='Исак',
        driver_score=0.90,
        driver_rating_count=1,
        driver_stats=None,
        driver_start_date='2017-12-01T00:00:00+0300',
        should_return_driver_info=should_return_driver_info,
        expected_rating='4.6',
        expected_name='Исак',
        expected_status_title='Исак',
        expected_profile_facts=[
            {'title': '4.6', 'subtitle': 'rating', 'is_top_value': False},
        ],
        expected_pictures=expected_driver_info_pictures,
        expected_feedback_badges=None,
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    TAXIONTHEWAY_DRIVER_FIELDS_BY_TARIFF={
        'econom': {
            'model_template_key': 'taxiontheway.driver.model',
            'color_code': 'D4D0CE',
            'plates_required': False,
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.driver.model': {'en': 'driver %(short_name)s'},
    },
)
def test_driver_name_instead_plates(taxi_protocol, tracker, now, mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _get_rating_v2(_request):
        assert _request.headers.get('X-Ya-Service-Name') == 'protocol'
        return {'unique_driver_id': 'id', 'rating': '4.666'}

    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    driver = response.json()['driver']

    assert driver['model'] == 'driver Исак'
    assert driver['color_code'] == 'D4D0CE'
    assert 'plates' not in driver
    assert 'color' not in driver


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    TAXIONTHEWAY_DRIVER_FIELDS_BY_TARIFF={
        'econom': {
            'model_template_key': 'taxiontheway.driver.model',
            'color_code': 'D4D0CE',
            'plates_required': False,
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.driver.model': {'en': 'driver %(short_name)s'},
    },
)
def test_tow_regular_show_photo2(taxi_protocol, tracker, now, mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _get_rating_v2(_request):
        assert _request.headers.get('X-Ya-Service-Name') == 'protocol'
        return {'unique_driver_id': 'id', 'rating': '4.666'}

    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    driver = response.json()['driver']

    assert driver['model'] == 'driver Исак'
    assert driver['color_code'] == 'D4D0CE'
    assert 'plates' not in driver
    assert 'color' not in driver
