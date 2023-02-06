# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest
import pytz


pytest_plugins = ['eats_stub_tinkoff_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_stub_tinkoff'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_card(get_cursor):
    def do_create_card(
            ucid='12345',
            spend_limit_period='IRREGULAR',
            spend_limit_value=0,
            spend_limit_remain=0,
            cash_limit_period='IRREGULAR',
            cash_limit_value=0,
            cash_limit_remain=0,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_stub_tinkoff.cards '
            '(ucid, spend_limit_period, spend_limit_value,'
            'spend_limit_remain, cash_limit_period,'
            'cash_limit_value, cash_limit_remain) '
            'VALUES(%s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            (
                ucid,
                spend_limit_period,
                decimal.Decimal(spend_limit_value),
                decimal.Decimal(spend_limit_remain),
                cash_limit_period,
                decimal.Decimal(cash_limit_value),
                decimal.Decimal(cash_limit_remain),
            ),
        )
        return cursor.fetchone()[0]

    return do_create_card


@pytest.fixture()
def create_setting(get_cursor):
    def do_create_setting(
            code='general',
            strict_mode=True,
            error_mode=False,
            mock_error_code=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_stub_tinkoff.settings '
            '(code, strict_mode, error_mode, mock_error_code) '
            'VALUES(%s, %s, %s, %s) '
            'RETURNING id',
            (code, strict_mode, error_mode, mock_error_code),
        )
        return cursor.fetchone()[0]

    return do_create_setting


@pytest.fixture()
def init_settings(create_setting):
    create_setting(
        code='general',
        strict_mode=True,
        error_mode=False,
        mock_error_code=None,
    )


@pytest.fixture()
def get_card(get_cursor):
    def do_get_card(ucid):
        cursor = get_cursor()
        cursor.execute(
            'SELECT id, ucid, spend_limit_period, '
            'spend_limit_value, spend_limit_remain, '
            'cash_limit_period, cash_limit_value, '
            'cash_limit_remain, created_at, updated_at '
            'FROM eats_stub_tinkoff.cards '
            'WHERE ucid = %s',
            (ucid,),
        )
        result = list(cursor)[0]
        return {
            'id': result[0],
            'ucid': result[1],
            'spend_limit_period': result[2],
            'spend_limit_value': result[3],
            'spend_limit_remain': result[4],
            'cash_limit_period': result[5],
            'cash_limit_value': result[6],
            'cash_limit_remain': result[7],
            'created_at': result[8],
            'updated_at': result[9],
        }

    return do_get_card


@pytest.fixture()
def get_general_setting(get_cursor):
    def do_get_general_setting():
        cursor = get_cursor()
        cursor.execute(
            'SELECT id, code, strict_mode, '
            'error_mode, mock_error_code, '
            'created_at, updated_at '
            'FROM eats_stub_tinkoff.settings '
            'WHERE code = \'general\'',
        )
        result = list(cursor)[0]
        return {
            'id': result[0],
            'code': result[1],
            'strict_mode': result[2],
            'error_mode': result[3],
            'mock_error_code': result[4],
            'created_at': result[5],
            'updated_at': result[6],
        }

    return do_get_general_setting


@pytest.fixture()
def set_strict_and_error_modes(taxi_eats_stub_tinkoff, get_general_setting):
    async def do_set_strict_and_error_modes(
            strict_mode, error_mode, mock_error_code,
    ):
        setting = get_general_setting()
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is False
        assert setting['mock_error_code'] is None

        if strict_mode:
            strict_mode_response = await taxi_eats_stub_tinkoff.post(
                f'/internal/api/v1/strict-mode/turn-on',
            )
        else:
            strict_mode_response = await taxi_eats_stub_tinkoff.post(
                f'/internal/api/v1/strict-mode/turn-off',
            )
        assert strict_mode_response.status == 204

        setting = get_general_setting()
        assert setting['strict_mode'] == strict_mode
        assert setting['error_mode'] is False
        assert setting['mock_error_code'] is None

        if error_mode:
            error_mode_response = await taxi_eats_stub_tinkoff.post(
                f'/internal/api/v1/error-mode/turn-on',
                json={'error_code': mock_error_code},
            )
        else:
            error_mode_response = await taxi_eats_stub_tinkoff.post(
                f'/internal/api/v1/error-mode/turn-off',
            )
        assert error_mode_response.status == 204

        setting = get_general_setting()
        assert setting['strict_mode'] == strict_mode
        assert setting['error_mode'] == error_mode
        assert setting['mock_error_code'] == mock_error_code

    return do_set_strict_and_error_modes


@pytest.fixture()
def create_account(get_cursor):
    def do_create_account(
            number='12345',
            name='Account Name',
            currency='RUB',
            bank_bik='12345678',
            account_type='Current',
            activation_date=datetime.datetime.utcnow().replace(
                tzinfo=pytz.UTC,
            ),
            balance=0,
            authorized=0,
            pending_payments=0,
            pending_requisitions=0,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_stub_tinkoff.accounts('
            'number, name, currency, bank_bik, account_type, activation_date,'
            'balance, authorized, pending_payments, pending_requisitions) '
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            (
                number,
                name,
                currency,
                bank_bik,
                account_type,
                activation_date,
                decimal.Decimal(balance),
                decimal.Decimal(authorized),
                decimal.Decimal(pending_payments),
                decimal.Decimal(pending_requisitions),
            ),
        )
        return cursor.fetchone()[0]

    return do_create_account


@pytest.fixture()
def get_account(get_cursor):
    def do_get_account(account_number):
        cursor = get_cursor()
        cursor.execute(
            'SELECT id, number, name, currency, bank_bik, account_type, '
            'activation_date, balance, authorized, pending_payments, '
            'pending_requisitions '
            'FROM eats_stub_tinkoff.accounts '
            'WHERE number = %s',
            (account_number,),
        )
        result = list(cursor)[0]
        return {
            'id': result[0],
            'number': result[1],
            'name': result[2],
            'currency': result[3],
            'bank_bik': result[4],
            'account_type': result[5],
            'activation_date': result[6],
            'balance': result[7],
            'authorized': result[8],
            'pending_payments': result[9],
            'pending_requisitions': result[10],
        }

    return do_get_account
