import json
import uuid

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


async def test_delete_personal_data_one_way(taxi_bank_applications, pgsql):
    some_json = {'a': 0, 'b': '0b', 'c': False}
    some_form = json.dumps(some_json)

    application_to_save = db_helpers.insert_simpl_application(
        pgsql, some_form, some_form, '0',
    )
    application_to_delete = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=some_form,
        prenormalized_form=some_form,
        agreement_version='0',
        submit_idempotency_token=str(uuid.uuid4()),
        buid='buid_delete_pd',
        create_idempotency_token=str(uuid.uuid4()),
        update_idempotency_token=str(uuid.uuid4()),
    )

    db_helpers.insert_simpl_id_draft_form(
        pgsql, application_to_save, some_form,
    )
    db_helpers.insert_simpl_id_draft_form(
        pgsql, application_to_delete, some_form,
    )

    db_helpers.insert_simpl_id_app_hist(
        pgsql=pgsql,
        application_id=application_to_save,
        submitted_form=some_form,
        prenormalized_form=some_form,
    )
    db_helpers.insert_simpl_id_app_hist(
        pgsql=pgsql,
        application_id=application_to_delete,
        submitted_form=some_form,
        prenormalized_form=some_form,
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification'
        '/delete_personal_data',
        headers=common.default_headers(),
        json={'application_id': application_to_delete},
    )

    assert response.status_code == 200

    assert db_helpers.get_simpl_id_app(
        pgsql, application_to_save,
    ).submitted_form == json.loads(some_form)

    simplified_identification_app = db_helpers.get_simpl_id_app(
        pgsql, application_to_delete,
    )
    assert simplified_identification_app.submitted_form is None
    assert simplified_identification_app.prenormalized_form is None

    assert (
        db_helpers.get_simpl_id_draft_form(pgsql, application_to_save)
        is not None
    )
    assert (
        db_helpers.get_simpl_id_draft_form(pgsql, application_to_delete)
        is None
    )

    assert (
        db_helpers.get_simpl_id_app_hist(
            pgsql, application_to_save,
        ).submitted_form
        is not None
    )

    # pylint: disable=invalid-name
    simplified_identification_app_hist = db_helpers.get_simpl_id_app_hist(
        pgsql, application_to_delete,
    )
    assert simplified_identification_app_hist.submitted_form is None
    assert simplified_identification_app_hist.prenormalized_form is None

    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification'
        '/delete_personal_data',
        headers=common.default_headers(),
        json={'application_id': application_to_delete},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'expected_code,application_id',
    [(400, 'invalid_uuid'), (404, 'A56DAB40-2BA1-44B6-965E-47C1C1216403')],
)
async def test_delete_personal_data_failures(
        taxi_bank_applications, pgsql, expected_code, application_id,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification'
        '/delete_personal_data',
        headers=common.default_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == expected_code
