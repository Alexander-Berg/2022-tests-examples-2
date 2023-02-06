import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.stq.activate_assortment import constants

S3_AVAILABILITY_FILE = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_call(stq_runner, sql):
    assortment_name = models.AssortmentName()

    place_enrichment_to_activate = models.PlaceEnrichmentStatus(
        place_id=constants.PLACE_ID,
        are_stocks_ready=True,
        is_vendor_data_ready=True,
        are_prices_ready=True,
    )
    sql.save(place_enrichment_to_activate)

    place_assortment_to_activate = models.PlaceAssortment(
        place_id=constants.PLACE_ID,
        assortment_name=assortment_name,
        in_progress_assortment=models.Assortment(
            updated_at=DEFAULT_TIME, created_at=DEFAULT_TIME,
        ),
        updated_at=OLD_TIME,
    )
    sql.save(place_assortment_to_activate)

    await stq_runner.eats_nomenclature_viewer_activate_assortment.call(
        task_id='1',
        kwargs={
            'place_id': constants.PLACE_ID,
            'assortment_name_id': sql.get_object_id(assortment_name),
        },
    )

    db_place_assortments = sql.load_all(models.PlaceAssortment)
    assert len(db_place_assortments) == 1
    db_place_assortment_activated = db_place_assortments[0]

    assert (
        db_place_assortment_activated.updated_at
        > place_assortment_to_activate.updated_at
    )
    assert (
        db_place_assortment_activated.active_assortment
        == place_assortment_to_activate.in_progress_assortment
    )
    assert not db_place_assortment_activated.in_progress_assortment


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_ignore_incomplete_enrichment(stq_runner, sql):
    assortment_name = models.AssortmentName()

    place_enrichment = models.PlaceEnrichmentStatus(
        place_id=constants.PLACE_ID,
        are_stocks_ready=False,
        is_vendor_data_ready=False,
        are_prices_ready=False,
    )
    sql.save(place_enrichment)

    place_assortment = models.PlaceAssortment(
        place_id=constants.PLACE_ID,
        assortment_name=assortment_name,
        in_progress_assortment=models.Assortment(),
        updated_at=OLD_TIME,
    )
    sql.save(place_assortment)

    await stq_runner.eats_nomenclature_viewer_activate_assortment.call(
        task_id='1',
        kwargs={
            'place_id': constants.PLACE_ID,
            'assortment_name_id': sql.get_object_id(assortment_name),
        },
    )

    db_place_assortments = sql.load_all(models.PlaceAssortment)
    assert len(db_place_assortments) == 1
    db_place_assortment = db_place_assortments[0]

    assert db_place_assortment.updated_at == place_assortment.updated_at
    assert place_assortment.in_progress_assortment
    assert not place_assortment.active_assortment


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'assortment_name.sql'],
)
async def test_stq_error_limit(stq_runner, testpoint, update_taxi_config):
    max_retries_on_error = 2
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_PROCESSING_V2',
        {'__default__': {'max_retries_on_error': max_retries_on_error}},
    )

    @testpoint(
        'eats-nomenclature-viewer_stq_activate_assortment::failure-injector',
    )
    def task_testpoint(_):
        return {'inject': True}

    for i in range(max_retries_on_error):
        await stq_runner.eats_nomenclature_viewer_activate_assortment.call(
            task_id='1',
            kwargs={
                'place_id': constants.PLACE_ID,
                'assortment_name_id': constants.ASSORTMENT_NAME_ID,
            },
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_nomenclature_viewer_activate_assortment.call(
        task_id='1',
        kwargs={
            'place_id': constants.PLACE_ID,
            'assortment_name_id': constants.ASSORTMENT_NAME_ID,
        },
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
