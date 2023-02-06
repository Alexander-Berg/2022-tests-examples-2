import pytest

from quality_control.generated.cron import run_cron
from test_quality_control.validate_vaccination_certificate import utils


@pytest.fixture
def gosu(mockserver):
    class GosuContext:
        def __init__(self):
            self.should_fail = False
            self.masked_initials = None

        def set_should_fail(self, should_fail):
            self.should_fail = should_fail

        def set_masked_initials(self, masked_initials):
            self.masked_initials = masked_initials

        def gosu_response(self):
            if self.masked_initials is None:
                return mockserver.make_response(status=204)

            return {
                'fio': self.masked_initials,
                'doc': 'doc',
                'birthdate': '01.01.2000',
                'en': False,
                'enFio': 'enFio',
                'enDoc': 'enDoc',
            }

    context = GosuContext()

    @mockserver.json_handler(
        '/covid-proxy/gosuslugi/a123b456-c789-d987-e654-f321g123h456',
    )
    async def validate(request):
        if context.should_fail:
            raise mockserver.TimeoutError()
        return context.gosu_response()

    context.validate = validate  # pylint: disable=W0201
    return context


@pytest.mark.config(
    QC_VACCINATION_JOB_SETTINGS={'enabled': True, 'limit': 100},
)
@pytest.mark.parametrize(
    (
        'pass_',
        'resolution',
        'masked_initials',
        'gosu_times_called',
        'should_fail',
    ),
    [
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456', 'Johny',
            ),
            'verified',
            'J****',
            1,
            False,
            id='verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                None,
                'Johny',
                nirvana_code='a123b456-c789-d987-e654-f321g123h456',
            ),
            'verified',
            'J****',
            1,
            False,
            id='verified from graph',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456', ' johny ',
            ),
            'verified',
            'J****',
            1,
            False,
            id='verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/vaccine/cert/verify/'
                'a123b456-c789-d987-e654-f321g123h456',
                'Johny',
            ),
            'verified',
            'J****',
            1,
            False,
            id='link verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.g0sus1ugi.ru/vaccine/cert/verify/'
                'a123b456-c789-d987-e654-f321g123h456',
                'Johny',
            ),
            'unexpected_format',
            None,
            0,
            False,
            id='link fraud',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456',
                'Иванов',
                'Иван',
                'Иванович',
            ),
            'verified',
            'И***** И*** И*******',
            1,
            False,
            id='verified full name',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456',
                ' иванов',
                'иван  ',
                'Иванович',
            ),
            'verified',
            'И***** И*** И*******',
            1,
            False,
            id='verified full name',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456', 'Johny',
            ),
            'not_verified',
            None,
            1,
            False,
            id='not verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456', 'Johny',
            ),
            'wrong_initials',
            'Q***',
            1,
            False,
            id='wrong_initials',
        ),
        pytest.param(
            utils.make_vaccination_pass(None, 'Johny'),
            'code_missing',
            None,
            0,
            False,
            id='code missing',
        ),
        pytest.param(
            utils.make_pass('1_1'),
            'code_missing',
            None,
            0,
            False,
            id='data missing',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'a123b456-c789-d987-e654-f321g123h456', 'Johny',
            ),
            'verified',
            'J****',
            2,
            True,
            id='timeout',
        ),
    ],
)
async def test_happy_path(
        qc_pools,  # pylint: disable=W0621
        gosu,  # pylint: disable=W0621
        pass_,
        resolution,
        masked_initials,
        gosu_times_called,
        should_fail,
):
    qc_pools.set_items([pass_])
    qc_pools.set_resolution(resolution)
    qc_pools.set_empty_push(should_fail)
    gosu.set_should_fail(should_fail)
    gosu.set_masked_initials(masked_initials)

    # crontask
    await run_cron.main(
        [
            'quality_control.crontasks.validate_vaccination_certificate',
            '-t',
            '0',
        ],
    )

    assert qc_pools.retrieve.times_called == 2
    assert qc_pools.push.times_called == 1
    assert gosu.validate.times_called == gosu_times_called
