from example_service.generated.service.swagger.models import api as models


def test_none_as_default() -> None:
    # None was forbiden before despite Optional in field annotation
    obj = models.ExampleListWithDefault(array=None)
    assert obj.array is None
