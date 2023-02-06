import json
from typing import Any
from typing import Dict
from typing import Generator
from typing import Tuple

from . import generators

_GENERATORS: dict = {
    '$oid': generators.Oid,
    '$collection_lookup': generators.CollectionLookup,
    '$json_string': generators.ObjectToJsonString,
    '$randint': generators.RandomInt,
    '$one_by_one': generators.OneByOne,
    '$serial': generators.Serial,
    '$str': generators.Str,
}


class ObjectHook:
    def __init__(self, additional_generators: dict = None):
        self._additional_generators: dict = additional_generators or {}
        self._hooks: Dict[Tuple[str, str], generators.Generator] = {}

    def _get_generator(
            self, generator, options: dict = None,
    ) -> generators.Generator:
        options = options or {}
        hashed_options = json.dumps(options, sort_keys=True)
        if (generator, hashed_options) not in self._hooks:
            if '__id__' in options:
                options.pop('__id__')
            additional_generator = self._additional_generators.get(generator)
            if additional_generator:
                self._hooks[
                    (generator, hashed_options)
                ] = self._additional_generators[generator](**options)
            elif generator in _GENERATORS:
                self._hooks[(generator, hashed_options)] = _GENERATORS[
                    generator
                ](**options)
            else:
                allowed_generators = set(_GENERATORS.keys())
                allowed_generators.update(self._additional_generators.keys())
                allowed_generatores_str = ', '.join(sorted(allowed_generators))
                msg = (
                    f'unknown generator {generator}, '
                    f'variants: {allowed_generatores_str}'
                )
                raise TypeError(msg)

        return self._hooks[(generator, hashed_options)]

    def __call__(self, obj) -> Any:
        if len(obj) == 1:
            generator_keys = _get_generator_keys(obj)
            if generator_keys:
                name = generator_keys[0]
                value = obj[name]
                generator = self._get_generator(name, value)
                return generator.fetch()
        return obj


def fixture_pipeline(
        content, additional_generators: dict = None,
) -> Generator[Any, None, None]:
    object_hook = ObjectHook(additional_generators)
    while True:
        yield json.loads(content, object_hook=object_hook)


def _get_generator_keys(obj):
    return [key for key in obj if key.startswith('$')]
