import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_cashback_calculator_plugins import *  # noqa: F403 F401


@pytest.fixture
def _userinfo_mock(mockserver):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_buid_info(request):
        return {
            'buid_info': {
                'buid': 'bank_uid',
                'yandex_uid': 'yandex_uid',
                'phone_id': 'phone_id',
            },
        }

    _userinfo_mock.buid_info_handle = _mock_buid_info
    return _userinfo_mock


@pytest.fixture
def _core_card_mock(mockserver):
    @mockserver.json_handler(
        '/bank-core-card/v1/card/product/get-by-trust-card-id',
    )
    def _mock_product_id(request):
        product_id = request.json['trust_card_id'] + '_product_id'
        return {
            'public_card_id': 'public_card_id',
            'public_agreement_id': 'public_agreement_id',
            'product': product_id,
        }

    _core_card_mock.product_id = _mock_product_id
    return _core_card_mock
