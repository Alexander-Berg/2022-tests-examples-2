from aiohttp import web


def get_surge_calculator_response(data, surge_value, surcharge=None):
    result = {
        'zone_id': 'MSK-Entusiast Ryazan',
        'is_cached': False,
        'experiment_id': 'exp_id',
        'experiment_name': 'exp_name',
        'calculation_id': 'some_calculation_id',
        'experiment_layer': 'default',
        'experiments': [],
        'experiment_errors': [],
        'classes': [
            {
                'name': name,
                'surge': {'value': surge_value},
                'value_raw': surge_value,
                'calculation_meta': {
                    'reason': 'pins_free',
                    'smooth': {
                        'point_a': {'value': surge_value, 'is_default': False},
                        'point_b': {'value': surge_value, 'is_default': False},
                    },
                    'counts': {
                        'free': 6,
                        'free_chain': 0,
                        'total': 6,
                        'pins': 0,
                        'radius': 3000,
                    },
                },
            }
            for name in data['classes']
        ],
    }
    if surcharge:
        for sub in result['classes']:
            sub['surge']['surcharge'] = {
                'alpha': surcharge.alpha,
                'beta': surcharge.beta,
                'value': surcharge.surcharge,
            }
    return result


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/calc-surge', self.calc_surge)

    @staticmethod
    async def calc_surge(request):
        data = await request.json()
        return web.json_response(get_surge_calculator_response(data, 1))
