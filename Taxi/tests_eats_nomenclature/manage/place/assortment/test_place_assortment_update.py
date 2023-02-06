import datetime as dt

import pytest
import pytz

from .... import utils


HANDLER = '/v1/manage/place/assortment'
PLACE_ID = 1
ASSORTMENT_NAME = 'new_assortment_name'
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_404_unknown_assortment_name(taxi_eats_nomenclature):
    unknown_assortment_name = 'unknown_assortment_name'
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?place_id={PLACE_ID}'
        + f'&assortment_name={unknown_assortment_name}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_404_unknown_place_id(taxi_eats_nomenclature):
    unknown_place_id = 2
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={unknown_place_id}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_404_inactive_assortment(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?place_id={PLACE_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert response.status_code == 404


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204_null_assortment_name(
        taxi_eats_nomenclature, pgsql, testpoint,
):
    @testpoint('yt-logger-new-assortment')
    def yt_logger(data):
        del data['timestamp_raw']
        assert data == {
            'place_id': str(PLACE_ID),
            'timestamp': MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S'),
        }

    insert_place_assortment(pgsql, None)
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID}',
    )
    assert response.status_code == 204
    assert get_place_default_assortment(pgsql, PLACE_ID) is None
    assert yt_logger.has_calls


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204_not_null_assortment_name(
        taxi_eats_nomenclature, pgsql, testpoint,
):
    @testpoint('yt-logger-new-assortment')
    def yt_logger(data):
        del data['timestamp_raw']
        assert data == {
            'place_id': str(PLACE_ID),
            'timestamp': MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S'),
        }

    insert_place_assortment(pgsql, 2)
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?place_id={PLACE_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert response.status_code == 204
    assert get_place_default_assortment(pgsql, PLACE_ID) == 2
    assert yt_logger.has_calls


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204_null_place_default_assortment(
        taxi_eats_nomenclature, pgsql, testpoint,
):
    @testpoint('yt-logger-new-assortment')
    def yt_logger(data):
        del data['timestamp_raw']
        assert data == {
            'place_id': str(PLACE_ID),
            'timestamp': MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S'),
        }

    del_place_default_assortment(pgsql, PLACE_ID)
    insert_place_assortment(pgsql, 2)
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?place_id={PLACE_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert response.status_code == 204
    assert get_place_default_assortment(pgsql, PLACE_ID) == 2
    assert yt_logger.has_calls


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
@pytest.mark.parametrize(
    **utils.gen_bool_params('enqueue_fts_if_new_default_assortment'),
)
@pytest.mark.parametrize(**utils.gen_bool_params('enable_fts_enqueue'))
async def test_enqueue_fts(
        taxi_eats_nomenclature,
        pgsql,
        stq,
        update_taxi_config,
        # parametrize
        enqueue_fts_if_new_default_assortment,
        enable_fts_enqueue,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {
            'enqueue_fts_if_new_default_assortment': (
                enqueue_fts_if_new_default_assortment
            ),
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_ASSORTMENT_ACTIVATION_NOTIFICATION_SETTINGS',
        {
            'common_delay_in_seconds': 0,
            'is_enabled': True,
            'per_component_additional_settings': {
                '__default__': {
                    'is_enabled': True,
                    'additional_delay_in_seconds': 0,
                },
                'stq_eats_full_text_search_indexer_update_retail_place': {
                    'is_enabled': enable_fts_enqueue,
                    'additional_delay_in_seconds': 0,
                },
            },
        },
    )

    insert_place_assortment(pgsql, 2)
    await taxi_eats_nomenclature.post(
        HANDLER
        + f'?place_id={PLACE_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert stq.eats_full_text_search_indexer_update_retail_place.has_calls == (
        enqueue_fts_if_new_default_assortment and enable_fts_enqueue
    )
    if enqueue_fts_if_new_default_assortment and enable_fts_enqueue:
        assert (
            stq.eats_full_text_search_indexer_update_retail_place.times_called
            == 1
        )
        task_info = (
            stq.eats_full_text_search_indexer_update_retail_place.next_call()
        )
        assert task_info['kwargs']['place_slug'] == 'slug1'


def get_place_default_assortment(pgsql, place_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select trait_id
        from eats_nomenclature.place_default_assortments
        where place_id={place_id}
        """,
    )
    return list(cursor)[0][0]


def del_place_default_assortment(pgsql, place_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        delete from eats_nomenclature.place_default_assortments
        where place_id={place_id}
        """,
    )


def insert_place_assortment(
        pgsql, trait_id, assortment_id=1, place_id=PLACE_ID,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.place_assortments (
            place_id, trait_id, assortment_id
        ) values ({place_id}, {trait_id or 'null'}, {assortment_id})
        """,
    )
