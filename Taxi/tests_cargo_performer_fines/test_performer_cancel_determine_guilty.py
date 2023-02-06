import pytest

from tests_cargo_performer_fines.plugins import performer as perf
from tests_cargo_performer_fines.plugins import pg_fetch


@pytest.fixture(name='validate_cancellation_db_entity')
def _validate_cancellation_db_entity(
        fetch_cancellation, default_cargo_order_id, default_dbid_uuid,
):
    def handler(entity_id=1):
        cancellation = fetch_cancellation(f'id={entity_id}')
        assert cancellation == pg_fetch.Cancellation(
            id_=entity_id,
            cancel_id=1,
            cargo_order_id=default_cargo_order_id,
            taxi_order_id='taxi',
            park_id=default_dbid_uuid['dbid'],
            driver_id=default_dbid_uuid['uuid'],
            cargo_cancel_reason='reason',
            completed=False,
            guilty=True,
            free_cancellations_limit_exceeded=False,
            payload={
                'claim_status': 'pickuped',
                'items_weight': 15.0,
                'special_requirements': ['cargo_eds'],
                'tags': ['test_tag_1'],
                'time_in_status_sec': 56329990,
                'waybill_ref': 'waybill-ref',
                'zone_id': 'moscow',
                'tariff_class': 'cargo',
            },
        )

    return handler


@pytest.mark.now('2022-06-01T13:10:00.786Z')
async def test_performer_cancel_determine_guilty_happy_path(
        taxi_cargo_performer_fines,
        default_headers,
        mock_driver_tags,
        validate_cancellation_db_entity,
        performer_request_property,
        waybill_info_request_property,
        exp3_performer_cancel_determine_guilty,
        exp3_performer_cancel_limits,
):
    await exp3_performer_cancel_determine_guilty()
    await exp3_performer_cancel_limits()
    mock_driver_tags()

    response = await taxi_cargo_performer_fines.post(
        '/performer/cancel/determine-guilty',
        headers=default_headers,
        json={
            'cancel_reason_id': 'reason',
            'cancel_request_id': 1,
            'taxi_order_id': 'taxi',
            'performer': performer_request_property(),
            'waybill_info': waybill_info_request_property(),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'alert_for_performer': {
            'alert_message': 'текст отмены value1, value2',
            'alert_title': 'Заголовок',
        },
    }

    validate_cancellation_db_entity()


@pytest.mark.parametrize('taxi_order_id', ['taxi', ''])
@pytest.mark.parametrize('cancel_reason', ['reason', ''])
@pytest.mark.parametrize('park_id', [perf.default_dbid_uuid()['dbid'], ''])
@pytest.mark.parametrize('driver_id', [perf.default_dbid_uuid()['uuid'], ''])
@pytest.mark.parametrize('tariff_class', ['cargo', None])
async def test_performer_cancel_determine_guilty_400(
        taxi_cargo_performer_fines,
        default_headers,
        mock_driver_tags,
        performer_request_property,
        waybill_info_request_property,
        exp3_performer_cancel_determine_guilty,
        exp3_performer_cancel_limits,
        taxi_order_id,
        cancel_reason,
        park_id,
        driver_id,
        tariff_class,
):
    await exp3_performer_cancel_determine_guilty()
    await exp3_performer_cancel_limits()
    mock_driver_tags()

    performer = performer_request_property()
    performer['park_id'] = park_id
    performer['driver_id'] = driver_id
    performer['tariff_class'] = tariff_class
    response = await taxi_cargo_performer_fines.post(
        '/performer/cancel/determine-guilty',
        headers=default_headers,
        json={
            'cancel_reason_id': cancel_reason,
            'cancel_request_id': 1,
            'taxi_order_id': taxi_order_id,
            'performer': performer,
            'waybill_info': waybill_info_request_property(),
        },
    )

    is_good_request = (
        taxi_order_id
        and cancel_reason
        and park_id
        and driver_id
        and tariff_class
    )
    if is_good_request:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json()['code'] == 'bad_request'


@pytest.mark.parametrize(
    'exp_determine_guilty_exists, exp_limits_exists',
    [(False, True), (True, False)],
)
async def test_performer_cancel_determine_guilty_404(
        taxi_cargo_performer_fines,
        default_headers,
        mock_driver_tags,
        performer_request_property,
        waybill_info_request_property,
        exp3_performer_cancel_determine_guilty,
        exp3_performer_cancel_limits,
        exp_determine_guilty_exists,
        exp_limits_exists,
):
    if exp_determine_guilty_exists:
        await exp3_performer_cancel_determine_guilty()
    if exp_limits_exists:
        await exp3_performer_cancel_limits()
    mock_driver_tags()

    response = await taxi_cargo_performer_fines.post(
        '/performer/cancel/determine-guilty',
        headers=default_headers,
        json={
            'cancel_reason_id': 'reason',
            'cancel_request_id': 1,
            'taxi_order_id': 'taxi',
            'performer': performer_request_property(),
            'waybill_info': waybill_info_request_property(),
        },
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'not_found'


@pytest.mark.now('2022-06-01T13:10:00.786Z')
async def test_performer_cancel_determine_guilty_broken_waybill(
        taxi_cargo_performer_fines,
        default_headers,
        mock_driver_tags,
        mock_waybill_info,
        performer_request_property,
        validate_cancellation_db_entity,
        waybill_info_request_property,
        exp3_performer_cancel_determine_guilty,
        exp3_performer_cancel_limits,
):
    await exp3_performer_cancel_determine_guilty()
    await exp3_performer_cancel_limits()
    mock_waybill_info()
    mock_driver_tags()

    waybill_info = waybill_info_request_property()
    waybill_info.pop('waybill')
    response = await taxi_cargo_performer_fines.post(
        '/performer/cancel/determine-guilty',
        headers=default_headers,
        json={
            'cancel_reason_id': 'reason',
            'cancel_request_id': 1,
            'taxi_order_id': 'taxi',
            'performer': performer_request_property(),
            'waybill_info': waybill_info,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'alert_for_performer': {
            'alert_message': 'текст отмены value1, value2',
            'alert_title': 'Заголовок',
        },
    }

    validate_cancellation_db_entity()
