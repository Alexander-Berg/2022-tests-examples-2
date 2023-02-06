import datetime

import pytest

from taxi.stq import async_worker_ng as async_worker
from testsuite.utils import http

from selfemployed.services import nalogru
from selfemployed.stq import finish_qse_binding


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id');
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_id', 'PHONE_PD_ID',
                TRUE, NULL, TRUE, NULL)
        """,
    ],
)
async def test_ok(
        stq3_context, patch, stq, mock_fleet_synchronizer, mock_personal,
):
    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check(request_id: str):
        assert request_id == 'bind_request_id'
        return nalogru.nalogru_binding.BindingStatus.COMPLETED, '012345678901'

    @mock_fleet_synchronizer('/v1/mapping/driver')
    def _mapping_driver(request):
        return {
            'mapping': [
                {
                    'app_family': 'taximeter',
                    'park_id': 'park_id',
                    'driver_id': 'contractor_profile_id',
                },
            ],
        }

    @mock_personal('/v1/tins/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': '012345678901', 'validate': True}
        return {'value': '01345678901', 'id': 'INN_PD_ID'}

    await finish_qse_binding.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='task_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='selfemployed_fns_finish_qse_binding',
            eta=None,
        ),
        park_id='park_id',
        contractor_id='contractor_id',
        phone_pd_id='PHONE_PD_ID',
    )

    form_record = await stq3_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='park_id',
        contractor_profile_id='contractor_id',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id='INN_PD_ID',
        is_phone_verified=True,
        sms_track_id=None,
        is_accepted=True,
        requested_at=None,
        increment=2,
    )

    binding_record = await stq3_context.pg.main_master.fetchrow(
        'SELECT * FROM se.nalogru_phone_bindings ORDER BY phone_pd_id',
    )
    binding_dict = dict(binding_record)
    del binding_dict['created_at']
    del binding_dict['updated_at']
    assert binding_dict == dict(
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id='INN_PD_ID',
        status='COMPLETED',
        bind_request_id=None,
        bind_requested_at=None,
        increment=2,
        exceeded_legal_income_year=None,
        exceeded_reported_income_year=None,
        business_unit='taxi',
    )

    profile_record = await stq3_context.pg.main_master.fetchrow(
        'SELECT * FROM se.finished_profiles',
    )
    profile_dict = dict(profile_record)
    del profile_dict['created_at']
    del profile_dict['updated_at']
    assert profile_dict == dict(
        park_id='park_id',
        contractor_profile_id='contractor_profile_id',
        phone_pd_id='PHONE_PD_ID',
        do_send_receipts=True,
        inn_pd_id='INN_PD_ID',
        is_own_park=False,
        increment=1,
        business_unit='taxi',
    )
    assert stq.selfemployed_fns_tag_contractor.next_call() == {
        'queue': 'selfemployed_fns_tag_contractor',
        'id': (
            'ab801519a5ebcb35abcfd92d92e2b92c1405ebcbb6801d937845a8d2156a9586'
        ),
        'args': [],
        'kwargs': {
            'trigger_id': 'quasi_profile_created',
            'park_id': 'park_id',
            'contractor_id': 'contractor_profile_id',
        },
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
    }
    assert stq.selfemployed_fns_tag_contractor.next_call() == {
        'queue': 'selfemployed_fns_tag_contractor',
        'id': (
            'dd53bb6b5b6d34a1b7a8471338823e02198f28b96d148e841c1a5720fb036f4b'
        ),
        'args': [],
        'kwargs': {
            'trigger_id': 'quasi_reporting_enabled',
            'park_id': 'park_id',
            'contractor_id': 'contractor_profile_id',
        },
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS', 'bind_request_id');
        INSERT INTO se.quasi_profile_forms
            (park_id, contractor_profile_id, phone_pd_id,
             is_phone_verified, sms_track_id, is_accepted, requested_at)
        VALUES ('park_id', 'contractor_id', 'PHONE_PD_ID',
                TRUE, NULL, TRUE, NULL)
        """,
    ],
)
@pytest.mark.config(
    SELFEMPLOYED_QSE_BIND_FLOW_SETTINGS={'fns_binding_polling_max_retries': 2},
)
@pytest.mark.parametrize('reschedule_count', (0, 2))
async def test_binding_incomplete(stq3_context, patch, stq, reschedule_count):
    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check(request_id: str):
        assert request_id == 'bind_request_id'
        return nalogru.nalogru_binding.BindingStatus.IN_PROGRESS, None

    await finish_qse_binding.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='task_id',
            exec_tries=0,
            reschedule_counter=reschedule_count,
            queue='selfemployed_fns_finish_qse_binding',
            eta=None,
        ),
        park_id='park_id',
        contractor_id='contractor_id',
        phone_pd_id='PHONE_PD_ID',
    )

    form_record = await stq3_context.pg.main_master.fetchrow(
        'SELECT * FROM se.quasi_profile_forms',
    )
    form_dict = dict(form_record)
    del form_dict['created_at']
    del form_dict['updated_at']
    assert form_dict == dict(
        park_id='park_id',
        contractor_profile_id='contractor_id',
        phone_pd_id='PHONE_PD_ID',
        inn_pd_id=None,
        is_phone_verified=True,
        sms_track_id=None,
        is_accepted=True,
        requested_at=None,
        increment=1,
    )

    assert not await stq3_context.pg.main_master.fetchrow(
        'SELECT * FROM se.finished_profiles',
    )
    assert not stq.selfemployed_fns_tag_contractor.has_calls

    assert stq.selfemployed_fns_finish_qse_binding.has_calls == (
        reschedule_count < 2
    )
