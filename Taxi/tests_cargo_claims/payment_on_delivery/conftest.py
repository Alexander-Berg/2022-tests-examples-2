from typing import Optional

import pytest


@pytest.fixture
def mock_cargo_misc_payments_link(mockserver):
    @mockserver.json_handler('/cargo-misc/payments/v1/link')
    def _client(request):
        return {'payment_url': 'some_payment_url'}


@pytest.fixture
def mock_token_fiscalization(mockserver):
    @mockserver.json_handler('/cargo-misc/payments/v1/check-token')
    def _check_token(request):
        return mockserver.make_response(
            json={
                'is_valid': True,
                'test': True,
                'fiscalization_enabled': True,
            },
        )


@pytest.fixture
def mock_token_no_fiscalization(mockserver):
    @mockserver.json_handler('/cargo-misc/payments/v1/check-token')
    def _check_token(request):
        return mockserver.make_response(
            json={
                'is_valid': True,
                'test': True,
                'fiscalization_enabled': False,
            },
        )


@pytest.fixture
def mocker_misc_payments_token(mockserver):
    def wrapper(response: Optional[dict] = None, status: int = 200):
        @mockserver.json_handler('/cargo-misc/payments/v1/check-token')
        def check_token(request):
            result = {} if response is None else response
            return mockserver.make_response(json=result, status=status)

        return check_token

    return wrapper


# pylint: disable=invalid-name
@pytest.fixture
def get_items_fiscalization_by_claim_id(pgsql):
    def wrapper(claim_id: str):
        i_fields = ('cost_value', 'cost_currency')
        if_fields = (
            'vat_code',
            'payment_subject',
            'payment_mode',
            'product_code',
            'country_of_origin_code',
            'customs_declaration_number',
            'excise',
        )
        fields_string = ','.join(
            [
                *[f'i.{field}' for field in i_fields],
                *[f'if.{field}' for field in if_fields],
            ],
        )

        cursor = pgsql['cargo_claims'].cursor()
        cursor.execute(
            f"""
                SELECT {fields_string}
                FROM cargo_claims.items_fiscalization as if,
                     cargo_claims.items as i,
                     cargo_claims.claims as c,
                     cargo_claims.claim_points as cp
                WHERE if.item_id = i.id AND
                      i.droppof_point = cp.id AND
                      cp.type = 'destination' AND
                      cp.claim_uuid = c.uuid_id AND
                      c.uuid_id='{claim_id}'
                ORDER BY cp.visit_order, i.id
            """,
        )

        return [
            {
                field: row[index]
                for index, field in enumerate([*i_fields, *if_fields])
                if row[index] is not None
            }
            for row in cursor
        ]

    return wrapper


@pytest.fixture
def check_driver_ip(pgsql):
    def _wrapper(expected):
        cursor = pgsql['cargo_claims'].cursor()
        cursor.execute(
            f"""
            SELECT ip FROM cargo_claims.taxi_performer_info
            """,
        )
        assert list(cursor)[0][0] == expected

    return _wrapper
