#! -*- coding: utf-8 -*-
from passport.backend.api.settings.octopus_api import FLASH_CALL_NUMBERS
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


def test_can_parse_flash_call_numbers():
    for pn in FLASH_CALL_NUMBERS:
        assert PhoneNumber.parse(pn, allow_impossible=True).international


def test_only_unique_codes():
    seen_codes = [pn[-4:] for pn in FLASH_CALL_NUMBERS]
    assert len(seen_codes) == len(set(seen_codes))


def test_numbers_pool_is_big():
    # Значение на глаз, чтобы уберечся от совсем невероятых багов построения пула
    assert len(FLASH_CALL_NUMBERS) > 2500
