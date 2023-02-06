import pytest


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('qc_pools', files=['pass_expired_insert.sql'])
async def test_happy_path(
        pgsql, taxi_qc_pools, mockserver, testpoint, load_json,
):
    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.json['status'] == 'FAIL'
        assert request.json['sanctions'] == ['sanction1']
        assert request.json['reason'] == {'keys': ['sanction1', 'reason']}
        return {}

    def _check_sanctions(sanctions):
        cursor = pgsql['qc_pools'].cursor()
        cursor.execute('SELECT pass_id,key,value from qc_pools.meta')
        result = cursor.fetchone()
        assert result is not None
        assert result[1] == 'sanctions'
        assert result[2] == sanctions

    async def _push_pool(pool):
        await taxi_qc_pools.post(
            '/internal/qc-pools/v1/pool/push',
            params={'pool': pool},
            json=load_json('id1_push.json'),
        )

    # set sanctions from array of strings
    await taxi_qc_pools.run_periodic_task('pools-cleaner')

    _check_sanctions('["sanction1","sanction2"]')

    await _push_pool('pool2')
    # add sanctions from array of strings
    await taxi_qc_pools.run_periodic_task('pools-executer')

    _check_sanctions('["sanction1","sanction2","sanction3"]')

    await _push_pool('pool3')
    # delete sanctions from array of strings
    await taxi_qc_pools.run_periodic_task('pools-executer')
    _check_sanctions('["sanction1"]')

    await _push_pool('pool4')
    await taxi_qc_pools.run_periodic_task('pools-executer')


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('qc_pools', files=['simple_pass_insert.sql'])
async def test_empty_add_path(
        pgsql, taxi_qc_pools, mockserver, testpoint, load_json,
):
    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.json['status'] == 'FAIL'
        assert 'sanctions' not in request.json
        return {}

    def _check_sanctions(sanctions):
        cursor = pgsql['qc_pools'].cursor()
        cursor.execute('SELECT pass_id,key,value from qc_pools.meta')
        result = cursor.fetchone()
        assert result is not None
        assert result[1] == 'sanctions'
        assert result[2] == sanctions

    async def _push_pool(pool):
        await taxi_qc_pools.post(
            '/internal/qc-pools/v1/pool/push',
            params={'pool': pool},
            json=load_json('id1_push.json'),
        )

    # add sanctions from array of strings
    await taxi_qc_pools.run_periodic_task('pools-cleaner')

    _check_sanctions('["sanction2","sanction3"]')

    await _push_pool('pool3')
    # delete sanctions from array of strings
    await taxi_qc_pools.run_periodic_task('pools-executer')
    _check_sanctions('[]')

    await _push_pool('pool4')
    await taxi_qc_pools.run_periodic_task('pools-executer')


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('qc_pools', files=['sanctions_pass_insert.sql'])
async def test_empty_remove_path(
        pgsql, taxi_qc_pools, mockserver, testpoint, load_json,
):
    @mockserver.json_handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        assert request.method == 'POST'
        assert request.json['status'] == 'FAIL'
        assert 'sanctions' not in request.json
        return {}

    def _check_sanctions(key, sanctions):
        cursor = pgsql['qc_pools'].cursor()
        cursor.execute('SELECT pass_id,key,value from qc_pools.meta')
        result = cursor.fetchone()
        assert result is not None
        assert result[1] == key
        assert result[2] == sanctions

    async def _push_pool(pool):
        await taxi_qc_pools.post(
            '/internal/qc-pools/v1/pool/push',
            params={'pool': pool},
            json=load_json('id1_push.json'),
        )

    # check sanctions from array of strings
    _check_sanctions('pool1.sanctions', '["sanction1"]')

    await _push_pool('pool3')
    # delete sanctions from array of strings
    await taxi_qc_pools.run_periodic_task('pools-cleaner')
    _check_sanctions('pool1.sanctions', '["sanction1"]')

    await _push_pool('pool4')
    await taxi_qc_pools.run_periodic_task('pools-executer')
