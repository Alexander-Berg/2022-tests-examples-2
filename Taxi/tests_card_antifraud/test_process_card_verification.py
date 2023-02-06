import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest


def update_verification(
        pgsql, yandex_uid, method, status, tries_left=None, version=0,
):
    tries_query = ''
    if tries_left is not None:
        tries_query = f'random_amount_tries_left = \'{tries_left}\', '
    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(
        (
            f'UPDATE card_antifraud.cards_verification '
            f'SET '
            f'status = \'{status}\', '
            + tries_query
            + f'method = \'{method}\', '
            + f'version = {version} '
            f'WHERE yandex_uid = \'{yandex_uid}\''
        ),
    )


def get_verifications(pgsql, yandex_uid, fields):
    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(
        (
            f'SELECT {fields} '
            f'FROM card_antifraud.cards_verification '
            f'WHERE yandex_uid = \'{yandex_uid}\''
        ),
    )
    columns = [it.name for it in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor]
    return rows


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'started_at,has_calls',
    [
        (datetime.datetime(2020, 2, 1, 13), True),
        (datetime.datetime(2020, 1, 30, 13), False),
    ],
)
async def test_reschedule(started_at, has_calls, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    task_id = '123'
    yandex_uid = '1234'
    verification_id = 'verification_1'
    card_id = 'x-123456'
    status = 'in_progress'
    method = 'standard2'

    args = [yandex_uid, verification_id, card_id, status, method, started_at]

    await stq_runner.process_card_verification.call(task_id=task_id, args=args)
    assert mock_stq_reschedule.has_calls == has_calls


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'method,db_status,request_status,expected_status',
    [
        ('standard1', 'in_progress', 'in_progress', 'in_progress'),
        ('standard2', 'in_progress', 'cvn_expected', 'cvn_expected'),
        ('standard2', 'cvn_expected', 'in_progress', 'cvn_expected'),
        ('standard2', 'cvn_expected', 'success', 'success'),
        ('standard1', 'failure', 'in_progress', 'failure'),
        (
            'standard2_3ds',
            '3ds_required',
            '3ds_status_received',
            '3ds_status_received',
        ),
        ('standard2_3ds', 'failure', '3ds_status_received', 'failure'),
        ('standard2_3ds', '3ds_required', 'success', 'success'),
        ('random_amt', 'in_progress', 'amount_expected', 'amount_expected'),
        ('random_amt', 'amount_expected', 'in_progress', 'amount_expected'),
        ('random_amt', 'amount_expected', 'success', 'success'),
        ('standard2', 'in_progress', 'cvn_expected', 'cvn_expected'),
        ('standard2', 'in_progress', '3ds_required', '3ds_required'),
        ('standard2', 'in_progress', 'amount_expected', 'amount_expected'),
        ('standard2', 'amount_expected', 'in_progress', 'amount_expected'),
        (
            'random_amt',
            'cvn_expected',
            '3ds_status_received',
            '3ds_status_received',
        ),
        ('standard2', 'in_progress', 'failure', 'failure'),
    ],
)
async def test_status_compare_success(
        method,
        db_status,
        request_status,
        expected_status,
        stq_runner,
        pgsql,
        taxi_card_antifraud_monitor,
):
    yandex_uid = '1234'
    version_before = 1

    #
    update_verification(
        pgsql, yandex_uid, method, db_status, version=version_before,
    )

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = request_status
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]

    async with metrics_helpers.MetricsCollector(
            taxi_card_antifraud_monitor, sensor='verification_finish',
    ) as collector:
        await stq_runner.process_card_verification.call(
            task_id=task_id, args=args,
        )

    result_verifications = get_verifications(
        pgsql, yandex_uid, 'method,status,version',
    )

    assert len(result_verifications) == 1
    assert result_verifications[0]['method'] == method
    assert result_verifications[0]['status'] == expected_status

    if db_status != expected_status:
        assert result_verifications[0]['version'] > version_before

    if request_status in ('success', 'failure'):
        metric = collector.get_single_collected_metric()
        assert metric.labels['status'] == expected_status
        assert metric.value == 1


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'db_tries_left,request_tries_left,expected_tries_left',
    [(3, 3, 3), (2, 3, 2), (3, 1, 1)],
)
async def test_status_compare_tries_left(
        db_tries_left,
        request_tries_left,
        expected_tries_left,
        stq_runner,
        pgsql,
):
    yandex_uid = '1234'

    update_verification(
        pgsql, yandex_uid, 'random_amt', 'amount_expected', db_tries_left,
    )

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = 'amount_expected'
    method = 'random_amt'
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]
    kwargs = {'random_amount_tries_left': request_tries_left}

    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, kwargs=kwargs,
    )
    result_verifications = get_verifications(
        pgsql, yandex_uid, 'random_amount_tries_left',
    )
    assert len(result_verifications) == 1
    tries_left = result_verifications[0]['random_amount_tries_left']
    assert tries_left == expected_tries_left


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'db_method,request_method,db_status,request_status,db_tries,request_tries',
    [
        ('standard2', 'standard1', 'in_progress', 'cvn_expected', None, None),
        ('unknown', 'random_amt', 'amount_expected', 'amount_expected', 3, 2),
    ],
)
async def test_different_methods_success(
        db_method,
        request_method,
        db_status,
        request_status,
        db_tries,
        request_tries,
        pgsql,
        stq_runner,
):
    yandex_uid = '1234'

    update_verification(pgsql, yandex_uid, db_method, db_status, db_tries)

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = request_status
    method = request_method
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]
    kwargs = {}
    if request_tries is not None:
        kwargs['random_amount_tries_left'] = request_tries

    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, kwargs=kwargs,
    )

    result_verifications = get_verifications(
        pgsql, yandex_uid, 'method,status,random_amount_tries_left',
    )
    assert len(result_verifications) == 1

    method = result_verifications[0]['method']
    assert method == request_method
    status = result_verifications[0]['status']
    assert status == request_status
    if request_tries:
        tries_left = result_verifications[0]['random_amount_tries_left']
        assert tries_left == request_tries


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'db_method,request_method,db_status,request_status,db_tries,request_tries',
    [
        (
            'random_amt',
            'random_amt',
            'amount_expected',
            'amount_expected',
            None,
            None,
        ),
        (
            'random_amt',
            'random_amt',
            'amount_expected',
            'amount_expected',
            None,
            3,
        ),
        (
            'random_amt',
            'random_amt',
            'amount_expected',
            'amount_expected',
            3,
            None,
        ),
        ('random_amt', 'unknown', 'amount_expected', 'amount_expected', 3, 1),
    ],
)
async def test_status_compare_failure(
        db_method,
        request_method,
        db_status,
        request_status,
        db_tries,
        request_tries,
        pgsql,
        stq_runner,
):
    yandex_uid = '1234'

    update_verification(pgsql, yandex_uid, db_method, db_status, db_tries)

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = request_status
    method = request_method
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]
    kwargs = {}
    if request_tries is not None:
        kwargs['random_amount_tries_left'] = request_tries

    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, kwargs=kwargs, expect_fail=True,
    )


@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_unknown_status(stq_runner):
    task_id = '123'
    verification_id = 'temp_id1'
    yandex_uid = '1234'
    card_id = 'card-x1234567'
    status = 'in_progress'
    method = 'unknown'
    started_at = datetime.datetime(2020, 2, 1, 13)
    args = [yandex_uid, verification_id, card_id, status, method, started_at]
    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, expect_fail=True,
    )


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize('db_status', ['in_progress', 'success'])
async def test_success_save_card(
        db_status, pgsql, stq_runner, stq, taxi_card_antifraud_monitor,
):
    yandex_uid = '1234'
    method = 'standard2'

    update_verification(pgsql, yandex_uid, method, db_status)

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = 'success'
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]

    async with metrics_helpers.MetricsCollector(
            taxi_card_antifraud_monitor,
            sensor='verification_finish',
            labels={'status': 'success'},
    ) as collector:
        await stq_runner.process_card_verification.call(
            task_id=task_id, args=args,
        )

    save_call = stq.save_verified_card.next_call()

    assert save_call['id'] == yandex_uid + card_id + 'test_id'

    kwargs = save_call['kwargs']
    kwargs.pop('log_extra')

    assert kwargs == {
        'user_uid': yandex_uid,
        'card_id': card_id,
        'device_id': 'test_id',
    }

    assert collector.get_single_collected_metric().value == 1


@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_status_write_conflict(
        pgsql, stq_runner, stq, testpoint, mockserver,
):
    @testpoint('process_card_verification')
    def _testpoint(data):
        update_verification(
            pgsql, '1234', 'standard2', 'cvn_required', version=1,
        )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    yandex_uid = '1234'
    db_status = 'in_progress'
    method = 'standard2'

    update_verification(pgsql, yandex_uid, method, db_status)

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = 'success'
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]

    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, expect_fail=False,
    )
    assert mock_stq_reschedule.has_calls is True


@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_tries_left_write_conflict(
        pgsql, stq_runner, stq, testpoint, mockserver,
):
    @testpoint('process_card_verification')
    def _testpoint(data):
        update_verification(
            pgsql, '1234', 'random_amt', 'amount_expected', 1, version=1,
        )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    yandex_uid = '1234'
    db_status = 'amount_expected'
    method = 'random_amt'
    db_tries_left = 3

    update_verification(pgsql, yandex_uid, method, db_status, db_tries_left)

    task_id = '123'
    verification_id = 'temp_id1'
    card_id = 'card-x1234567'
    status = 'amount_expected'
    tries_left = 2
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]
    kwargs = {'random_amount_tries_left': tries_left}

    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, kwargs=kwargs, expect_fail=False,
    )
    assert mock_stq_reschedule.has_calls is True


@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_update_duplicates(pgsql, stq_runner):
    task_id = '123'
    yandex_uid = '1235'
    verification_id = 'purchase_1235'
    card_id = 'card-x1235'
    status = 'success'
    method = 'standard2_3ds'
    started_at = datetime.datetime(2020, 2, 1, 13)

    args = [yandex_uid, verification_id, card_id, status, method, started_at]

    await stq_runner.process_card_verification.call(
        task_id=task_id, args=args, expect_fail=False,
    )

    result_verifications = get_verifications(
        pgsql, yandex_uid, 'method,status,version',
    )

    assert len(result_verifications) == 3
    for i in result_verifications:
        assert i['status'] == 'success'
