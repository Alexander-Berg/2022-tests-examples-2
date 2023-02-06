import pytest

from quality_control.generated.cron import run_cron
from test_quality_control.validate_vaccination_certificate import utils


@pytest.fixture
def gosu_status(mockserver):
    class GosuStatusContext:
        def __init__(self):
            self.should_fail = False
            self.masked_initials = None
            self.empty_attrs = False
            self.custom_attr = None
            self.item_type = None
            self.item_status = None
            self.item_expired_at = None

        def set_should_fail(self, should_fail):
            self.should_fail = should_fail

        def set_masked_initials(self, masked_initials):
            self.masked_initials = masked_initials

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

    context = GosuStatusContext()

    @mockserver.json_handler(
        '/covid-proxy/gosuslugi-status/1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2',
    )
    async def validate(request):
        if context.should_fail:
            raise mockserver.TimeoutError()
        return context.gosu_response()

    context.validate = validate  # pylint: disable=W0201
    return context


@pytest.mark.now('2021-11-30T12:00:00+0000')
@pytest.mark.config(
    QC_VACCINATION_JOB_SETTINGS={'enabled': True, 'limit': 100},
    QC_VACCINATION_PROVIDER_SETTINGS={
        'gosu-status': {
            'code_regex': (
                '[0-9a-fA-F]{8}'
                '\\-[0-9a-fA-F]{4}'
                '\\-[0-9a-fA-F]{4}'
                '\\-[0-9a-fA-F]{4}'
                '\\-[0-9a-fA-F]{12}'
            ),
            'extract_regex': (
                'https://www.gosuslugi.ru/covid-cert/status/'
                '(?P<code>[0-9a-fA-F]{8}'
                '\\-[0-9a-fA-F]{4}'
                '\\-[0-9a-fA-F]{4}'
                '\\-[0-9a-fA-F]{4}'
                '\\-[0-9a-fA-F]{12})'
                '\\?lang=(?P<lang>en|ru)'
            ),
            'qr_data_regex': 'https://www.gosuslugi.ru/covid-cert/status',
            'allowed_deadline': 5,
            'allowed_types': ['VACCINE_CERT', 'TEMPORARY_CERT'],
            'allowed_statuses': ['OK', '1'],
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
        'empty_attrs',
        'custom_attr',
    ),
    [
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
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
            None,
            id='unexpected_format',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
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
            None,
            id='empty middle name',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
                'Johny',
            ),
            'not_verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '31.12.3000',
            1,
            False,
            True,
            None,
            id='empty attrs',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
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
            {'type': 'enPassport', 'envalue': '** *******'},
            id='attr w/o value',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
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
            None,
            id='wrong type',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
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
            None,
            id='wrong status',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
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
            None,
            id='expired',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
                'Johny',
            ),
            'verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '02.12.2021',
            1,
            False,
            False,
            None,
            id='near_expired',
        ),
        pytest.param(
            utils.make_vaccination_pass(
                'https://www.gosuslugi.ru/covid-cert/status/'
                '1e1ec6a6-11a2-4730-bae1-9cfb33c77cd2?lang=ru',
                'Johny',
            ),
            'verified',
            'J****',
            'VACCINE_CERT',
            '1',
            '07.12.2021',
            1,
            False,
            False,
            None,
            id='near_not_expired',
        ),
    ],
)
async def test_happy_path(
        qc_pools,  # pylint: disable=W0621
        gosu_status,  # pylint: disable=W0621
        pass_,
        resolution,
        masked_initials,
        item_type,
        item_status,
        item_expired_at,
        gosu_v2_times_called,
        should_fail,
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
    gosu_status.set_should_fail(should_fail)
    gosu_status.set_masked_initials(masked_initials)
    gosu_status.set_empty_attrs(empty_attrs)
    gosu_status.set_custom_attr(custom_attr)
    gosu_status.set_item_type(item_type)
    gosu_status.set_item_status(item_status)
    gosu_status.set_item_expired_at(item_expired_at)

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
    assert gosu_status.validate.times_called == gosu_v2_times_called
