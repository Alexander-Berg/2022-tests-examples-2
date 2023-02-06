import pytest


def get_verifications(pgsql):
    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(f'SELECT * FROM card_antifraud.cards_verification')

    columns = [it.name for it in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor]
    return rows


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.suspend_periodic_tasks('periodic_verifications_cleanup')
@pytest.mark.pgsql('card_antifraud', files=['pg_card_antifraud.sql'])
async def test_periodic_cleanup(taxi_card_antifraud, pgsql):
    verifications = get_verifications(pgsql)
    assert len(verifications) == 2

    await taxi_card_antifraud.run_periodic_task(
        'periodic_verifications_cleanup',
    )

    verifications = get_verifications(pgsql)
    assert len(verifications) == 1
