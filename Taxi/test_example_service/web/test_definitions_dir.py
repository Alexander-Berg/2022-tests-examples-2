from dummy.generated import models as dummy_models
from example_library.generated import models
from generated.clients_libs.yet_another_service import moi_leo
from generated.clients_libs.yet_another_service import ya_geo
from generated.models import yet_another_service as yas_models

from example_service.generated.service.swagger.models import api


def test_server_model():
    obj = api.ExtraObject.deserialize(
        {
            'extra-name': 'Vasya',
            'now': {},
            'job': {'is_done': False},
            'prop': {'value': True},
        },
    )

    assert obj.extra_name == 'Vasya'
    assert isinstance(obj.now, api.Now)
    assert isinstance(obj.job, models.Job)
    assert obj.prop.value is True

    in_dir_cross_ref = api.ExtraCross.deserialize({'cross': {'name': 'Iron'}})
    assert isinstance(in_dir_cross_ref.cross, api.NewExtraObject)
    assert in_dir_cross_ref.cross.name == 'Iron'

    from_root_to_dir = api.LinkedToDefinitionsDir.deserialize(
        {'property': {'name': 'Hello'}},
    )
    assert isinstance(from_root_to_dir.property, api.NewExtraObject)
    assert from_root_to_dir.property.name == 'Hello'


def test_client_model():
    obj = yas_models.ExtraObject.deserialize(
        {
            'extra-name': 'Petya',
            'another': {'name': 'Crack'},
            'point': {'lat': 21, 'lon': 39},
            'prop': {'value': True},
        },
    )
    assert obj.extra_name == 'Petya'
    assert isinstance(obj.another, yas_models.AnotherObject)
    assert isinstance(obj.point, ya_geo.GeoPoint)
    assert obj.prop.value is True

    from_root_to_dir = yas_models.CubeWrapper.deserialize(
        {'cube': {'size': 10}},
    )
    assert isinstance(from_root_to_dir.cube, yas_models.Cube)
    assert from_root_to_dir.cube.size == 10

    in_dir_cross_ref = yas_models.CrossRef.deserialize(
        {'extra-object': {'name': 'Zapp'}},
    )
    assert isinstance(in_dir_cross_ref.extra_object, yas_models.NewExtraObject)
    assert in_dir_cross_ref.extra_object.name == 'Zapp'


def test_server_libs():
    data = {
        'property': {
            'extra-name': 'name',
            'job1': {'is_done': True},
            'job2': {'is_done': True},
            'dummy': {'name': 'lala'},
            'dummy2': {'name': 'dada'},
            'prop': {'value': True},
            'drop': {'is_done': True},
            'extra_dummy': {'name': 'hoho'},
        },
    }
    objs = [
        api.LibrariesDefinitionsDirRefFromApi.deserialize(data),
        api.LibrariesDefinitionsDirRefFromDir.deserialize(data),
        api.LibrariesDefinitionsDirRefFromRoot.deserialize(data),
    ]
    for obj in objs:
        assert isinstance(obj.property.job1, models.Job)
        assert isinstance(obj.property.job2, models.Job)
        assert isinstance(obj.property.dummy, dummy_models.DummyObject)
        assert isinstance(obj.property.dummy2, dummy_models.DummyObject)
        assert isinstance(obj.property.prop, models.ExtraProperty)
        assert isinstance(obj.property.drop, models.Job)
        assert isinstance(obj.property.extra_dummy, dummy_models.ExtraObject)

    data = {'ref': {'name': 'Jailer'}}
    objs = [
        models.DefinitionsDirRef.deserialize(data),
        models.CrossRef.deserialize(data),
    ]
    for obj in objs:
        assert isinstance(obj.ref, models.NewExtraObject)
        assert obj.ref.name == 'Jailer'


def test_client_libs():
    data = {
        'point': {'lat': 0, 'lon': 0},
        'route': {'route': [{'lat': 0, 'lon': 0}]},
        'moi': {'moi': {'name': 'moi'}},
        'leo': {'leo': {'name': 'leo'}},
        'extra-moi': {'moi': {'name': 'moi'}},
        'extra-leo': {'leo': {'name': 'leo'}},
    }

    objs = [
        yas_models.LibraryRefKingApi.deserialize(data),
        yas_models.LibraryRefKingRoot.deserialize(data),
        yas_models.LibraryRefKingDir.deserialize(data),
    ]

    for obj in objs:
        assert isinstance(obj.point, ya_geo.GeoPoint)
        assert isinstance(obj.route, ya_geo.Route)
        assert isinstance(obj.moi, ya_geo.MoiRef)
        assert isinstance(obj.moi.moi, moi_leo.Moi)
        assert isinstance(obj.leo, ya_geo.LeoRef)
        assert isinstance(obj.leo.leo, moi_leo.Leo)
        assert isinstance(obj.extra_moi, ya_geo.MoiExtraRef)
        assert isinstance(obj.extra_moi.moi, moi_leo.Moi)
        assert isinstance(obj.extra_leo, ya_geo.LeoExtraRef)
        assert isinstance(obj.extra_leo.leo, moi_leo.Leo)

    data = {'name': {'name': 'Grom'}}
    objs = [
        moi_leo.DefinitionsDirRef.deserialize(data),
        moi_leo.CrossRef.deserialize(data),
    ]
    for obj in objs:
        assert isinstance(obj.name, moi_leo.NewExtraObject)
        assert obj.name.name == 'Grom'
