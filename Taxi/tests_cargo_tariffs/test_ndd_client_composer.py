import pytest

from testsuite.utils import matching


@pytest.fixture(name='v1_ndd_client_composer')
async def _v1_ndd_client_composer(taxi_cargo_tariffs):
    class ComposerClient:
        url = '/tariffs/v1/ndd-client/v1/composer'
        retrieve_url = url + '/retrieve'
        payload = {
            'employer_id': 'corp_id_1',
            'trips_number': 102,
            'source_point': [56.1, 36.1],
            'destination_point': [56.756676, 37.549591],
            'tariff_category': 'interval_with_fees',
        }

        async def compose(self):
            return await taxi_cargo_tariffs.post(self.url, json=self.payload)

        async def retrieve(self, composition_id):
            return await taxi_cargo_tariffs.get(
                self.retrieve_url, params={'composition_id': composition_id},
            )

    return ComposerClient()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER={
        'ndd_client': [
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
            {
                'condition_group_name': 'source_geo',
                'fields': [{'name': 'source_zone'}],
            },
        ],
    },
)
async def test_simple(
        taxi_cargo_tariffs,
        v1_ndd_client_composer,
        insert_tariffs_to_db,
        default_ndd_client_tariff,
        fill_db,
):
    _, document_id = await insert_tariffs_to_db.insert_dummy()
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    _, document_id_2 = await fill_db()
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 200
    assert resp.json() == {
        'composition_id': matching.any_string,
        'tariff': default_ndd_client_tariff,
        'composer_process': {'tariff_nodes': [document_id, document_id_2]},
    }
    retrieve_resp = await v1_ndd_client_composer.retrieve(
        composition_id=resp.json()['composition_id'],
    )
    assert retrieve_resp.json() == resp.json()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER={
        'ndd_client': [
            {
                'condition_group_name': 'source_geo',
                'fields': [{'name': 'source_zone'}],
            },
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
        ],
    },
)
async def test_picking_with_config(
        taxi_cargo_tariffs, v1_ndd_client_composer, insert_tariffs_to_db,
):
    await insert_tariffs_to_db.insert_dummy()
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 200
    assert resp.json()['tariff']['delivery']['intake'] == '0'


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_two_same_in_a_row(
        taxi_cargo_tariffs, v1_ndd_client_composer, fill_db,
):
    await fill_db()
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 200

    resp2 = await v1_ndd_client_composer.compose()
    assert resp2.status_code == 200

    assert resp.json() == resp2.json()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_not_matched_by_all_conditions(
        taxi_cargo_tariffs, v1_ndd_client_composer,
):
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    v1_ndd_client_composer.payload['employer_id'] = 'not_matched_employer_id'
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 404


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER={
        'ndd_client': [
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
            {
                'condition_group_name': 'source_geo',
                'fields': [{'name': 'source_zone'}],
            },
        ],
    },
)
async def test_not_matched_by_first_condition(
        taxi_cargo_tariffs, v1_ndd_client_composer, insert_tariffs_to_db,
):
    insert_tariffs_to_db.conditions = [
        {
            'field_name': 'employer_id',
            'sign': 'equal',
            'value': 'corp_client_1',
        },
    ]
    await insert_tariffs_to_db.insert_dummy()
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    v1_ndd_client_composer.payload['employer_id'] = 'not_matched_employer_id'
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 404


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER={
        'ndd_client': [
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
            {
                'condition_group_name': 'source_geo',
                'fields': [{'name': 'source_zone'}],
            },
        ],
    },
)
async def test_not_matched_by_not_first_condition(
        taxi_cargo_tariffs, v1_ndd_client_composer, insert_tariffs_to_db,
):
    insert_tariffs_to_db.conditions = [
        {
            'field_name': 'employer_id',
            'sign': 'equal',
            'value': 'corp_client_1',
        },
    ]
    await insert_tariffs_to_db.insert_dummy()
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    v1_ndd_client_composer.payload['employer_id'] = 'corp_client_1'
    v1_ndd_client_composer.payload['source_point'] = [100, 100]
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 404


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_big_tariff_zone(
        taxi_cargo_tariffs, insert_tariffs_to_db, v1_ndd_client_composer,
):
    await insert_tariffs_to_db.insert_dummy(source_zone='russia')
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    resp = await v1_ndd_client_composer.compose()
    assert resp.status_code == 200


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER={
        'ndd_client': [
            {
                'condition_group_name': 'source_geo',
                'fields': [{'name': 'source_zone'}],
            },
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
        ],
    },
)
async def test_two_tariff_zones(
        taxi_cargo_tariffs, insert_tariffs_to_db, v1_ndd_client_composer,
):
    await insert_tariffs_to_db.insert_dummy(source_zone='moscow', intake='200')
    await insert_tariffs_to_db.insert_dummy(source_zone='russia', intake='300')
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
    resp = await v1_ndd_client_composer.compose()
    assert resp.json()['tariff']['delivery']['intake'] == '200'
