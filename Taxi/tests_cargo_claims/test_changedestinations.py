import pytest

from . import conftest

DESTINATION_PICKUPED = {
    'extra_data': {
        'comment': (
            'Код от подъезда/домофона: door_2.\nКомментарий: comment_2.'
        ),
    },
    'fullname': '2',
    'geopoint': [37.0, 55.8],
    'type': 'address',
}

DESTINATION_DELIVERED = {
    'extra_data': {
        'comment': (
            'Код от подъезда/домофона: door_3.\nКомментарий: comment_3.'
        ),
    },
    'fullname': '3',
    'geopoint': [37.0, 55.0],
    'type': 'address',
}


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize(
    'destination_pickuped, destination_delivering',
    (
        # pytest.param(None, DESTINATION_DELIVERED, id='config_default'),
        pytest.param(
            DESTINATION_PICKUPED,
            DESTINATION_DELIVERED,
            marks=(
                pytest.mark.config(
                    CARGO_CHANGE_DESTINATIONS=[
                        'mark_performer_found',
                        'point_visited',
                        'point_skipped',
                        'return',
                    ],
                )
            ),
            id='config_performer_found',
        ),
    ),
)
async def test_confirm_changedestinations(
        taxi_cargo_claims,
        state_controller,
        mockserver,
        destination_pickuped,
        destination_delivering,
):
    destinations = []

    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        assert len(request.json['destinations']) == 1
        assert request.json['disable_price_changing'] is True
        destinations.append(request.json['destinations'][0])
        return conftest.CHANGEDESTINATIONS_RESPONSE

    state_controller.use_create_version('v2')
    await state_controller.apply(target_status='pickuped', next_point_order=2)

    # skip changedestinations for first point
    expected_times_called = 0
    if destination_pickuped is not None:
        expected_times_called = expected_times_called + 1
    assert _changedestinations.times_called == expected_times_called

    await state_controller.apply(
        target_status='delivered', next_point_order=None, fresh_claim=False,
    )

    if destination_delivering is not None:
        expected_times_called = expected_times_called + 1
    assert _changedestinations.times_called == expected_times_called

    if destination_pickuped is not None:
        assert destinations[0] == destination_pickuped
    if destination_delivering is not None:
        assert destinations[-1] == destination_delivering
