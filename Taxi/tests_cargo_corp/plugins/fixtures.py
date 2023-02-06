import pytest

from tests_cargo_corp import utils


@pytest.fixture
def register_default_card(insert_card):
    insert_card(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=utils.YANDEX_UID,
        card_id=utils.CARD_ID,
    )
