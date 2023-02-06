import pytest

from quality_control.generated.cron import run_cron
from test_quality_control.validate_vaccination_certificate import utils


@pytest.fixture
def imos(mockserver):
    class ImosContext:
        def __init__(self):
            self.should_fail = False
            self.status = 'VACCINATED'
            self.masked_initials = None

        def set_should_fail(self, should_fail):
            self.should_fail = should_fail

        def set_masked_initials(self, masked_initials):
            self.masked_initials = masked_initials

        def set_status(self, status):
            self.status = status

        def imos_response(self):
            if self.masked_initials is None:
                return {'result': False}

            return {
                'result': {
                    'number': 'number',
                    'uid': 'uid',
                    'source': 'source',
                    'created_emias': 'created_emias',
                    'qrCode': 'qrCode',
                    'certificate': {
                        'status': self.status,
                        'start': 'start',
                        'end': 'end',
                        'initials': self.masked_initials,
                        'birthDay': '2000-01-01',
                        'hash': 'hash',
                        'issuer': 'issuer',
                    },
                    'vaccinated': {'complete': True},
                },
            }

    context = ImosContext()

    @mockserver.json_handler('/covid-proxy/imos')
    async def validate(request):
        if context.should_fail:
            raise mockserver.TimeoutError()

        assert request.json['number'] == '5KEKK2589432'
        return context.imos_response()

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
        'status',
        'imos_times_called',
        'should_fail',
    ),
    [
        pytest.param(
            utils.make_vaccination_pass('5KEKK2589432', 'Johny'),
            'verified',
            'J****',
            'VACCINATED',
            1,
            False,
            id='verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                None, 'Johny', nirvana_code='5KEKK2589432',
            ),
            'verified',
            'J****',
            'VACCINATED',
            1,
            False,
            id='verified for graph',
        ),
        pytest.param(
            utils.make_vaccination_pass('5KEKK2589432', ' johny '),
            'verified',
            'J****',
            'VACCINATED',
            1,
            False,
            id='verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://immune.mos.ru/qr?id=5KEKK2589432', 'Johny',
            ),
            'verified',
            'J****',
            'VACCINATED',
            1,
            False,
            id='link verified',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://immune.m0s.ru/qr?id=5KEKK2589432', 'Johny',
            ),
            'unexpected_format',
            None,
            None,
            0,
            False,
            id='link fraud',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                '5KEKK2589432', 'Иванов', 'Иван', 'Иванович',
            ),
            'verified',
            'И***** И*** И*******',
            'VACCINATED',
            1,
            False,
            id='verified full name',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                '5KEKK2589432', ' иванов', 'иван  ', 'Иванович',
            ),
            'verified',
            'И***** И*** И*******',
            'VACCINATED',
            1,
            False,
            id='verified full name',
        ),
        pytest.param(
            utils.make_vaccination_pass('5KEKK2589432', 'Johny'),
            'not_verified',
            None,
            None,
            1,
            False,
            id='not verified',
        ),
        pytest.param(
            utils.make_vaccination_pass('5KEKK2589432', 'Johny'),
            'wrong_initials',
            'Q**',
            'VACCINATED',
            1,
            False,
            id='wrong initials',
        ),
        pytest.param(
            utils.make_vaccination_pass('5KEKK2589432', 'Johny'),
            'not_verified',
            'J****',
            'IRRELEVANT',
            1,
            False,
            id='irrelevant status',
        ),
        pytest.param(
            utils.make_vaccination_pass(None, 'Johny'),
            'code_missing',
            None,
            None,
            0,
            False,
            id='code missing',
        ),
        pytest.param(
            utils.make_pass('1_1'),
            'code_missing',
            None,
            None,
            0,
            False,
            id='data missing',
        ),
        pytest.param(
            utils.make_vaccination_pass('5KEKK2589432', 'Johny'),
            'verified',
            'J****',
            'VACCINATED',
            2,
            True,
            id='timeout',
        ),
    ],
)
async def test_happy_path(
        qc_pools,  # pylint: disable=W0621
        imos,  # pylint: disable=W0621
        pass_,
        resolution,
        masked_initials,
        status,
        imos_times_called,
        should_fail,
):
    qc_pools.set_items([pass_])
    qc_pools.set_resolution(resolution)
    qc_pools.set_empty_push(should_fail)
    qc_pools.set_misc_data({'status': status})
    imos.set_should_fail(should_fail)
    imos.set_masked_initials(masked_initials)
    imos.set_status(status)

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
    assert imos.validate.times_called == imos_times_called
