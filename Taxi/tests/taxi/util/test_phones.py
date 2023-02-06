import pytest

from taxi.util import phones


@pytest.mark.parametrize('phone', ['+71234567890', '+123'])
async def test_ok(phone):
    phones.check_phone_number(phone)


@pytest.mark.parametrize('phone', ['71234567890', 'qwerty', ''])
async def test_bad(phone):
    with pytest.raises(phones.BadPhoneNumber):
        phones.check_phone_number(phone)
