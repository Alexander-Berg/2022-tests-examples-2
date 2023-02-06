import itertools
import operator


class Services:
    def __init__(self, services):
        self.services = services

    @property
    def branches(self):
        return itertools.chain.from_iterable(
            map(operator.itemgetter('branches'), self.services),
        )

    @property
    def configs(self):
        return itertools.chain.from_iterable(
            map(operator.itemgetter('configs'), self.branches),
        )

    @property
    def events(self):
        return itertools.chain.from_iterable(
            map(operator.itemgetter('events'), self.configs),
        )


def compare_db_models(db_models, expected_models):
    def _extract_dict(model, keys):
        if isinstance(model, dict):
            return {x: model[x] for x in keys}
        return {x: getattr(model, x) for x in keys}

    assert len(db_models) == len(
        expected_models,
    ), f'{len(db_models)} != {len(expected_models)}'
    for i, (db_model, expected_model) in enumerate(
            zip(db_models, expected_models),
    ):
        extracted = _extract_dict(db_model, expected_model.keys())
        assert (
            extracted == expected_model
        ), f'{i} : {extracted} != {expected_model}'
