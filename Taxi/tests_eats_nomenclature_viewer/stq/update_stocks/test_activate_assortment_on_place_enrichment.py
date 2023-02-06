import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_stocks import constants

S3_PATH = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.s3(
    files={
        S3_PATH: 'stock_item_template.json',
        constants.S3_AVAILABILITY_FILE: 'availability_item_template.json',
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=[
        'brand.sql',
        'place.sql',
        'product_for_item_template.sql',
        'availability_file.sql',
    ],
)
async def test_place_enrichment_values(stq_runner, sql):

    sql.save(
        models.PlaceAssortment(
            place_id=constants.PLACE_ID,
            in_progress_assortment=models.Assortment(),
        ),
    )

    place_enrichment = models.PlaceEnrichmentStatus(
        place_id=constants.PLACE_ID,
        are_stocks_ready=False,
        is_vendor_data_ready=False,
        are_prices_ready=False,
    )
    sql.save(place_enrichment)

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_PATH,
            'place_id': constants.PLACE_ID,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_place_enrichment_statuses = sql.load_all(models.PlaceEnrichmentStatus)
    assert len(db_place_enrichment_statuses) == 1
    db_place_enrichment = db_place_enrichment_statuses[0]

    assert db_place_enrichment.are_stocks_ready


@pytest.mark.parametrize(**utils.gen_bool_params('is_place_enriched'))
@pytest.mark.s3(
    files={
        S3_PATH: 'stock_item_template.json',
        constants.S3_AVAILABILITY_FILE: 'availability_item_template.json',
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=[
        'brand.sql',
        'place.sql',
        'product_for_item_template.sql',
        'availability_file.sql',
    ],
)
async def test_activate_assortment_call(
        stq,
        stq_runner,
        sql,
        # parametrize
        is_place_enriched,
):
    sql.save(
        models.PlaceAssortment(
            place_id=constants.PLACE_ID,
            in_progress_assortment=models.Assortment(),
        ),
    )

    place_enrichment = models.PlaceEnrichmentStatus(
        place_id=constants.PLACE_ID,
        are_stocks_ready=is_place_enriched,
        is_vendor_data_ready=is_place_enriched,
        are_prices_ready=is_place_enriched,
    )
    sql.save(place_enrichment)

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_PATH,
            'place_id': constants.PLACE_ID,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )
    assert (
        stq.eats_nomenclature_viewer_activate_assortment.times_called
        == is_place_enriched
    )


@pytest.mark.parametrize(**utils.gen_bool_params('is_in_progress'))
@pytest.mark.s3(
    files={
        S3_PATH: 'stock_item_template.json',
        constants.S3_AVAILABILITY_FILE: 'availability_item_template.json',
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=[
        'brand.sql',
        'place.sql',
        'product_for_item_template.sql',
        'availability_file.sql',
    ],
)
async def test_in_progress_assortment(
        stq,
        stq_runner,
        sql,
        # parametrize
        is_in_progress,
):
    assortment_name = models.AssortmentName()

    sql.save(
        models.PlaceEnrichmentStatus(
            place_id=constants.PLACE_ID,
            are_stocks_ready=True,
            is_vendor_data_ready=True,
            are_prices_ready=True,
        ),
    )
    if is_in_progress:
        sql.save(
            models.PlaceAssortment(
                place_id=constants.PLACE_ID,
                assortment_name=assortment_name,
                in_progress_assortment=models.Assortment(),
            ),
        )
    else:
        sql.save(
            models.PlaceAssortment(
                place_id=constants.PLACE_ID,
                assortment_name=assortment_name,
                active_assortment=models.Assortment(),
            ),
        )

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_PATH,
            'place_id': constants.PLACE_ID,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )
    assert (
        stq.eats_nomenclature_viewer_activate_assortment.times_called
        == is_in_progress
    )


@pytest.mark.s3(
    files={
        S3_PATH: 'stock_item_template.json',
        constants.S3_AVAILABILITY_FILE: 'availability_item_template.json',
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=[
        'brand.sql',
        'place.sql',
        'product_for_item_template.sql',
        'availability_file.sql',
    ],
)
async def test_stq_args(stq, stq_runner, sql):
    sql.save(
        models.PlaceEnrichmentStatus(
            place_id=constants.PLACE_ID,
            are_stocks_ready=True,
            is_vendor_data_ready=True,
            are_prices_ready=True,
        ),
    )

    assortment_names = [models.AssortmentName() for _ in range(0, 2)]
    for assortment_name in assortment_names:
        sql.save(
            models.PlaceAssortment(
                place_id=constants.PLACE_ID,
                assortment_name=assortment_name,
                in_progress_assortment=models.Assortment(),
            ),
        )

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_PATH,
            'place_id': constants.PLACE_ID,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )
    stq_calls = [
        stq.eats_nomenclature_viewer_activate_assortment.next_call()
        for _ in range(
            0, stq.eats_nomenclature_viewer_activate_assortment.times_called,
        )
    ]
    for stq_call in stq_calls:
        kwargs = stq_call['kwargs']
        assert (
            stq_call['id']
            == f'{kwargs["place_id"]}_{kwargs["assortment_name_id"]}'
        )
    assert {i['kwargs']['place_id'] for i in stq_calls} == {constants.PLACE_ID}
    assert {i['kwargs']['assortment_name_id'] for i in stq_calls} == {
        sql.get_object_id(i) for i in assortment_names
    }
