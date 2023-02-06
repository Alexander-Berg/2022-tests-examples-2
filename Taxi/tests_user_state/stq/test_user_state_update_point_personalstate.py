import pytest

MOSCOW_POINT = [37.900188446044922, 55.416580200195312]

DEFAULT_YANDEX_UID = 'test_yandex_uid'
DEFAULT_ZONE = 'moscow'
DEFAULT_APP = 'test_app'
DEFAULT_BRAND = 'test_brand'
DEFAULT_CLASS = 'econom'


def get_task_kwargs(application=DEFAULT_APP, classes=None):
    if classes is None:
        classes = [DEFAULT_CLASS]
    return {
        'yandex_uid': 'test_yandex_uid',
        'point': MOSCOW_POINT,
        'application': application,
        'selected_classes': classes,
    }


PERSONALSTATE_FIELDS_TO_POP = ['_id', 'updated']


def get_mongo_personalstate(
        mongodb,
        yandex_uid=DEFAULT_YANDEX_UID,
        zone=DEFAULT_ZONE,
        brand=DEFAULT_BRAND,
        fields_to_pop=None,
):
    if fields_to_pop is None:
        fields_to_pop = PERSONALSTATE_FIELDS_TO_POP

    result = mongodb.personal_state.find_one(
        {'yandex_uid': yandex_uid, 'nearest_zone': zone, 'brand': brand},
    )
    if result is None:
        return None

    for field in fields_to_pop:
        if field in result:
            result.pop(field)

    return result


def get_personalstate(
        brand=DEFAULT_BRAND,
        selected_class=DEFAULT_CLASS,
        multiclass_classes=None,
        tariffs=None,
):
    result = {
        'yandex_uid': DEFAULT_YANDEX_UID,
        'nearest_zone': DEFAULT_ZONE,
        'brand': brand,
        'revision_id': 0,
        'selected_vertical': None,
        'tariffs': tariffs or [],
    }

    if multiclass_classes is None:
        result['selected_class'] = selected_class
    else:
        result['multiclass_options'] = {
            'class': multiclass_classes,
            'selected': True,
        }
    return result


@pytest.mark.config(APPLICATION_MAP_BRAND={DEFAULT_APP: DEFAULT_BRAND})
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_ok(stq_runner, mongodb):
    task_kwargs = get_task_kwargs()

    await stq_runner.user_state_update_point_personalstate.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    personalstate = get_mongo_personalstate(mongodb)
    assert personalstate == get_personalstate()


@pytest.mark.config(APPLICATION_MAP_BRAND={DEFAULT_APP: DEFAULT_BRAND})
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_ok_multiclass(stq_runner, mongodb):
    classes = [DEFAULT_CLASS, 'another_class', 'yet_another_class']
    task_kwargs = get_task_kwargs(classes=classes)

    await stq_runner.user_state_update_point_personalstate.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    personalstate = get_mongo_personalstate(mongodb)
    assert personalstate == get_personalstate(multiclass_classes=classes)


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_unknown_app(stq_runner, mongodb):
    task_kwargs = get_task_kwargs(application='unknown')

    await stq_runner.user_state_update_point_personalstate.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    personalstate = get_mongo_personalstate(mongodb, brand=None)
    assert personalstate == get_personalstate(brand=None)


@pytest.mark.config(APPLICATION_MAP_BRAND={DEFAULT_APP: DEFAULT_BRAND})
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'is_point_in_geoindex',
    [
        pytest.param(
            True,
            marks=pytest.mark.geoareas(
                filename='geoareas.json', db_format=True,
            ),
            id='Point in index',
        ),
        pytest.param(False, id='Point not in index'),
    ],
)
@pytest.mark.parametrize(
    'current_personalstate',
    [
        pytest.param(None, id='No personalstate for zone'),
        pytest.param(
            get_personalstate(selected_class='business'),
            id='Personalstate already exists',
        ),
    ],
)
@pytest.mark.parametrize(
    'can_be_default, selected_class',
    [
        pytest.param(False, 'minivan', id='Class can not be default'),
        pytest.param(True, 'econom', id='Class can be default'),
    ],
)
async def test_no_update(
        stq_runner,
        mongodb,
        is_point_in_geoindex,
        current_personalstate,
        can_be_default,
        selected_class,
):
    task_kwargs = get_task_kwargs(classes=[selected_class])

    if current_personalstate:
        mongodb.personal_state.insert(current_personalstate)
        current_personalstate.pop('_id')

    await stq_runner.user_state_update_point_personalstate.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    personalstate = get_mongo_personalstate(mongodb)
    should_update = (
        is_point_in_geoindex
        and can_be_default
        and current_personalstate is None
    )

    if should_update:
        assert personalstate == get_personalstate()
    else:
        assert personalstate == current_personalstate


@pytest.mark.config(APPLICATION_MAP_BRAND={DEFAULT_APP: DEFAULT_BRAND})
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_invalid_personalstate_in_db(stq_runner, mongodb):
    task_kwargs = get_task_kwargs()

    invalid_personalstate = get_personalstate(
        tariffs=[{'class': DEFAULT_CLASS, 'requirements': {'invalid': None}}],
    )
    mongodb.personal_state.insert(invalid_personalstate)
    invalid_personalstate.pop('_id')
    ps_before = invalid_personalstate

    await stq_runner.user_state_update_point_personalstate.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    ps_after = get_mongo_personalstate(mongodb)
    assert ps_after == ps_before
