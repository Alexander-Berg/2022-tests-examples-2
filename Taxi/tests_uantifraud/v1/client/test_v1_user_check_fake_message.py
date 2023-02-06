import copy

import pytest


UAFS_SANCTION_REASON_TO_CLIENT_MESSAGE_MAPPING = (
    'UAFS_SANCTION_REASON_TO_CLIENT_MESSAGE_MAPPING'
)


async def test_user_without_known_reason(taxi_uantifraud, testpoint):
    @testpoint('default_message_call')
    def default_message_call(_):
        pass

    order_id = 'unknown_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert default_message_call.times_called == 1


def _frauder_response_base_check(response):
    assert response.status_code == 200
    resp = response.json()
    assert 'order_status_alert' in resp
    for field in ['title', 'text', 'change_params_button_text']:
        assert field in resp['order_status_alert']


@pytest.mark.redis_store(file='redis')
async def test_frauder(taxi_uantifraud, testpoint):
    @testpoint('default_message_call')
    def default_message_call(_):
        pass

    order_id = 'frauder_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert default_message_call.times_called == 0


@pytest.mark.redis_store(file='redis')
async def test_without_corrupt(taxi_uantifraud, testpoint):
    @testpoint('default_message_call')
    def default_message_call(_):
        pass

    order_id = 'frauder_for_corrupt_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert default_message_call.times_called == 0


@pytest.mark.redis_store(file='redis')
@pytest.mark.parametrize(
    'field_for_corrupt',
    ['title', 'text', 'change_params_button_text', 'retry_button_text'],
)
@pytest.mark.parametrize('subfield_for_corrupt', ['keyset', 'key'])
async def test_pass_to_default_message(
        taxi_uantifraud,
        testpoint,
        taxi_config,
        field_for_corrupt,
        subfield_for_corrupt,
):
    @testpoint('default_message_call')
    def default_message_call(_):
        pass

    @testpoint('fallback_message_call')
    def fallback_message_call(_):
        pass

    def corrupt_message_in_config(taxi_config, reason, field, subfield):
        mapping_config = copy.deepcopy(
            taxi_config.get(UAFS_SANCTION_REASON_TO_CLIENT_MESSAGE_MAPPING),
        )
        mapping_config['mappings'][reason]['window_fields'][field][
            subfield
        ] = 'bad_tanker_value'
        taxi_config.set_values(
            {UAFS_SANCTION_REASON_TO_CLIENT_MESSAGE_MAPPING: mapping_config},
        )

    corrupt_message_in_config(
        taxi_config,
        'ban_template_for_corrut_some_field',
        field_for_corrupt,
        subfield_for_corrupt,
    )
    order_id = 'frauder_for_corrupt_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert default_message_call.times_called == 1
    assert fallback_message_call.times_called == 0


@pytest.mark.redis_store(file='redis')
async def test_without_mapped_reason(taxi_uantifraud, testpoint):
    @testpoint('default_message_call')
    def default_message_call(_):
        pass

    @testpoint('fallback_message_call')
    def fallback_message_call(_):
        pass

    order_id = 'frauder_without_mapped_reason_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert default_message_call.times_called == 1
    assert fallback_message_call.times_called == 0


@pytest.mark.redis_store(file='redis')
async def test_pass_to_fallback_message(
        taxi_uantifraud, testpoint, taxi_config,
):
    @testpoint('default_message_call')
    def default_message_call(_):
        pass

    @testpoint('fallback_message_call')
    def fallback_message_call(_):
        pass

    mapping_config = copy.deepcopy(
        taxi_config.get(UAFS_SANCTION_REASON_TO_CLIENT_MESSAGE_MAPPING),
    )
    mapping_config['__default_window__']['title']['key'] = 'bad_tanker_value'
    taxi_config.set_values(
        {UAFS_SANCTION_REASON_TO_CLIENT_MESSAGE_MAPPING: mapping_config},
    )

    order_id = 'frauder_without_mapped_reason_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert default_message_call.times_called == 1
    assert fallback_message_call.times_called == 1


@pytest.mark.redis_store(file='redis')
async def test_duplication_priority_detection(taxi_uantifraud, testpoint):
    @testpoint('duplication_priority_detected')
    def duplication_priority_detected(_):
        pass

    order_id = 'frauder_with_duplication_priority_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/check_fake/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    _frauder_response_base_check(response)
    assert duplication_priority_detected.times_called == 1
