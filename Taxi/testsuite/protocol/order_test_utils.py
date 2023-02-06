import pytest


@pytest.fixture
def couponreserve(mockserver):
    class Context:
        used_count = 0

    ctx = Context()

    @mockserver.json_handler('/coupons/v1/couponreserve')
    def mock_couponreserve(request):
        if ctx.used_count != 0:
            return {
                'exists': True,
                'valid': False,
                'valid_any': False,
                'value': 200,
                'series': 'onlyoneusage',
            }

        ctx.used_count += 1
        return {
            'exists': True,
            'valid': True,
            'valid_any': True,
            'value': 200,
            'series': 'onlyoneusage',
        }

    return ctx
