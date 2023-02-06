import copy
import itertools


def check_headers(headers):
    assert 'X-Yandex-UID' in headers
    assert 'X-Request-Language' in headers
    # assert 'X-YaTaxi-PhoneId' in headers


def prepare_queries(query_template, format_kwargs):
    kwarg_names = []
    kwarg_values = []
    for kwarg_name, kwarg_value in format_kwargs.items():
        kwarg_names.append(kwarg_name)
        kwarg_values.append(
            [
                ', '.join(f'"{word}"' for word in permutation)
                for permutation in itertools.permutations(kwarg_value)
            ],
        )

    return [
        query_template.format(**dict(zip(kwarg_names, variant)))
        for variant in itertools.product(*kwarg_values)
    ]


def dict_updater(update: dict):
    def _impl(obj: dict):
        obj = copy.deepcopy(obj)
        obj.update(update)
        return obj

    return _impl


def kv_updater_hook(update: dict):
    return {
        k: kv_updater_hook(v) if isinstance(v, dict) else dict_updater({k: v})
        for k, v in update.items()
    }


def item_view_to_list_view(order):
    result = copy.deepcopy(order)

    result['route'] = {'source': order['route']['source']['short_text']}
    if order['route'].get('destinations'):
        result['route']['destination'] = order['route']['destinations'][-1][
            'short_text'
        ]

    if 'rating' in result['driver']:
        del result['driver']['rating']
    if 'photo_url' in result['driver']:
        del result['driver']['photo']

    if 'payment' in order:
        result['payment'] = {
            key: value
            for key, value in order['payment'].items()
            if key
            in [
                'final_cost',
                'cost',
                'currency_code',
                'cashback',
                'cashback_spent',
            ]
        }

    for key in [
            'legal_entities',
            'park',
            'receipt',
            'receipts',
            'extra_enabled',
            'formatted_duration',
            'calculation',
    ]:
        if key in result:
            del result[key]

    return result
