# pylint: disable=redefined-outer-name,
import copy
import importlib
import os
import sys
import uuid

import pytest

# pylint: disable=wrong-import-position
sys.path.append(os.path.join('submodules', 'codegen'))

from swaggen import gen  # noqa: E402
from swaggen import models  # noqa: E402
from swaggen import ref  # noqa: E402
from swaggen import schema as schema_mod  # noqa: E402
from swaggen import settings as settings_mod  # noqa: E402
from swaggen import tracing  # noqa: E402
from taxi.codegen import packaging  # noqa: E402
from taxi.util import yaml_util  # noqa: E402


class Importer:
    def __init__(self, name):
        self._name = name

    def api_models(self):
        return importlib.import_module(
            self._name + '.generated.swagger.models.api',
        )

    def request(self, name):
        return importlib.import_module(
            self._name + '.generated.swagger.requests.' + name,
        )

    def responses(self):
        return importlib.import_module(
            self._name + '.generated.swagger.responses',
        )


@pytest.fixture
def generator(tmpdir, monkeypatch):
    def generate(name, schema):
        name += '_' + uuid.uuid4().hex
        schema_source = schema_mod.SchemaSource(
            source_type=schema_mod.SourceType.API,
            source_name=name,
            target=settings_mod.ParsingTarget.SERVER,
        )
        schema = schema_mod.Schema(
            data=tracing.Dict(schema, filepath='api.yaml'),
            source=schema_source,
        )
        path = tmpdir.mkdir(name)
        swagger_package = packaging.Package(
            path, (name, 'generated', 'swagger'),
        )
        models_package = swagger_package.make_subpackage('models')

        namespace = 'api'
        schemas_path = '.'
        gen.Generator(
            namespace, [schema], swagger_package, schemas_path=schemas_path,
        ).generate()
        models_schema = schema_mod.Schema(
            data=tracing.Dict(
                {'definitions': schema.data['definitions'].raw},
                filepath='api.yaml',
            ),
            source=schema_source,
        )
        definitions = {
            namespace: models.Definitions(
                namespace=namespace,
                module_name=namespace,
                private=[models_schema],
                protected={},
                libs=[],
            ),
        }
        ref_index = {
            namespace: ref.TargetedSchema(
                models_schema, namespace, swagger_package.full_name, namespace,
            ),
        }
        models.generate_models(
            swagger_package,
            models_package,
            definitions,
            ref_index,
            schemas_path=schemas_path,
        )
        monkeypatch.syspath_prepend(path)
        return Importer(name)

    return generate


@pytest.fixture
def make_schema():
    schema = {
        'swagger': '2.0',
        'info': {'title': 'Title', 'version': '0.0.1a0'},
        'paths': {},
    }

    def make(definitions):
        copy.deepcopy(schema)
        schema['definitions'] = definitions
        return schema

    return make


@pytest.fixture
def petstore(get_file_path, generator):
    schema = yaml_util.load_file(get_file_path('petstore.yaml'))
    return generator('petstore', schema)
