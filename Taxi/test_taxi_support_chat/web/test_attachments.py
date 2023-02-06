import pytest

from taxi_support_chat.internal import attachments


@pytest.mark.parametrize(
    'filename, expected_filename',
    [
        ('test', 'test'),
        ('\x01', ''),
        ('абв\x02гдея', 'abvgdeya'),
        ('а++бв гд  е +я\t', 'a__bv_gd__e__ya_'),
    ],
)
async def test_transliterate_filename(filename, expected_filename):
    transliterated_filename = attachments.transliterate_and_clear_field(
        filename,
    )
    assert transliterated_filename == expected_filename
