import pytest

from taxi import translations


async def test_translations(stq3_context):
    assert stq3_context.translations.client_messages
    assert stq3_context.translations.hiring_forms
    with pytest.raises(translations.BlockNotFoundError):
        assert stq3_context.translations.order
