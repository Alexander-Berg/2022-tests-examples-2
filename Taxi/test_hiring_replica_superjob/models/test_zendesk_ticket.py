async def test_make_ticket(load_json, serialize_tiket):
    data = load_json('resume.json')
    ticket = serialize_tiket(data)
    _ticket = load_json('ticket.json')
    assert ticket == _ticket
