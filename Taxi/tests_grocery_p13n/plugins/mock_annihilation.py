import pytest


@pytest.fixture(name='mock_annihilation', autouse=True)
def mock_annihilation(mockserver):
    class Context:
        def __init__(self):
            self.annihilations = []

        def add_annihilation(
                self,
                *,
                wallet_id,
                balance_to_annihilate,
                currency,
                annihilation_date,
        ):
            self.annihilations.append(
                {
                    'wallet_id': wallet_id,
                    'balance_to_annihilate': balance_to_annihilate,
                    'currency': currency,
                    'annihilation_date': annihilation_date,
                },
            )

        def clear(self):
            self.annihilations = []

    context = Context()

    @mockserver.json_handler('/cashback-annihilator/v1/annihilation/info')
    def _mock_v1_get_annihilation(request):
        return mockserver.make_response(
            json={'annihilations': context.annihilations}, status=200,
        )

    return context
