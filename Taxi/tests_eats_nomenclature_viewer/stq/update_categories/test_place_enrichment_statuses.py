import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.stq.update_categories import constants

S3_PATH = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_TIME = dt.datetime(1999, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.s3(files={S3_PATH: 'single_object_data_template.json'})
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'product_for_data_template.sql'],
)
async def test_insert_new_place(stq_runner, sql):
    place_id_old = sql.save(models.Place(brand_id=constants.BRAND_ID))
    place_id_new_1 = sql.save(models.Place(brand_id=constants.BRAND_ID))
    place_id_new_2 = sql.save(models.Place(brand_id=constants.BRAND_ID))

    old_place_enrichment = models.PlaceEnrichmentStatus(
        place_id=place_id_old,
        are_prices_ready=True,
        are_stocks_ready=True,
        is_vendor_data_ready=True,
        updated_at=OLD_TIME,
    )
    sql.save(old_place_enrichment)

    expected_place_enrichment_1 = models.PlaceEnrichmentStatus(
        place_id=place_id_new_1,
        are_prices_ready=False,
        are_stocks_ready=False,
        is_vendor_data_ready=False,
    )
    expected_place_enrichment_2 = models.PlaceEnrichmentStatus(
        place_id=place_id_new_2,
        are_prices_ready=False,
        are_stocks_ready=False,
        is_vendor_data_ready=False,
    )

    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_PATH,
            'assortment_name': models.AssortmentName().name,
            'brand_id': constants.BRAND_ID,
            'place_ids': [
                expected_place_enrichment_1.place_id,
                expected_place_enrichment_2.place_id,
            ],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_place_enrichment_statuses = {
        i.place_id: i for i in sql.load_all(models.PlaceEnrichmentStatus)
    }
    assert len(db_place_enrichment_statuses) == 3
    db_place_enrichment_old = db_place_enrichment_statuses[
        old_place_enrichment.place_id
    ]
    db_place_enrichment_new_1 = db_place_enrichment_statuses[
        expected_place_enrichment_1.place_id
    ]
    db_place_enrichment_new_2 = db_place_enrichment_statuses[
        expected_place_enrichment_2.place_id
    ]

    assert db_place_enrichment_old == old_place_enrichment
    for db_place_enrichment_new, expected_place_enrichment in [
            (db_place_enrichment_new_1, expected_place_enrichment_1),
            (db_place_enrichment_new_2, expected_place_enrichment_2),
    ]:
        assert (
            db_place_enrichment_new.updated_at
            > db_place_enrichment_old.updated_at
        )
        db_place_enrichment_new.reset_field_recursive('updated_at')
        db_place_enrichment_new.reset_field_recursive('created_at')
        expected_place_enrichment.reset_field_recursive('updated_at')
        expected_place_enrichment.reset_field_recursive('created_at')
        assert db_place_enrichment_new == expected_place_enrichment


@pytest.mark.s3(files={S3_PATH: 'single_object_data_template.json'})
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_update(stq_runner, sql):
    place_enrichment_to_change = models.PlaceEnrichmentStatus(
        place_id=constants.PLACE_ID,
        are_prices_ready=True,
        are_stocks_ready=True,
        is_vendor_data_ready=True,
        updated_at=OLD_TIME,
    )
    sql.save(place_enrichment_to_change)

    expected_place_enrichment = place_enrichment_to_change.clone()
    expected_place_enrichment.updated_at = None
    expected_place_enrichment.are_prices_ready = False
    expected_place_enrichment.are_stocks_ready = False
    expected_place_enrichment.is_vendor_data_ready = False

    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_PATH,
            'assortment_name': models.AssortmentName().name,
            'brand_id': constants.BRAND_ID,
            'place_ids': [expected_place_enrichment.place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_place_enrichment_statuses = sql.load_all(models.PlaceEnrichmentStatus)
    assert len(db_place_enrichment_statuses) == 1
    db_place_enrichment_changed = db_place_enrichment_statuses[0]
    assert (
        db_place_enrichment_changed.updated_at
        > place_enrichment_to_change.updated_at
    )  # noqa: E501
    db_place_enrichment_changed.reset_field_recursive('updated_at')
    db_place_enrichment_changed.reset_field_recursive('created_at')
    assert db_place_enrichment_changed == expected_place_enrichment
