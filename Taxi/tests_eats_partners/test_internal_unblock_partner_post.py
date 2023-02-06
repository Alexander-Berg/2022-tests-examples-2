import pytest


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize('response_code,partner_id', [(200, 1), (200, 2)])
async def test_internal_unblock_partner(
        taxi_eats_partners, response_code, partner_id, pgsql,
):
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/unblock?partner_id={}'.format(partner_id),
    )
    cursor = pgsql['eats_partners'].cursor()

    assert response.status_code == response_code
    cursor.execute(
        """
    SELECT is_blocked, blocked_at FROM eats_partners.partners
     WHERE partner_id = {}
    """.format(
            partner_id,
        ),
    )
    result = list(cursor)[0]
    assert result[0] is False
    assert result[1] is None
