import mock

from dmp_suite.maintenance.sla_updater import task


PREFIX = 'dmp_suite.maintenance.sla_updater.task'


def full_path(name, prefix=PREFIX):
    return f'{prefix}.{name}'


def apply_standard_mocks(func):
    @mock.patch(full_path('settings'))
    @mock.patch(full_path('get_pgaas_connection'))
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def apply_mocks_above_ignore_args(func):
    def wrapper(*args, **kwargs):
        return func()
    return wrapper


def apply_mocks_above_reverse_args(func):
    def wrapper(*args, **kwargs):
        return func(*reversed(args), **kwargs)
    return wrapper


@apply_standard_mocks
@mock.patch(full_path('__version__'), '1.1.1')
@mock.patch(full_path('get_consensus'), return_value=None)
@mock.patch(full_path('get_ctl'))
@apply_mocks_above_ignore_args
@mock.patch(full_path('logger'))
def test_no_consensus(logger):
    """
    Проверяем, что в случае отсутствия консенсусса будет выведено сообщение в логи
    """

    task._update_sla('mock_etl')

    logger.info.assert_has_calls([
        mock.call('Live hosts have no consensus')
    ])


@apply_standard_mocks
@mock.patch(full_path('__version__'), '1.1.1')
@mock.patch(full_path('get_consensus'), return_value='1.1.1')
@apply_mocks_above_ignore_args
@mock.patch(full_path('get_ctl'))
@mock.patch(full_path('logger'))
@apply_mocks_above_reverse_args
def test_already_updated(get_ctl, logger):
    """
    Проверяем, что если табличка с sla уже была обновлена,
    то будет выведено сообщение в логи
    """
    service = mock.Mock()
    service.get_code_version = lambda _: '1.1.1'

    ctl = mock.Mock()
    ctl.service = service

    get_ctl.return_value = ctl

    task._update_sla('mock_etl')

    logger.info.assert_has_calls([
        mock.call('Sla table has already been updated')
    ])


@apply_standard_mocks
@mock.patch(full_path('__version__'), '1.1.0')
@mock.patch(full_path('get_consensus'), return_value='1.1.1')
@apply_mocks_above_ignore_args
@mock.patch(full_path('get_ctl'))
@mock.patch(full_path('logger'))
@apply_mocks_above_reverse_args
def test_consensus_does_not_match_host_version(get_ctl, logger):
    """
    Еще бывают ситуации, когда версия кода для сервиса, который запускает код не совпадает с консенсусом
    """
    service = mock.Mock()
    service.get_code_version = lambda _: '1.1.2'

    ctl = mock.Mock()
    ctl.service = service

    get_ctl.return_value = ctl

    task._update_sla('mock_etl')

    logger.warning.assert_has_calls([
        mock.call('Consensus does not match host version')
    ])
