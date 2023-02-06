import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_categories import constants
from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils

S3_CATEGORIES_FILE = '/some_path_to_categories.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


async def test_insert_new_place(stq_runner, load, mds_s3_storage, sql):
    brand_id = sql.save(models.Brand())
    old_place_id = sql.save(models.Place(brand_id=brand_id))
    new_place_id = sql.save(models.Place(brand_id=brand_id))

    # product for template
    sql.save(
        models.Product(
            brand_id=brand_id,
            nmn_id=constants.DEFAULT_CATEGORY_PRODUCT_VALUES['id'],
        ),
    )

    assortment_name = models.AssortmentName(updated_at=OLD_TIME)
    old_place_assortment = models.PlaceAssortment(
        place_id=old_place_id,
        assortment_name=assortment_name,
        updated_at=OLD_TIME,
    )
    sql.save(old_place_assortment)

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': assortment_name.name,
            'brand_id': brand_id,
            'place_ids': [new_place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    place_id_to_place_assortment = {
        i.place_id: i for i in sql.load_all(models.PlaceAssortment)
    }
    assert len(place_id_to_place_assortment) == 2

    db_place_assortment_old = place_id_to_place_assortment[old_place_id]
    db_place_assortment_new = place_id_to_place_assortment[new_place_id]

    assert db_place_assortment_old == old_place_assortment
    assert (
        db_place_assortment_new.updated_at > db_place_assortment_old.updated_at
    )
    assert db_place_assortment_new.in_progress_assortment is not None
    assert db_place_assortment_new.active_assortment is None
    assert db_place_assortment_new.assortment_name == assortment_name


async def test_insert_new_assortment_name(
        stq_runner, load, mds_s3_storage, sql,
):
    brand_id = sql.save(models.Brand())
    place_id = sql.save(models.Place(brand_id=brand_id))

    # product for template
    sql.save(
        models.Product(
            brand_id=brand_id,
            nmn_id=constants.DEFAULT_CATEGORY_PRODUCT_VALUES['id'],
        ),
    )

    assortment_name = models.AssortmentName(updated_at=OLD_TIME)
    old_place_assortment = models.PlaceAssortment(
        place_id=place_id,
        assortment_name=assortment_name,
        updated_at=OLD_TIME,
    )
    sql.save(old_place_assortment)

    expected_assortment_name = models.AssortmentName()

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': expected_assortment_name.name,
            'brand_id': brand_id,
            'place_ids': [place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    name_to_place_assortment = {
        i.assortment_name.name: i for i in sql.load_all(models.PlaceAssortment)
    }
    assert len(name_to_place_assortment) == 2

    db_place_assortment_old = name_to_place_assortment[assortment_name.name]
    db_place_assortment_new = name_to_place_assortment[
        expected_assortment_name.name
    ]

    assert db_place_assortment_old == old_place_assortment
    assert db_place_assortment_new.updated_at > old_place_assortment.updated_at
    assert db_place_assortment_new.in_progress_assortment is not None
    assert db_place_assortment_new.active_assortment is None


@pytest.mark.parametrize(
    **utils.gen_bool_params('is_outdated_in_progress_assortment'),
)
async def test_update_in_progress(
        stq_runner,
        load,
        mds_s3_storage,
        sql,
        update_taxi_config,
        # parametrize
        is_outdated_in_progress_assortment,
):
    outdated_in_progress_treshold = dt.timedelta(minutes=30)
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_UPDATE_CATEGORIES',
        {
            'in_progress_assortment_timeout_in_min': (
                outdated_in_progress_treshold.seconds / 60
            ),
        },
    )

    assortment_created_at = utils.now_with_tz()
    if is_outdated_in_progress_assortment:
        assortment_created_at -= outdated_in_progress_treshold * 2

    brand_id = sql.save(models.Brand())
    place_id = sql.save(models.Place(brand_id=brand_id))

    # product for template
    sql.save(
        models.Product(
            brand_id=brand_id,
            nmn_id=constants.DEFAULT_CATEGORY_PRODUCT_VALUES['id'],
        ),
    )

    old_assortment = models.Assortment(
        updated_at=OLD_TIME, created_at=assortment_created_at,
    )
    place_assortment = models.PlaceAssortment(
        place_id=place_id,
        in_progress_assortment=old_assortment,
        updated_at=OLD_TIME,
    )
    sql.save(place_assortment)

    mds_s3_storage.put_object(
        S3_CATEGORIES_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_categories.call(
        task_id='1',
        kwargs={
            's3_path': S3_CATEGORIES_FILE,
            'assortment_name': place_assortment.assortment_name.name,
            'brand_id': brand_id,
            'place_ids': [place_id],
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_place_assortments = sql.load_all(models.PlaceAssortment)
    assert len(db_place_assortments) == 1

    db_place_assortment = db_place_assortments[0]
    if is_outdated_in_progress_assortment:
        assert db_place_assortment.updated_at > place_assortment.updated_at
        assert (
            db_place_assortment.in_progress_assortment.assortment_id
            != old_assortment.assortment_id
        )
    else:
        assert db_place_assortment.updated_at == place_assortment.updated_at
        assert db_place_assortment.in_progress_assortment == old_assortment
