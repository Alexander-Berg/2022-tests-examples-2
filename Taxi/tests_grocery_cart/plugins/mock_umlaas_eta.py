import pytest


@pytest.fixture(name='umlaas_eta', autouse=True)
def mock_umlaas_eta(mockserver):
    class Context:
        def __init__(self):
            self.predicted_times = []
            self.times_called = 0
            self.umlaas_grocery_eta_times_called = 0
            self.umlaas_grocery_eta_prediction = {}

        def set_prediction(
                self,
                eta_min,
                eta_max,
                total_time=0,
                cooking_time=0,
                delivery_time=0,
        ):
            self.umlaas_grocery_eta_prediction = {
                'total_time': total_time,
                'cooking_time': cooking_time,
                'delivery_time': delivery_time,
                'promise': {'min': eta_min, 'max': eta_max},
            }

        def add_prediction(
                self,
                eta_min,
                eta_max,
                total_time=0,
                cooking_time=0,
                delivery_time=0,
        ):
            self.set_prediction(
                eta_min * 60,
                eta_max * 60,
                total_time * 60,
                cooking_time * 60,
                delivery_time * 60,
            )
            times = {'boundaries': {'min': eta_min, 'max': eta_max}}
            if total_time is not None:
                times['total_time'] = total_time
            if cooking_time is not None:
                times['cooking_time'] = cooking_time
            if delivery_time is not None:
                times['delivery_time'] = delivery_time

            self.predicted_times.append(
                {'id': len(self.predicted_times), 'times': times},
            )

    context = Context()

    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        context.umlaas_grocery_eta_times_called += 1
        return context.umlaas_grocery_eta_prediction

    return context
