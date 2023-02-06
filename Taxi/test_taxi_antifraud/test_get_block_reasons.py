import pytest


@pytest.mark.config(
    AFS_SUPPORT_USER_BLOCK_REASONS={
        'possible_reasons': [
            {'tanker_id': 'qwerty', 'reason': 'run'},
            {'tanker_id': '123', 'reason': 'd'},
        ],
    },
)
async def test_block_reasons(web_app_client):
    response = await web_app_client.get('/v1/block_reasons/get')
    assert response.status == 200
    assert await response.json() == {
        'possible_reasons': [
            {'tanker_id': 'qwerty', 'reason': 'run'},
            {'tanker_id': '123', 'reason': 'd'},
        ],
    }
