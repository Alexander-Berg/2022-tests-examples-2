# pylint: disable=import-only-modules
import pytest

from testsuite.utils import http

from selfemployed.db import dbmain
from selfemployed.logic.process_requisites import Requisites
from . import conftest


CONFIG_DIRECT_CALL = dict(
    is_enabled=True,
    eligible_banks=[dict(bik='044525974')],
    account_prefix='40820',
    disabled_tag_name='nonresident_temporary_blocked',
    use_stq=False,
)

CONFIG_DISABLED = {**CONFIG_DIRECT_CALL, **dict(is_enabled=False)}
CONFIG_NON_ELIGIBLE = {**CONFIG_DIRECT_CALL, **dict(eligible_banks=[])}

NONRESIDENT_BANK_ERROR = {
    'title': 'Заголовок: Данный банк не работает с нерезидентами',
    'subtitle': 'Данный банк не работает с нерезидентами - длинный текст',
    'button_text': 'Понятно',
}


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, inn, bik, account_number,
            created_at, modified_at)
        VALUES
            ('aaa15', '41p', '41d', 'm_inn1', NULL, NULL,
             NOW(), NOW()),
            ('aaa16', '42p', '42d', 'm_inn2', NULL, NULL,
             NOW(), NOW())
        """,
    ],
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfemployed_nonresidents': '9.51'},
        },
        'taximeter-ios': {
            'feature_support': {'selfemployed_nonresidents': '1.0'},
        },
    },
)
@pytest.mark.parametrize(
    ('bik', 'account', 'expected_response', 'expected_code', 'useragent'),
    [
        pytest.param(
            '044525974',
            '40820810000000375671',
            {'next_step': 'finish', 'step_count': 7, 'step_index': 7},
            200,
            'Taximeter 9.30',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_DIRECT_CALL,
                ),
            ],
        ),
        pytest.param(
            '044525974',
            '40820810000000375671',
            {'account_error': 'Номер счёта введен некорректно'},
            409,
            'Taximeter 9.30',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_DISABLED,
                ),
            ],
        ),
        pytest.param(
            '04452597',
            '40820810000000375671',
            {
                'bik_error': 'БИК введен некорректно',
                'account_error': 'Номер счёта введен некорректно',
            },
            409,
            'Taximeter 9.30',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_DIRECT_CALL,
                ),
            ],
        ),
        pytest.param(
            '04452597',
            None,
            {'bik_error': 'БИК введен некорректно'},
            409,
            'Taximeter 9.30',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_DIRECT_CALL,
                ),
            ],
        ),
        pytest.param(
            '044525974',
            '40820810000000375671',
            {'bik_error': 'Данный банк не работает с нерезидентами'},
            409,
            'Taximeter 9.30',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_NON_ELIGIBLE,
                ),
            ],
        ),
        pytest.param(
            '044525974',
            '40820810000000375671',
            {
                'bik_error': 'Данный банк не работает с нерезидентами',
                'nonresident_bank_error': NONRESIDENT_BANK_ERROR,
            },
            409,
            'Taximeter 9.51',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_NON_ELIGIBLE,
                ),
            ],
        ),
        pytest.param(
            '044525974',
            '40820810000000375671',
            {
                'bik_error': 'Данный банк не работает с нерезидентами',
                'nonresident_bank_error': NONRESIDENT_BANK_ERROR,
            },
            409,
            'Taximeter 1.0 (123) ios',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_NON_ELIGIBLE,
                ),
            ],
        ),
        pytest.param(
            '044525974',
            None,
            {'next_step': 'finish', 'step_count': 7, 'step_index': 7},
            200,
            'Taximeter 9.51',
            marks=[
                pytest.mark.config(
                    SELFEMPLOYED_NONRESIDENT_SETTINGS=CONFIG_NON_ELIGIBLE,
                ),
            ],
        ),
    ],
)
async def test_post_requisites_nonresident(
        useragent,
        bik,
        account,
        expected_response,
        expected_code,
        se_client,
        se_web_context,
        patch,
        mockserver,
        mock_partner_contracts,
        mock_client_notify,
):
    park_id = '41p'
    driver_id = '41d'
    clid = 'OLD_PARK_CLID'
    se_id = 'aaa15'

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _request_parks(*args, **kwargs):
        return {
            'driver_profiles': [],
            'parks': [{'provider_config': {'yandex': {'clid': clid}}}],
        }

    @mock_partner_contracts('/v1/register_partner/rus/')
    def _register_partner(request):
        assert request.json == {
            'flow': 'selfemployed',
            'rewrite': True,
            'new': True,
            'stage_name': 'newreq',
            'inquiry_id': se_id,
            'params': {
                'selfemployed_id': se_id,
                'clid': clid,
                'company_rs': account,
                'company_bik': bik,
            },
        }
        return {'inquiry_id': 'inquiry_id', 'status': 'status'}

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': f'{park_id}-{driver_id}',
            'collapse_key': f'requisites_saved_{park_id}',
            'notification': {'text': 'Реквизиты сохранены'},
        }
        return {'notification_id': 'notification_id'}

    data = {'step': dbmain.Step.REQUISITES, 'bik': bik}
    if account:
        data.update(personal_account=account)

    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers={'User-Agent': useragent},
        params={'park': park_id, 'driver': driver_id},
        json=data,
    )

    # assert response
    assert response.status == expected_code
    content = await response.json()
    assert content == expected_response

    if not expected_code == 200:
        return

    if not account:
        return

    assert _send_message.times_called == 1

    assert _register_partner.times_called == 1

    # assert db
    postgres = se_web_context.pg
    row = await dbmain.get_from_driver(postgres, park_id, driver_id)
    if data['bik']:
        assert row['bik'] == data['bik']
    else:
        assert not row['bik']

    if data['personal_account']:
        assert row['account_number'] == data['personal_account']
    else:
        assert not row['account_number']

    if bik and account:
        assert row['step'] == dbmain.Step.REQUISITES


@pytest.mark.parametrize(
    ('bik', 'account', 'expected_result'),
    (
        ('044525974', '40820810000000375671', Requisites.Type.NONRESIDENT),
        ('04452597', '40820810000000375671', Requisites.Type.BIK_INVALID),
        ('044525974', None, Requisites.Type.EMPTY),
        ('044525974', '4082081000000037567', Requisites.Type.ACCOUNT_INVALID),
        (
            '044525975',
            '40820810000000375671',
            Requisites.Type.BIK_NONRESIDENT_NOT_ELIGIBLE,
        ),
    ),
)
def test_get_requisites_type(bik, account, expected_result):
    nonresident_config = {
        'account_prefix': '40820',
        'eligible_banks': [{'bik': '044525974'}],
    }
    requisites = Requisites(
        bik, account, Requisites.Context(nonresident_config),
    )
    assert requisites.type_ == expected_result
