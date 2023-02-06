import pytest

from taxi_schemas import utils


@pytest.mark.nofilldb()
@pytest.mark.parametrize('schema_path', utils.get_all_schemas_paths())
def test_duplications_indexes(schema_path):
    schema_dict = utils.load_yaml(schema_path)
    indexes_names = []
    for index in schema_dict.get('indexes', []):
        name = utils.indexes_sort_representer(index)
        indexes_names.append(name)

    duplicate_indexes = []
    for index_name in indexes_names:
        if indexes_names.count(index_name) > 1:
            duplicate_indexes.append(index_name)

    assert not duplicate_indexes
