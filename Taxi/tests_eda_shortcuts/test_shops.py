# pylint: disable=wildcard-import, import-only-modules, import-error
from eda_shortcuts_plugins import *  # noqa: F403 F401
import pytest

from .conftest import get_eda_params


@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(
    EDA_SHORTCUTS_SHOP_OVERRIDES={
        '3179': {'title': 'some_title', 'image_tag': 'some_image_tag'},
        '2777': {'title': 'some_title', 'image_tag': 'some_image_tag2'},
    },
)
async def test_shop_button_shortcuts(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/shops',
        json=req_body,
        headers={
            'X-Yandex-UID': '1234',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj = response.json()
    assert obj['scenario_tops'][0]['scenario'] == 'eats_shop'
    shop_shortcuts = obj['scenario_tops'][0]['shortcuts']
    shop_ids = [int(get_eda_params(x, 'place_id')) for x in shop_shortcuts]
    assert shop_ids == [3621, 3265]

    place_3621 = [
        x for x in shop_shortcuts if int(get_eda_params(x, 'place_id')) == 3621
    ][0]
    assert place_3621['content']['title'] == 'some_title'
    assert place_3621['content']['image_tag'] == 'some_image_tag'

    place_3265 = [
        x for x in shop_shortcuts if int(get_eda_params(x, 'place_id')) == 3265
    ][0]
    assert place_3265['content']['title'] == 'some_title'
    assert place_3265['content']['image_tag'] == 'some_image_tag2'


@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(
    EDA_SHORTCUTS_SHOP_OVERRIDES={
        '3179': {'title': 'some_title', 'image_tag': 'some_image_tag'},
        '2777': {'title': 'some_title', 'image_tag': 'some_image_tag2'},
    },
)
async def test_shop_shortcuts(taxi_eda_shortcuts, mockserver, load_json):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    req_body = {**load_json('dummy.json'), 'shop_format': 'shortcut'}
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/shops',
        json=req_body,
        headers={
            'X-Yandex-UID': '1234',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj = response.json()
    assert obj['scenario_tops'][0]['scenario'] == 'eats_shop'
    shop_shortcuts = obj['scenario_tops'][0]['shortcuts']
    shop_ids = [int(get_eda_params(x, 'place_id')) for x in shop_shortcuts]
    assert shop_ids == [3621, 3265]

    place_3621 = [
        x for x in shop_shortcuts if int(get_eda_params(x, 'place_id')) == 3621
    ][0]
    assert place_3621['content']['title'] == 'some_title'
    assert place_3621['content']['image_tag'] == 'some_image_tag_shortcut'

    place_3265 = [
        x for x in shop_shortcuts if int(get_eda_params(x, 'place_id')) == 3265
    ][0]
    assert place_3265['content']['title'] == 'some_title'
    assert place_3265['content']['image_tag'] == 'some_image_tag2_shortcut'


@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(
    EDA_SHORTCUTS_SHOP_OVERRIDES={
        '3179': {'title': 'some_title', 'image_tag': 'some_image_tag'},
    },
)
async def test_shop_without_override(
        taxi_eda_shortcuts, mockserver, load_json, testpoint,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @testpoint('brand_without_image_tag_override')
    def _testpoint(arg):
        pass

    req_body = {**load_json('dummy.json'), 'shop_format': 'shortcut'}
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/shops',
        json=req_body,
        headers={
            'X-Yandex-UID': '1234',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj = response.json()
    assert obj['scenario_tops'][0]['scenario'] == 'eats_shop'
    shop_shortcuts = obj['scenario_tops'][0]['shortcuts']
    shop_ids = [int(get_eda_params(x, 'place_id')) for x in shop_shortcuts]
    assert shop_ids == [3621]

    assert _testpoint.times_called == 2
    assert _testpoint.next_call()['arg'] == {'brand': '1693'}
    assert _testpoint.next_call()['arg'] == {'brand': '2777'}
