async def test_chiefs(library_context, staff_mockserver):
    staff_mockserver()
    chief_logins = await library_context.staff_api.get_chiefs_login(
        ['nevladov', 'oxcd8o', 'deoevgen'],
    )
    assert chief_logins == {'nevladov': 'ilyasov', 'oxcd8o': 'ilyasov'}
