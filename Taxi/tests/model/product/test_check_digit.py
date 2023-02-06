from stall.model.product import ean13_check_digit


async def test_ean13_check_digit(tap):
    with tap:
        tap.eq(ean13_check_digit('2505240007850'), '0', 'correct')
        tap.eq(ean13_check_digit('2505240007928'), '8', 'correct')
        tap.eq(ean13_check_digit('2505240007096'), '6', 'correct')
        tap.eq(ean13_check_digit('2302811005792'), '2', 'correct')
        tap.eq(ean13_check_digit('3014260241803'), '3', 'correct')
