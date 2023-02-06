import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.config(
    REPOSITION_IN_POLLING_ORDER=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'reposition_v2_in_polling_order': '9.07'},
        },
    },
)
async def test_return_incoming_tags(
        taxi_contractor_orders_polling, mockserver,
):
    # Testing only reposition as it is the easiest
    # TODO add other tests
    @mockserver.handler('/reposition/v2/reposition', prefix=True)
    def _mock_reposition(request):
        return mockserver.make_response(status=500)

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={
            'reposition_state_etag': 'incoming_state_tag',
            'reposition_modes_etag': 'incoming_modes_tag',
            'reposition_offered_modes_etag': 'incoming_offered_modes_tag',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['reposition_state_etag'] == 'incoming_state_tag'
    assert data['reposition_modes_etag'] == 'incoming_modes_tag'
    assert (
        data['reposition_offered_modes_etag'] == 'incoming_offered_modes_tag'
    )
