import pytest

from model_gen import parse


@pytest.mark.parametrize(
    'filename',
    [
        'empty_object.yaml',
        'default_required.yaml',
        'recurse.yaml',
        'required_absent_property.yaml',
    ],
)
def test_unsupported_yaml(get_file_path, filename):
    with pytest.raises(AssertionError):
        parse.gen_params(get_file_path(filename), 'test_project')


def test_custom_vector_default(get_file_path):
    params = parse.gen_params(
        get_file_path('custom_vector_default.yaml'), 'test_project',
    )
    prop = params['definitions'][0].properties[0]
    with pytest.raises(NotImplementedError):
        if prop.has_default:
            prop.cxx_default
