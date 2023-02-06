import pytest

from tests_qc_pools import utils


@pytest.mark.pgsql(
    'qc_pools', files=['simple_pass_insert.sql', 'simple_cursors_insert.sql'],
)
@pytest.mark.config(
    QC_POOLS_LOADER_SETTINGS={
        'enabled': True,
        'period_ms': 5000,
        'exams': ['dkvu'],
        'limit': 100,
    },
)
@pytest.mark.parametrize(
    'pass_id,pass_,code',
    [
        ('id1', [utils.make_pass('id1', 'dkvu', status='new')], 200),
        ('id1', [utils.make_pass('id1', 'dkvu', status='resolved')], 404),
        ('id2', [utils.make_pass('id2', 'dkvu', status='pending')], 200),
        (
            'id3',
            [
                utils.make_pass('id1', 'dkvu', status='resolved'),
                utils.make_pass('id2', 'dkvu', status='pending'),
                utils.make_pass('id3', 'dkvu', status='pending'),
            ],
            200,
        ),
        ('id2', [utils.make_pass('id2', 'dkvu', status='new')], 404),
    ],
)
async def test_task_sync(taxi_qc_pools, mockserver, pass_id, pass_, code):
    @mockserver.json_handler('/quality-control/api/v1/pass/list')
    def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return {
            'cursor': 'next',
            'items': pass_,
            'modified': '2020-07-19T08:53:03Z',
        }

    await taxi_qc_pools.run_periodic_task('qc_passes_loader')

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': pass_id},
    )
    assert response.status_code == code

    if code == 200:
        is_new = False
        for pass_item in pass_:
            if pass_item['id'] == pass_id and pass_item['status'] == 'NEW':
                is_new = True
                break

        if not is_new:
            assert response.json()['pass']['media'] == utils.make_media_list(
                pass_id,
            )


@pytest.mark.pgsql(
    'qc_pools', files=['simple_pass_insert.sql', 'simple_cursors_insert.sql'],
)
@pytest.mark.config(
    QC_POOLS_LOADER_SETTINGS={
        'enabled': True,
        'period_ms': 5000,
        'exams': ['dkvu'],
        'limit': 100,
    },
)
@pytest.mark.parametrize(
    'pass_id,pass_,code',
    [
        ('id2', [utils.make_pass('id2', 'dkvu', status='pending')], 200),
        (
            'id3',
            [
                utils.make_pass(
                    'id3', 'dkvu', status='pending', reason='regular',
                ),
            ],
            200,
        ),
        (
            'id4',
            [
                utils.make_pass(
                    'id4',
                    'dkvu',
                    status='pending',
                    reason='invite',
                    invite='hello',
                ),
            ],
            200,
        ),
        (
            'id5',
            [
                utils.make_pass(
                    'id5', 'dkvu', status='pending', parent='father',
                ),
            ],
            200,
        ),
        (
            'id6',
            [
                utils.make_pass(
                    'id6',
                    'dkvu',
                    status='pending',
                    reason='regular',
                    parent='mother',
                ),
            ],
            200,
        ),
        (
            'id7',
            [
                utils.make_pass(
                    'id7',
                    'dkvu',
                    status='pending',
                    reason='invite',
                    invite='hello',
                    parent='parent',
                ),
            ],
            200,
        ),
    ],
)
async def test_save_data_fields(
        pgsql, taxi_qc_pools, mockserver, pass_id, pass_, code,
):
    @mockserver.json_handler('/quality-control/api/v1/pass/list')
    def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return {
            'cursor': 'next',
            'items': pass_,
            'modified': '2020-07-19T08:53:03Z',
        }

    await taxi_qc_pools.run_periodic_task('qc_passes_loader')

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': pass_id},
    )
    assert response.status_code == code

    assert len(pass_) == 1  # test written for 1 pass
    necessary_fields = {'invite', 'reason_code', 'parent_pass'}
    necessary_data = {'lightbox', 'year', 'surname'}
    cursor = pgsql['qc_pools'].cursor()
    cursor.execute('SELECT key,json_value from qc_pools.meta')
    got_additional_data = {}
    got_data = {}
    for row in cursor:
        if row[0] in necessary_fields:
            got_additional_data[row[0]] = row[1]
        if row[0] in necessary_data:
            got_data[row[0]] = row[1]

    right_additional_data = utils.make_right_additional_field(pass_[0])
    right_data = utils.make_right_data(pass_[0])
    assert right_additional_data == got_additional_data
    assert right_data == got_data


@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.pgsql('qc_pools', files=['pass_expired_insert.sql'])
@pytest.mark.config(
    QC_POOLS_CLEANER_SETTINGS={
        'enabled': True,
        'period_ms': 5000,
        'limit': 100,
    },
)
async def test_delete_expired_passes(
        pgsql, taxi_qc_pools, mockserver, testpoint,
):
    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.json['status'] == 'FAIL'
        assert request.json['sanctions'] == ['sanction_no_resolution']
        assert request.json['identity']['script']['name'] == 'pool1'
        assert request.json['identity']['script']['id'] is not None
        return {}

    @testpoint('pools-cleaner::metrics_collected')
    def task_finished(data):
        return data

    await taxi_qc_pools.run_periodic_task('pools-cleaner')

    cursor = pgsql['qc_pools'].cursor()
    cursor.execute('SELECT * from qc_pools.pools')
    got_passes = set()
    for row in cursor:
        got_passes.add(row[2])
        if row[2] in {'id2', 'id4'}:
            assert row[1] == 'next_pool'

    assert got_passes == {'id2', 'id3', 'id4'}

    response = await task_finished.wait_call()
    assert response['data']['dkvu']['pool2']['expired'] == 2


@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.pgsql('qc_pools', files=['pass_expired_insert.sql'])
@pytest.mark.parametrize(
    'status,passes',
    [(400, {'id2', 'id3', 'id4'}), (500, {'id1', 'id2', 'id3', 'id4'})],
)
async def test_delete_expired_passes_with_resolve_error(
        pgsql, taxi_qc_pools, mockserver, testpoint, status, passes,
):
    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.json['status'] == 'FAIL'
        assert request.json['sanctions'] == ['sanction_no_resolution']
        assert request.json['identity']['script']['name'] == 'pool1'
        assert request.json['identity']['script']['id'] is not None
        return mockserver.make_response('Already resolved', status=status)

    await taxi_qc_pools.run_periodic_task('pools-cleaner')

    cursor = pgsql['qc_pools'].cursor()
    cursor.execute('SELECT * from qc_pools.pools')
    got_passes = set()
    for row in cursor:
        got_passes.add(row[2])
        if row[2] == 'id2':
            assert row[1] == 'next_pool'

    assert got_passes == passes


@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.pgsql(
    'qc_pools', files=['simple_pass_insert.sql', 'simple_cursors_insert.sql'],
)
@pytest.mark.config(
    QC_POOLS_LOADER_SETTINGS={
        'enabled': True,
        'period_ms': 5000,
        'exams': ['dkvu'],
        'limit': 100,
    },
)
@pytest.mark.parametrize(
    'pass_id,pass_,code',
    [('id4', [utils.make_pass('id4', 'dkvu', status='pending')], 200)],
)
async def test_task_one_pass_sync(
        taxi_qc_pools, mockserver, pass_id, pass_, code, load_json, testpoint,
):
    async def check_pass(pass_id, pool, status):
        response = await taxi_qc_pools.get(
            '/internal/qc-pools/v1/pass/info', params={'id': pass_id},
        )
        assert response.status_code == code
        assert response.json()['pool_states'][0]['pool'] == pool
        assert response.json()['pool_states'][0]['status'] == status

    @mockserver.json_handler('/quality-control/api/v1/pass/list')
    def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return {
            'cursor': 'next',
            'items': pass_,
            'modified': '2020-07-19T08:53:03Z',
        }

    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.args.get('pass_id') == pass_id
        assert request.json['status'] == 'SUCCESS'
        assert request.json['data'] == {'surname': 'surnameid4'}
        assert request.json['identity']['script']['name'] == 'init'
        assert request.json['identity']['script']['id'] is not None
        return {}

    await taxi_qc_pools.run_periodic_task('qc_passes_loader')
    await check_pass(pass_id, 'init', 'processed')

    await taxi_qc_pools.run_periodic_task('pools-executer')

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': pass_id},
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.pgsql(
    'qc_pools', files=['simple_pass_insert.sql', 'simple_cursors_insert.sql'],
)
@pytest.mark.config(
    QC_POOLS_LOADER_SETTINGS={
        'enabled': True,
        'period_ms': 5000,
        'exams': ['dkvu'],
        'limit': 100,
    },
)
@pytest.mark.parametrize(
    'pass_id,pass_,code',
    [('id5', [utils.make_pass('id5', 'dkvu', status='pending')], 200)],
)
async def test_task_data_pass_sync(
        taxi_qc_pools, mockserver, pass_id, pass_, code, load_json, testpoint,
):
    async def check_pass(pass_id, pool, status):
        response = await taxi_qc_pools.get(
            '/internal/qc-pools/v1/pass/info', params={'id': pass_id},
        )
        assert response.status_code == code
        assert response.json()['pool_states'][0]['pool'] == pool
        assert response.json()['pool_states'][0]['status'] == status

    @mockserver.json_handler('/quality-control/api/v1/pass/list')
    def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return {
            'cursor': 'next',
            'items': pass_,
            'modified': '2020-07-19T08:53:03Z',
        }

    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.args.get('pass_id') == pass_id
        assert request.json['status'] == 'SUCCESS'
        assert request.json['data'] == {
            'lightbox': True,
            'name': 'Иван',
            'surname': 'Ивановский',
        }
        assert request.json['identity']['script']['name'] == 'pool1'
        assert request.json['identity']['script']['id'] is not None
        return {}

    await taxi_qc_pools.run_periodic_task('qc_passes_loader')
    await check_pass(pass_id, 'init', 'processed')

    await taxi_qc_pools.run_periodic_task('pools-executer')
    await check_pass(pass_id, 'pool1', 'new')

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push.json'),
    )
    assert response.status_code == 200

    await check_pass(pass_id, 'pool1', 'processed')
    await taxi_qc_pools.run_periodic_task('pools-executer')

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': pass_id},
    )
    assert response.status_code == 404
