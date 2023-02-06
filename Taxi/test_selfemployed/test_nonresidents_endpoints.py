import pytest


@pytest.mark.config(
    SELFEMPLOYED_NONRESIDENT_SETTINGS=dict(
        is_enabled=True,
        eligible_banks=[dict(bik='044525974')],
        account_prefix='40820',
        disabled_tag_name='nonresident_temporary_blocked',
        use_stq=False,
    ),
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, park_id, driver_id, inn, bik, account_number,
            created_at, modified_at)
        VALUES
            ('aaa15', '4_1p', '4_1d', 'm_inn1', NULL, '40820123123',
             NOW(), NOW()),
            ('aaa16', '4_2p', '4_2d', 'm_inn2', NULL, '40819123123',
             NOW(), NOW())
        """,
    ],
)
@pytest.mark.parametrize(
    ('park_id', 'set_tag_name', 'expected_code', 'expected_response'),
    [
        pytest.param(
            '4_1p',
            'some_tag',
            200,
            {'is_nonresident': True, 'has_blocking_tag': False},
        ),
        pytest.param(
            '4_1p',
            'nonresident_temporary_blocked',
            200,
            {'is_nonresident': True, 'has_blocking_tag': True},
        ),
        pytest.param(
            '4_2p',
            'some_tag',
            200,
            {'is_nonresident': False, 'has_blocking_tag': False},
        ),
        pytest.param(
            '4_2p',
            'nonresident_temporary_blocked',
            200,
            {'is_nonresident': False, 'has_blocking_tag': False},
        ),
    ],
)
async def test_nonresident_check(
        park_id,
        set_tag_name,
        expected_code,
        expected_response,
        se_client,
        mockserver,
):
    @mockserver.json_handler('/tags/v2/match_single')
    async def _match_single(*args, **kwargs):
        return {'tags': ['park_test_1', set_tag_name, 'bronze']}

    response = await se_client.post(
        '/nonresident/check', json={'park_id': park_id},
    )

    # assert response
    assert response.status == expected_code
    content = await response.json()
    assert content == expected_response


@pytest.mark.config(
    SELFEMPLOYED_NONRESIDENT_SETTINGS=dict(
        is_enabled=True,
        eligible_banks=[dict(bik='044525974')],
        account_prefix='40820',
        disabled_tag_name='nonresident_temporary_blocked',
        use_stq=False,
    ),
)
@pytest.mark.parametrize(
    ('park_id', 'expected_code'), [pytest.param('4_1p', 200)],
)
async def test_nonresident_unblock(
        park_id, expected_code, se_client, mockserver,
):
    @mockserver.json_handler('/tags/v2/upload')
    async def _v2_upload(request):
        assert request.json == {
            'provider_id': 'selfemployed',
            'remove': [
                {
                    'entity_type': 'park',
                    'tags': [
                        {
                            'name': 'nonresident_temporary_blocked',
                            'entity': park_id,
                        },
                    ],
                },
            ],
        }
        return {}

    response = await se_client.post(
        '/nonresident/unblock', json={'park_id': park_id},
    )

    # assert response
    assert response.status == expected_code
    assert _v2_upload.times_called == 1
