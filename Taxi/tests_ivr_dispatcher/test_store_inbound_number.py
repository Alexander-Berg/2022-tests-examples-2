async def test_store_inbound_number(taxi_ivr_dispatcher, pgsql):
    data = {'order_id': '123', 'inbound_number': '321'}
    response = await taxi_ivr_dispatcher.post('/inbound_number', json=data)
    assert response.status == 200

    db = pgsql['ivr_api']
    cursor = db.cursor()
    cursor.execute('SELECT order_id, inbound_number FROM ivr_api.order_data')
    result = list(cursor.fetchall())
    assert len(result) == 1
    assert result[0] == ('123', '321')
