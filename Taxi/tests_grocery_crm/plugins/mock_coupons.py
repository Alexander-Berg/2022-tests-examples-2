import pytest


@pytest.fixture(name='coupons', autouse=True)
def mock_coupons(mockserver):
    class Context:
        def __init__(self):
            self.saved_referrals = []
            self.expected_request = None

        def set_request_check(self, request):
            self.expected_request = request

        def set_referrals(self, referrals):
            self.saved_referrals = referrals

        def referral_times_called(self):
            return mock_referral.times_called

        def flush(self):
            mock_referral.flush()

    context = Context()

    @mockserver.json_handler('coupons/v1/coupons/referral')
    def mock_referral(request):
        body = request.json
        if context.expected_request is not None:
            for key, value in context.expected_request.items():
                if value is not None:
                    assert body[key] == value
                else:
                    assert key not in body
        return context.saved_referrals

    return context
