async def test_trigger(pgsql):
    cursor = pgsql['crm_admin'].cursor()
    query = """INSERT INTO crm_admin.campaign(root_id, name, entity_type, trend,
                    kind, discount, state, owner_name,
                    ticket, ticket_status,
                    created_at, updated_at
                )
                VALUES (1, 'кампания', 'User', 'Тип',
                    'подтип', True, 'NEW', 'user1',
                    'Тикет1', 'Открыт',
                    '2020-03-20 01:00:00', '2020-03-20 01:00:00'
                ) RETURNING id"""
    cursor.execute(query)
    campaign_id = cursor.fetchone()[0]

    query = """update crm_admin.campaign set state='SENT' where id=%s"""
    cursor.execute(query, (campaign_id,))

    query = """delete from crm_admin.campaign where id=%s"""
    cursor.execute(query, (campaign_id,))

    query = """select state_from, state_to from crm_admin.campaign_state_log
     where campaign_id=%s order by updated_at"""
    cursor.execute(query, (campaign_id,))

    expected = (('', 'NEW'), ('NEW', 'SENT'), ('SENT', ''))

    for value in expected:
        assert cursor.fetchone() == value
