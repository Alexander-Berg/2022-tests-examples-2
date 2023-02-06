DEFAULT_HEADERS = {
    'X-Forwarded-For': '12.34.56.78, 98.76.54.32',
    'AcceptLanguage': 'ru',
}


async def test_return_moved_410(
        taxi_cargo_claims, create_segment_with_performer, mockserver,
):
    segment = await create_segment_with_performer()
    claim_id = f'order/{segment.cargo_order_id}'

    response = await taxi_cargo_claims.post(
        'v1/admin/claims/return',
        params={'claim_id': claim_id},
        headers=DEFAULT_HEADERS,
        json={
            'last_known_status': 'pickuped',
            'point_id': 1_000_000,
            'ticket': 'support_ticket',
            'comment': 'support_comment',
        },
    )
    assert response.status_code == 410
    assert response.json() == {
        'code': 'use_waybills_admin_page',
        'message': 'Воспользуйтесь админкой вейбиллов',
    }
