import stall.error_code


async def test_options_guest(api, tap):
    with tap.plan(5):
        t = await api()

        await t.get_ok('api_profile_error_codes')
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('error_codes.0.code')

        received_codes = dict(
            (x['code'], x)
            for x in t.res['json']['error_codes']
        )

        codes = [
            x for x in dir(stall.error_code)
            if isinstance(
                getattr(stall.error_code, x), stall.error_code.ErrorCode
            ) and x != 'OK' and x != 'PARTIAL_INFORMATION'
        ]

        with tap.subtest(len(codes), 'Тестируем все коды') as taps:
            for code in codes:
                taps.in_ok(code, received_codes, f'Код {code} есть')
