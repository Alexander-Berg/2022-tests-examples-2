from example_service.generated.service.swagger.models import api as api_models


def test_equalness_of_models():
    model_a = api_models.OpenNullable(
        nullable_required_string='kek', required_string='pek',
    )
    model_b = api_models.OpenNullable(
        nullable_required_string='kek', required_string='pek',
    )
    assert model_a == model_b
    assert hash(model_a) == hash(model_b)
