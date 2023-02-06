# pylint: disable=invalid-name,unused-variable

import datetime as dt

import pytest

from testsuite.utils import http

from selfemployed.db import dbmain
from selfemployed.db import dbreceipts
from . import conftest

EPSILON_TIMEDELTA_SEC = 10


@pytest.mark.pgsql(
    'selfemployed_orders@0',
    queries=[
        """
        INSERT INTO receipts
            (id, park_id, driver_id, receipt_type, inn, status, total,
             fns_url, is_corp,
             receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz,
             created_at, modified_at)
        VALUES
            ('ay1', 'ay1', 'ay1', 'order', '111', 'new', 100.0,
            'http://bla-bla', false, NOW(), NOW(), NOW(), NOW(), NOW(), NOW())
        """,
    ],
)
async def test_get_receipt_url_ok(se_client):
    response = await se_client.get(
        '/get-receipt-image', params={'park_id': 'ay1', 'order_id': 'ay1'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'receipt_url': 'http://bla-bla'}


async def test_get_receipt_url_404(se_client):
    response = await se_client.get(
        '/get-receipt-image', params={'park_id': 'ay2', 'order_id': 'ay2'},
    )

    assert response.status == 404


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, step, driver_id, park_id,
             created_at, modified_at,
             bik, account_number)
        VALUES
            ('ax12', 'requisites', 'ax12', 'ax12',
             now()::timestamp, now()::timestamp,
             '1', '1')
        """,
    ],
)
async def test_get_selfemployed_status_present(se_client):
    response = await se_client.get(
        '/selfemployed-status',
        params={'park_id': 'ax12', 'driver_id': 'ax12'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'requisites_missing': False}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.finished_ownpark_profile_metadata
            (created_park_id, created_contractor_id, phone_pd_id,
             initial_park_id, initial_contractor_id,
             salesforce_account_id, salesforce_requisites_case_id,
             external_id)
        VALUES
            ('cp1', 'cc1', 'phone',
             'ip1', 'ic1',
             'sf_acc', 'sf_case',
             '1')
        """,
    ],
)
async def test_get_selfemployed_v2_status_present(se_client):
    response = await se_client.get(
        '/selfemployed-status', params={'park_id': 'cp1', 'driver_id': 'cc1'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'requisites_missing': False}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.finished_ownpark_profile_metadata
            (created_park_id, created_contractor_id, phone_pd_id,
             initial_park_id, initial_contractor_id,
             salesforce_account_id, salesforce_requisites_case_id,
             external_id)
        VALUES
            ('cp1', 'cc1', 'phone',
             'ip1', 'ic1',
             'sf_acc', NULL,
             '1')
        """,
    ],
)
async def test_get_selfemployed_v2_status_present_account(
        mock_salesforce, se_client,
):
    @mock_salesforce('/services/data/v46.0/sobjects/Account/sf_acc')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Type,City__c,IBAN__c,SWIFT__c'}
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': '00000000000000000000',
            'SWIFT__c': '000000000',
        }

    response = await se_client.get(
        '/selfemployed-status', params={'park_id': 'cp1', 'driver_id': 'cc1'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'requisites_missing': False}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.finished_ownpark_profile_metadata
            (created_park_id, created_contractor_id, phone_pd_id,
             initial_park_id, initial_contractor_id,
             salesforce_account_id, salesforce_requisites_case_id,
             external_id)
        VALUES
            ('cp1', 'cc1', 'phone',
             'ip1', 'ic1',
             'sf_acc', NULL,
             '1')
        """,
    ],
)
async def test_get_selfemployed_v2_status_missing(mock_salesforce, se_client):
    @mock_salesforce('/services/data/v46.0/sobjects/Account/sf_acc')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Type,City__c,IBAN__c,SWIFT__c'}
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': None,
            'SWIFT__c': None,
        }

    response = await se_client.get(
        '/selfemployed-status', params={'park_id': 'cp1', 'driver_id': 'cc1'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'requisites_missing': True}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, step, driver_id, park_id, bik, account_number, created_at,
            modified_at)
        VALUES
            ('ax11-1', 'requisites', 'ax11-1', 'ax11-1', NULL, NULL,
             now()::timestamp, now()::timestamp),
            ('ax11-2', 'permission', 'ax11-2', 'ax11-2', 'bik', 'acc/n',
             now()::timestamp, now()::timestamp)
        """,
    ],
)
@pytest.mark.parametrize(
    'park_id, driver_id', [('ax11-1', 'ax11-1'), ('ax11-2', 'ax11-2')],
)
async def test_get_selfemployed_status_missing(se_client, park_id, driver_id):
    response = await se_client.get(
        '/selfemployed-status',
        params={'park_id': park_id, 'driver_id': driver_id},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'requisites_missing': True}


async def test_get_selfemployed_status_404(se_client):
    response = await se_client.get(
        '/selfemployed-status',
        params={'park_id': 'ax13', 'driver_id': 'ax13'},
    )

    assert response.status == 404


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id,
             created_at, modified_at)
        VALUES
            ('selfemployed_id1', 'oldpark15', 'olddriver15',
             now()::timestamp, now()::timestamp),
            ('selfemployed_selfreg_id1', 'selfreg', 'selfregid1',
             now()::timestamp, now()::timestamp)
        """,
    ],
)
@pytest.mark.parametrize(
    'selfemployed_id, old_park_id, old_driver_id, selfreg_error',
    [
        ('selfemployed_id1', 'oldpark15', 'olddriver15', None),
        ('selfemployed_selfreg_id1', 'selfreg', 'selfregid1', None),
        ('selfemployed_selfreg_id1', 'selfreg', 'selfregid1', 404),
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_new_park_callback(
        se_web_context,
        se_client,
        mockserver,
        mock_selfreg,
        mock_tags,
        mock_client_notify,
        selfemployed_id,
        old_park_id,
        old_driver_id,
        selfreg_error,
        stq,
):
    park_id = 'newpark15'
    driver_id = 'newdriver15'

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': f'{old_park_id}-{old_driver_id}',
            'notification': {'text': 'Парк создан'},
        }
        return {'notification_id': 'notification_id'}

    @mock_selfreg('/internal/selfreg/v1/new-contractor-callback')
    async def _selfreg_callback(request):
        assert request.method == 'POST'
        body = request.json
        assert body == {
            'selfreg_id': 'selfregid1',
            'park_id': park_id,
            'driver_profile_id': driver_id,
            'source': 'selfemployed',
        }
        if selfreg_error:
            return mockserver.make_response(status=selfreg_error)
        return {}

    response = await se_client.post(
        '/new-park-callback',
        json={
            'selfemployed_id': selfemployed_id,
            'driver_id': driver_id,
            'park_id': park_id,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'status': 'ok'}

    entry = await dbmain.get_from_driver(
        se_web_context.pg, old_park_id, old_driver_id,
    )

    assert entry['park_id'] == park_id
    assert entry['driver_id'] == driver_id
    assert stq.selfemployed_fns_tag_contractor.next_call()['kwargs'] == {
        'trigger_id': 'ownpark_profile_created',
        'park_id': park_id,
        'contractor_id': driver_id,
    }
    if selfemployed_id == 'selfemployed_selfreg_id1':
        assert _selfreg_callback.times_called == 1
        assert _send_message.times_called == 0
    else:
        assert _selfreg_callback.times_called == 0
        assert _send_message.times_called == 1


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status)
        VALUES
            ('PARK_PHONE_PD_ID', 'INN_PD_ID_1', 'COMPLETED'),
            ('SELFREG_PHONE_PD_ID', 'INN_PD_ID_2', 'COMPLETED');
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('parkid', 'contractorid', 'PARK_PHONE_PD_ID'),
            ('selfreg', 'selfregid', 'SELFREG_PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code, agreements,
             inn_pd_id, residency_state,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id)
         VALUES
            ('PARK_PHONE_PD_ID', 'FILLED', 'park_se',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}',
             'INN_PD_ID_1', 'RESIDENT',
             'salesforce_account_id_1', NULL,
             'parkid', 'contractorid'),
            ('SELFREG_PHONE_PD_ID', 'FILLED', 'selfreg_se',
             'address', '321', '7654321',
             '{"general": true, "gas_stations": true}',
             'INN_PD_ID_2', 'RESIDENT',
             'salesforce_account_id_2', NULL,
             'selfreg', 'selfregid');
        """,
    ],
)
@pytest.mark.parametrize(
    'selfemployed_id, old_park_id, old_driver_id, selfreg_error',
    [
        ('park_se', 'oldparkid', 'oldcontractorid', None),
        ('selfreg_se', 'selfreg', 'selfregid', None),
        ('selfreg_se', 'selfreg', 'selfregid', 404),
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_new_park_callback_new_style(
        se_web_context,
        se_client,
        mockserver,
        mock_selfreg,
        mock_tags,
        mock_fleet_synchronizer,
        selfemployed_id,
        old_park_id,
        old_driver_id,
        selfreg_error,
        stq,
):
    park_id = 'newparkid'
    contractor_id = 'newcontractorid'

    @mock_fleet_synchronizer('/v1/mapping/driver')
    def _mapping_driver(request):
        return {'mapping': []}

    @mock_selfreg('/internal/selfreg/v1/new-contractor-callback')
    async def _selfreg_callback(request):
        assert request.method == 'POST'
        body = request.json
        assert body == {
            'selfreg_id': 'selfregid',
            'park_id': park_id,
            'driver_profile_id': contractor_id,
            'source': 'selfemployed',
        }
        if selfreg_error:
            return mockserver.make_response(status=selfreg_error)
        return {}

    response = await se_client.post(
        '/new-park-callback',
        json={
            'selfemployed_id': selfemployed_id,
            'driver_id': contractor_id,
            'park_id': park_id,
        },
    )

    profile = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.finished_profiles '
        'WHERE park_id = $1 and contractor_profile_id = $2',
        park_id,
        contractor_id,
    )

    metadata = await se_web_context.pg.main_master.fetchrow(
        'SELECT * FROM se.finished_ownpark_profile_metadata '
        'WHERE created_park_id = $1 and created_contractor_id = $2',
        park_id,
        contractor_id,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'status': 'ok'}

    assert profile['park_id'] == park_id
    assert profile['contractor_profile_id'] == contractor_id
    assert profile['is_own_park']
    assert metadata

    assert stq.selfemployed_fns_tag_contractor.next_call()['kwargs'] == {
        'trigger_id': 'ownpark_profile_created',
        'park_id': park_id,
        'contractor_id': contractor_id,
    }
    assert _selfreg_callback.times_called == (old_park_id == 'selfreg')


@pytest.mark.config(
    SELFEMPLOYED_NONRESIDENT_SETTINGS={
        'is_enabled': True,
        'eligible_banks': [{'bik': '044525974'}],
        'account_prefix': '40820',
        'disabled_tag_name': 'nonresident_temporary_blocked',
        'use_stq': False,
    },
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, bik, account_number,
             created_at, modified_at)
        VALUES
            ('aaa15', 'oldpark15', 'olddriver15',
            '044525974', '40817810000000375671',
             now()::timestamp, now()::timestamp),
            ('aaa16', 'oldpark16', 'olddriver16',
            '044525974', '40820810000000375671',
             now()::timestamp, now()::timestamp)
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    ('selfemployed_id', 'park_id', 'driver_id', 'expected_triggers'),
    [
        (
            'aaa15',
            'newaaa15park',
            'newaaa15driver',
            ['ownpark_profile_created'],
        ),
        (
            'aaa16',
            'newaaa16park',
            'newaaa16driver',
            ['ownpark_profile_created', 'ownpark_requisites_set_nonresident'],
        ),
    ],
)
async def test_new_park_callback_nonresident(
        se_web_context,
        se_client,
        mock_client_notify,
        mock_tags,
        selfemployed_id,
        park_id,
        driver_id,
        expected_triggers,
        stq,
):
    @mock_client_notify('/v2/push')
    async def _send_message(request):
        return {'notification_id': 'notification_id'}

    response = await se_client.post(
        '/new-park-callback',
        json={
            'selfemployed_id': selfemployed_id,
            'driver_id': driver_id,
            'park_id': park_id,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'status': 'ok'}

    triggers = set()
    while stq.selfemployed_fns_tag_contractor.has_calls:
        kwargs = stq.selfemployed_fns_tag_contractor.next_call()['kwargs']
        assert len(kwargs) == 3
        assert kwargs['park_id'] == park_id
        assert kwargs['contractor_id'] == driver_id
        triggers.add(kwargs['trigger_id'])
    assert set(expected_triggers) == triggers


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=["""DELETE FROM profiles WHERE id = 'aaa15'"""],
)
async def test_new_park_callback_error(se_client):
    response = await se_client.post(
        '/new-park-callback',
        json={
            'selfemployed_id': 'aaa15',
            'driver_id': 'aaaaa',
            'park_id': 'bbbbb',
        },
    )
    assert response.status == 400


async def test_requisites_callback(se_client):
    response = await se_client.post(
        '/requisites-callback',
        json={'data': 'data', 'driver_id': 'aaaaa', 'park_id': 'bbbbb'},
    )
    assert response.status == 200


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, park_id, driver_id, inn,
            created_at, modified_at)
        VALUES
            ('si1', 'd1', 'p1', 'psi1', 'dsi1', '512345123',
            now()::timestamp, now()::timestamp)
        """,
    ],
)
async def test_selfemployed_info_200(se_client):
    response = await se_client.get(
        '/selfemployed-info', params={'park_id': 'psi1', 'driver_id': 'dsi1'},
    )
    content = await response.json()

    assert response.status == 200
    assert content
    assert content['inn'] == '512345123'


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, park_id, driver_id, inn,
            created_at, modified_at)
        VALUES
            ('si1', 'd1', 'p1', 'psi1', 'dsi1', '512345123',
            now()::timestamp, now()::timestamp)
        """,
    ],
)
async def test_selfemployed_info_400(se_client):
    response = await se_client.get(
        '/selfemployed-info', params={'park_id': 'psi1'},
    )
    assert response.status == 400


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, park_id, driver_id, inn,
            created_at, modified_at)
        VALUES
            ('si1', 'd1', 'p1', 'xxx1', 'yyy1', '512345123',
            now()::timestamp, now()::timestamp)
        """,
    ],
)
async def test_selfemployed_info_404(se_client):
    response = await se_client.get(
        '/selfemployed-info', params={'park_id': 'psi1', 'driver_id': 'dsi1'},
    )
    assert response.status == 404


@pytest.mark.config(
    SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION=(
        conftest.SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION
    ),
)
@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
async def test_correct_subvention(se_client, se_web_context):
    json_body = {
        'driver_id': 'd1',
        'park_id': 'p1',
        'reverse_subvention_id': 'rs1',
        'new_subvention_id': 's2',
        'total': 100.5,
        'receipt_date': '2018-12-29T17:29:30.742701Z',
        'checkout_date': '2018-12-29T17:29:30.742701Z',
    }

    response = await se_client.post('/correct-subvention/v2', json=json_body)
    assert response.status == 200

    pg = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg, 'p1')
    correction = await dbreceipts.get_correction(pg, shard, 'rs1')

    assert correction['reverse_id'] == 'rs1'
    assert correction['new_id'] == 's2'
    assert correction['total'] == 100.5
    assert str(correction['receipt_at']) == '2018-12-29 17:29:30.742701'
    assert str(correction['checkout_at']) == '2018-12-29 17:29:30.742701'
    assert correction['status'] == 'new'

    # Here dt.datetime.now() is smaller than db's timestamp
    # because time freezes during the test. This affects
    # dt.datetime.now() but doesn't affect db's now()::timestamp.
    assert (
        correction['created_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC
    assert (
        correction['modified_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC


@pytest.mark.config(
    SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION=(
        conftest.SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION
    ),
)
@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
async def test_cancel_subvention(se_client, se_web_context):
    json_body = {
        'driver_id': 'd1',
        'park_id': 'p1',
        'reverse_subvention_id': 'rs1',
        'total': 0,
        'receipt_date': '2018-12-29T17:29:30.742701Z',
        'checkout_date': '2018-12-29T17:29:30.742701Z',
    }

    response = await se_client.post('/correct-subvention/v2', json=json_body)
    assert response.status == 200

    pg = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg, 'p1')
    correction = await dbreceipts.get_correction(pg, shard, 'rs1')

    assert correction['reverse_id'] == 'rs1'
    assert correction['new_id'] is None
    assert correction['total'] == 0
    assert str(correction['receipt_at']) == '2018-12-29 17:29:30.742701'
    assert str(correction['checkout_at']) == '2018-12-29 17:29:30.742701'
    assert correction['status'] == 'new'

    # Here dt.datetime.now() is smaller than db's timestamp
    # because time freezes during the test. This affects
    # dt.datetime.now() but doesn't affect db's now()::timestamp.
    assert (
        correction['created_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC
    assert (
        correction['modified_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC


@pytest.mark.config(
    SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION=(
        conftest.SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION
    ),
)
@pytest.mark.client_experiments3(
    consumer='selfemployed/fns-se/billing-events',
    experiment_name='pro_fns_selfemployment_use_billing_events',
    args=[{'name': 'park_id', 'type': 'string', 'value': 'p1'}],
    value={'use_old_style': False},
)
@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
async def test_correct_subvention_moved_to_stq(se_client, se_web_context):
    json_body = {
        'driver_id': 'd1',
        'park_id': 'p1',
        'reverse_subvention_id': 'rs1',
        'total': 0,
        'receipt_date': '2018-12-29T17:29:30.742701Z',
        'checkout_date': '2018-12-29T17:29:30.742701Z',
    }

    response = await se_client.post('/correct-subvention/v2', json=json_body)
    assert response.status == 200

    pg = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg, 'p1')
    with pytest.raises(dbreceipts.CorrectionNotFoundError):
        await dbreceipts.get_correction(pg, shard, 'rs1')


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
                (id, from_driver_id,
                from_park_id, step, created_at, modified_at)
        VALUES
                ('aaa15', 'ddd15', 'ppp15', 'intro',
                now()::timestamp, now()::timestamp)
        """,
    ],
)
async def test_block_updates(se_client):
    response = await se_client.post(
        '/block-updates', json={'from': '2019-01-01 00:00:00'},
    )

    content = await response.json()
    assert content == {'blocked': [], 'unblocked': []}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, park_id, driver_id,
            created_at, modified_at)
        VALUES
            ('1', 'ip1', 'id1', 'cp1', 'cd1', now(), now()),
            ('2', 'ip2', 'id2', 'cp2', 'cd2', now(), now()),
            ('3', 'selfreg', 'id3', 'cp3', 'cd3', now(), now());
        INSERT INTO se.finished_ownpark_profile_metadata
            (initial_park_id, initial_contractor_id,
             created_park_id, created_contractor_id,
             phone_pd_id, salesforce_account_id, external_id)
        VALUES
            ('ip2', 'id2', 'cp2', 'cd2', 'ph2', 'sf2', '2'),
            ('ip4', 'id4', 'cp4', 'cd4', 'ph4', 'sf4', '4'),
            ('selfreg', 'id5', 'cp5', 'cd5', 'ph5', 'sf5', '5');
        """,
    ],
)
@pytest.mark.parametrize(
    'park_id,expected_code,expected_response',
    [
        ('cp1', 200, {'old_park_id': 'ip1', 'old_driver_id': 'id1'}),
        ('cp2', 200, {'old_park_id': 'ip2', 'old_driver_id': 'id2'}),
        ('cp3', 404, None),
        ('cp4', 200, {'old_park_id': 'ip4', 'old_driver_id': 'id4'}),
        ('cp5', 404, None),
        ('cp6', 404, None),
    ],
)
async def test_get_profile_details(
        se_client, park_id, expected_code, expected_response,
):
    response = await se_client.get(
        '/get-profile-details', params={'park_id': park_id},
    )

    assert response.status == expected_code
    if expected_response:
        assert (await response.json()) == expected_response


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, park_id, driver_id, salesforce_account_id,
             created_at, modified_at)
        VALUES ('se_id1', 'parkid1', 'driverid1', 'sf_id', now(), now()),
               ('se_id2', 'parkid2', 'driverid2', NULL, now(), now());
        """,
    ],
)
@pytest.mark.parametrize(
    'park,driver,status,response_json',
    [
        ('parkid1', 'driverid1', 200, {'salesforce_account_id': 'sf_id'}),
        ('parkid2', 'driverid2', 200, {}),
        ('parkid3', 'driverid3', 404, None),
    ],
)
async def test_get_salesforce_account_id(
        se_client, park, driver, status, response_json,
):
    response = await se_client.get(
        '/service/salesforce-account-id',
        params={'park_id': park, 'driver_id': driver},
    )

    assert response.status == status
    if response_json is not None:
        assert (await response.json()) == response_json
