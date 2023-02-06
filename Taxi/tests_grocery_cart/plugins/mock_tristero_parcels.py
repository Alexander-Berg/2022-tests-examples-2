import pytest

from tests_grocery_cart.plugins import keys


@pytest.fixture(name='tristero_parcels', autouse=True)
def mock_tristero_parcels(mockserver):
    parcels = {}

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/parcels-info',
    )
    def mock_tristero_parcels_info(request):
        return {
            'parcels': [
                parcels[parcel_id]
                for parcel_id in request.json['parcel_ids']
                if parcel_id in parcels
            ],
        }

    class Context:
        def add_parcel(
                self,
                *,
                parcel_id,
                depot_id=keys.DEFAULT_WMS_DEPOT_ID,
                quantity_limit='1',
                status='in_depot',
                order_id=None,
                vendor='market',
                can_left_at_door=True,
                request_kind=None,
        ):
            parcels[parcel_id] = {
                'parcel_id': parcel_id,
                'depot_id': depot_id,
                'title': f'title for {parcel_id}',
                'quantity_limit': quantity_limit,
                'subtitle': f'subtitle for {parcel_id}',
                'image_url_template': f'url for {parcel_id}',
                'state': status,
                'state_meta': {},
                'measurements': {
                    'width': 1,
                    'height': 2,
                    'length': 4,
                    'weight': 8,
                },
                'order_id': order_id,
                'vendor': vendor,
                'can_left_at_door': can_left_at_door,
                'request_kind': request_kind,
            }

        def times_called(self):
            return mock_tristero_parcels_info.times_called

        def flush(self):
            mock_tristero_parcels_info.flush()

    context = Context()
    return context
