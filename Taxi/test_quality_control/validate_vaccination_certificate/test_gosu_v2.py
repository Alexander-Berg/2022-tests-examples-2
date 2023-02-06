import pytest

from quality_control.generated.cron import run_cron
from test_quality_control.validate_vaccination_certificate import utils


@pytest.fixture
def gosu_v2(mockserver):
    class GosuV2Context:
        def __init__(self):
            self.should_fail = False
            self.masked_initials = None
            self.incorrect_ck = False
            self.empty_attrs = False
            self.custom_attr = None
            self.item_type = None
            self.item_status = None
            self.item_expired_at = None

        def set_should_fail(self, should_fail):
            self.should_fail = should_fail

        def set_masked_initials(self, masked_initials):
            self.masked_initials = masked_initials

        def set_incorrect_ck(self, incorrect_ck):
            self.incorrect_ck = incorrect_ck

        def set_empty_attrs(self, empty_attrs):
            self.empty_attrs = empty_attrs

        def set_custom_attr(self, custom_attr):
            self.custom_attr = custom_attr

        def set_item_type(self, item_type):
            self.item_type = item_type

        def set_item_status(self, item_status):
            self.item_status = item_status

        def set_item_expired_at(self, item_expired_at):
            self.item_expired_at = item_expired_at

        def gosu_response(self):
            if self.incorrect_ck:
                return mockserver.make_response(status=400)

            response = {
                'items': [
                    {
                        'status': self.item_status,
                        'type': self.item_type,
                        'expiredAt': self.item_expired_at,
                        'attrs': [
                            {'type': 'fio', 'value': self.masked_initials},
                            {'type': 'passport', 'value': 'doc'},
                            {'type': 'birthDate', 'value': '01.01.2000'},
                        ],
                    },
                ],
            }

            if self.empty_attrs:
                del response['items'][0]['attrs']

            if self.custom_attr:
                response['items'][0]['attrs'].append(self.custom_attr)

            return response

    context = GosuV2Context()

    @mockserver.json_handler('/covid-proxy/gosuslugi-v2/9500000024612243')
    async def validate(request):
        if context.should_fail:
            raise mockserver.TimeoutError()
        return context.gosu_response()

    context.validate = validate  # pylint: disable=W0201
    return context


@pytest.mark.config(
    QC_VACCINATION_JOB_SETTINGS={'enabled': True, 'limit': 100},
    QC_VACCINATION_PROVIDER_SETTINGS={
        'gosu-v2': {
            'code_regex': '[0-9]{16}',
            'extract_regex': (
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '(?P<code>[0-9]{16})\\?lang=(?P<lang>en|ru)'
                '&ck=(?P<ck>[a-z0-9]{8}-?'
                '[a-z0-9]{4}-?'
                '[a-z0-9]{4}-?'
                '[a-z0-9]{4}-?'
                '[a-z0-9]{12})'
            ),
            'qr_data_regex': 'https://www.gosuslugi.ru/covid-cert/verify',
        },
    },
)
@pytest.mark.parametrize(
    (
        'pass_',
        'resolution',
        'masked_initials',
        'item_type',
        'item_status',
        'item_expired_at',
        'gosu_v2_times_called',
        'should_fail',
        'incorrect_ck',
        'empty_attrs',
        'custom_attr',
    ),
    [
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '31.12.3000',
            1,
            False,
            False,
            False,
            None,
            id='verified',
        ),
        pytest.param(
            utils.make_vaccination_pass('9500000024612243', 'Johny'),
            'unexpected_format',
            'J****',
            None,
            None,
            None,
            0,
            False,
            False,
            False,
            None,
            id='unexpected_format',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'not_verified',
            None,
            None,
            None,
            None,
            1,
            False,
            True,
            False,
            None,
            id='wrong ck',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'John',
                'von Neumann',
                ' ',
            ),
            'verified',
            'J*** V**********',
            'VACCINE_CERT',
            '1',
            '31.12.3000',
            1,
            False,
            False,
            False,
            None,
            id='empty middle name',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'not_verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '31.12.3000',
            1,
            False,
            False,
            True,
            None,
            id='empty attrs',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '31.12.3000',
            1,
            False,
            False,
            False,
            {'type': 'enPassport', 'envalue': '** *******'},
            id='attr w/o value',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'not_verified',
            'J****',
            'COVID_TEST',
            '1',
            '31.12.3000',
            1,
            False,
            False,
            False,
            None,
            id='wrong type',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'not_verified',
            'J****',
            'VACCINE_CERT',
            '404',
            '31.12.3000',
            1,
            False,
            False,
            False,
            None,
            id='wrong status',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/verify/'
                '9500000024612243?lang=ru&ck=0498e5a526b8e186bfc9dc1a96a07336',
                'Johny',
            ),
            'not_verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '31.12.2000',
            1,
            False,
            False,
            False,
            None,
            id='expired',
        ),
    ],
)
async def test_happy_path(
        qc_pools,  # pylint: disable=W0621
        gosu_v2,  # pylint: disable=W0621
        pass_,
        resolution,
        masked_initials,
        item_type,
        item_status,
        item_expired_at,
        gosu_v2_times_called,
        should_fail,
        incorrect_ck,
        empty_attrs,
        custom_attr,
):
    qc_pools.set_items([pass_])
    qc_pools.set_resolution(resolution)
    qc_pools.set_empty_push(should_fail)
    qc_pools.set_misc_data(
        {
            'type': item_type,
            'status': item_status,
            'expired_at': item_expired_at,
        },
    )
    gosu_v2.set_should_fail(should_fail)
    gosu_v2.set_masked_initials(masked_initials)
    gosu_v2.set_incorrect_ck(incorrect_ck)
    gosu_v2.set_empty_attrs(empty_attrs)
    gosu_v2.set_custom_attr(custom_attr)
    gosu_v2.set_item_type(item_type)
    gosu_v2.set_item_status(item_status)
    gosu_v2.set_item_expired_at(item_expired_at)

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
    assert gosu_v2.validate.times_called == gosu_v2_times_called
