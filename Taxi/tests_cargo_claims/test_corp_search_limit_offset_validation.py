import pytest


@pytest.mark.parametrize(
    'limit,offset,should_fail',
    (
        pytest.param(0, 1000, False),
        pytest.param(10, 1000, False),
        pytest.param(0, 1000, False),
        pytest.param(
            10,
            1000,
            True,
            marks=pytest.mark.config(
                CARGO_CLAIMS_YT_SEARCH_VALIDATION={
                    'enabled': True,
                    'max_limit': 1001,
                },
            ),
        ),
    ),
)
async def test_limit_and_offset_validation(
        state_controller,
        taxi_cargo_claims,
        get_default_headers,
        limit,
        offset,
        should_fail,
):
    claim_info = await state_controller.apply(target_status='new')
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        json={
            'offset': offset,
            'limit': limit,
            'claim_id': claim_info.claim_id,
        },
        headers=get_default_headers(),
    )

    if should_fail:
        assert response.status_code == 400
        assert response.json()['code'] == 'validation_error'
        assert (
            response.json()['message']
            == 'Превышен максимальное значение limit '
            + '+ offset. Для поиска используйте курсор'
        )
    else:
        assert response.status_code == 200
