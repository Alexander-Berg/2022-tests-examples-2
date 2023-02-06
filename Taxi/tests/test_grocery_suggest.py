import json

from taxi_pyml.grocery.suggest.views.v1 import objects
from taxi_pyml.grocery.suggest.views.v1 import view


def test_static_resource(get_directory_path):
    static_resource = view.load_static_resource(
        get_directory_path('resources'),
    )

    assert (
        static_resource.get_item_info('ba8ec170-022a-11ea-b7fe-ac1f6b974fa0')
        is not None
    )
    assert static_resource.get_items_by_category('Просто хлеб') is not None


def test_ml_request(load_json):
    request = load_json('request.json')
    assert json.dumps(request, sort_keys=True) == json.dumps(
        objects.MLRequest.deserialize(request).serialize(), sort_keys=True,
    )
