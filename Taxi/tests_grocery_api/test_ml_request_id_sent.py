import pytest

from . import conftest
from . import tests_headers


@pytest.mark.now(conftest.DEFAULT_OFFER_TIME)
async def test_parcels(
        taxi_grocery_api,
        overlord_catalog,
        tristero_parcels,
        umlaas_grocery_eta,
        grocery_depots,
        grocery_surge,
):
    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    depot_id = 'depot-id-1'
    legacy_depot_id = '100'
    lat = 1.1
    lon = -2.2
    location = [lat, lon]
    customer_address = 'ymapsbm1://geo?ll={}%2C{}'.format(lat, lon)

    order = tristero_parcels.add_order(
        vendor=vendor,
        order_id=order_id,
        customer_address=customer_address,
        customer_location=location,
        ref_order=ref_order,
        status='received',
        depot_id=depot_id,
        delivery_date=conftest.DEFAULT_OFFER_TIME,
        token=token,
    )
    order.add_parcel(
        parcel_id='98765432-10ab-cdef-0000-000001000001:st-pa',
        status='in_depot',
        title='\u041f\u043e\u0441\u044b\u043b\u043a\u0430',
        image_url_template='parcels-image_template.jpg',
        quantity_limit='1',
    )

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        int(legacy_depot_id), depot_id=depot_id, location=location,
    )

    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    overlord_catalog.add_depot(
        depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )

    grocery_surge.add_record(
        legacy_depot_id=legacy_depot_id,
        timestamp=conftest.DEFAULT_OFFER_TIME,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    umlaas_grocery_eta.set_request_id(order_id)

    await taxi_grocery_api.invalidate_caches()

    response = await taxi_grocery_api.get(
        '/lavka/v1/api/v1/parcels/order_info',
        params={'vendor': vendor, 'ref_order': ref_order, 'token': token},
        headers=tests_headers.HEADERS,
    )
    assert response.status_code == 200
    assert umlaas_grocery_eta.umlaas_grocery_eta_times_called == 1
