"""
Отдельные тесты для ручки /invite. Старые тесты в test_admin.py
со временем должны переехать сюда.
"""

from test_qc_invites.helpers import consts


async def test_invite_invalid_filters(taxi_qc_invites_web, load_json):
    invite_request = load_json('invite_requests.json')[0]
    response = await taxi_qc_invites_web.post(
        consts.INVITE_URL, json=invite_request,
    )
    assert response.status == 400
