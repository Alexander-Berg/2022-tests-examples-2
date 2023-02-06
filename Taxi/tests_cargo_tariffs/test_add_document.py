import pytest


from testsuite.utils import matching


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_simple_document_create(
        v1_tariff_creator, v1_document_creator, default_ndd_client_tariff,
):
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    tariff_id = resp.json()['id']
    resp = await v1_document_creator.create(
        tariff_id, default_ndd_client_tariff,
    )
    assert resp.status_code == 200
    assert resp.json()['id'] == matching.AnyString()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_document_create_without_tariff(
        v1_document_creator, default_ndd_client_tariff,
):
    tariff_id = 'some_tariff_id'
    resp = await v1_document_creator.create(
        tariff_id, default_ndd_client_tariff,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'tariff_not_exists'


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_simple_document_create_check(
        v1_tariff_creator, v1_document_creator, default_ndd_client_tariff,
):
    v1_document_creator.url += '/check'
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    tariff_id = resp.json()['id']
    resp = await v1_document_creator.create(
        tariff_id, default_ndd_client_tariff,
    )
    assert resp.status_code == 200
    assert resp.json()['change_doc_id'] == tariff_id
    assert resp.json()['data']['tariff_id'] == tariff_id
    assert resp.json()['data']['document'] == default_ndd_client_tariff


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_document_create_check_with_diff(
        v1_tariff_creator,
        v1_document_creator,
        default_ndd_client_tariff,
        zero_ndd_client_tariff,
):
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    tariff_id = resp.json()['id']
    resp = await v1_document_creator.create(
        tariff_id, default_ndd_client_tariff,
    )
    assert resp.status_code == 200
    v1_document_creator.url += '/check'
    resp = await v1_document_creator.create(tariff_id, zero_ndd_client_tariff)
    assert resp.status_code == 200
    assert resp.json()['change_doc_id'] == tariff_id
    assert resp.json()['data']['tariff_id'] == tariff_id
    assert resp.json()['data']['document'] == zero_ndd_client_tariff
    assert resp.json()['diff']['current']['tariff_id'] == tariff_id
    assert (
        resp.json()['diff']['current']['document'] == default_ndd_client_tariff
    )
    assert resp.json()['diff']['new']['tariff_id'] == tariff_id
    assert resp.json()['diff']['new']['document'] == zero_ndd_client_tariff


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_document_create_check_without_tariff(
        v1_document_creator, default_ndd_client_tariff,
):
    tariff_id = 'some_tariff_id'
    resp = await v1_document_creator.create(
        tariff_id, default_ndd_client_tariff,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'tariff_not_exists'
