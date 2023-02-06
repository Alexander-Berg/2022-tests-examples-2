import pytest


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'WithoutVatOfferAccept',
            'source_field': 'subject',
            'sf_api_name': 'Subject',
            'lookup_alias': 'parks_accept_offer',
            'load_period': 1,
        },
        {
            'source': 'WithoutVatOfferAccept',
            'source_field': 'clid',
            'sf_api_name': 'Cl ID',
            'lookup_alias': 'parks_accept_offer',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'parks_accept_offer': {
            'sf_org': 'pro',
            'sf_key': 'Cl_ID',
            'sf_object': 'Account',
            'source_key': 'clid',
        },
    },
)
async def test_load_offer_accept(taxi_sf_data_load_web, pgsql):
    cursor = pgsql['sf_data_load'].cursor()

    corp_call = {'clid': '654321'}

    resp = await taxi_sf_data_load_web.put(
        '/v1/offer-accept/parks', json=corp_call,
    )
    assert resp.status == 200

    resp = await taxi_sf_data_load_web.put(
        '/v1/offer-accept/parks', json=corp_call,
    )

    assert resp.status == 200

    query = """
        SELECT
            source_class_name,
            source_field,
            sf_api_field_name,
            lookup_alias,
            data_value
        FROM sf_data_load.loading_fields
        ORDER BY source_field;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == [
        (
            'WithoutVatOfferAccept',
            'clid',
            'Cl ID',
            'parks_accept_offer',
            '654321',
        ),
        (
            'WithoutVatOfferAccept',
            'subject',
            'Subject',
            'parks_accept_offer',
            'Без NDS-ная схема/оферта для 654321',
        ),
    ]
