import typing


# pylint: disable=import-error
from eats_analytics import eats_analytics


def find_block(block_id: str, data: dict) -> list:
    """
    Хелпер для поиска заведений в блоке. В случае если блок не найден,
    то тест упадет с ошибкой.
    """

    # NOTE: переменная нужна только для понятности сообщения об ошибке
    block_found = False

    for block in data['blocks']:
        if block['id'] == block_id:
            assert block['list'], 'block with id {} is empty'.format(block_id)
            return block['list']

    assert block_found, 'block with id "{}" not found'.format(block_id)
    return []


def find_place_by_slug(slug: str, data: typing.Optional[list]) -> dict:
    """
    Хелпер, который позволяет получить заведение по слагу.
    В случае если завдедение не найдено тест упадет с ошибкой.
    """
    # NOTE: переменная нужна только для понятности сообщения об ошибке
    place_found = False

    if data is not None:
        for place in data:
            if place['payload']['slug'] == slug:
                return place

    assert place_found, 'place with slug "{}" not found'.format(slug)
    return {}


def get_block_slugs(data: typing.Optional[list]) -> typing.List[str]:
    """
    Хелпер, который возвращает все слаги ресторанов в блоке.
    """
    if not data:
        return []

    result = []
    for place in data:
        result.append(place['payload']['slug'])

    return result


def assert_no_slug(slug: str, data: typing.Optional[list]):
    """
    Хелпер, который позволяет проверить, что в списке нет завения
    с переданным слагом
    """

    if data is not None:
        for place in data:
            message = 'found unenexpected place "{}"'.format(slug)
            assert place['payload']['slug'] != slug, message


def assert_no_block_or_empty(block_id: str, data: dict):
    """
    Хелпер, который позволяет проверить, что в выдаче нет блока
    с данным идентфикатором или в блоке пустой список заведений.
    """

    block_found = False

    for block in data['blocks']:
        if block['id'] == block_id:
            assert block == {'id': block_id, 'list': []}

    assert not block_found, 'block with id "{}" found'.format(block_id)


def assert_has_meta_in_layout(meta_id: str, meta_type: str, place: dict):
    found_meta_layout = False
    found_meta = False
    for layout in place['payload']['layout']:
        if layout['type'] == 'meta':
            found_meta_layout = True

            for meta in layout['layout']:
                if meta['id'] == meta_id and meta['type'] == meta_type:
                    found_meta = True
                    break
            break

    assert found_meta_layout and found_meta


def assert_has_action_in_layout(action_id: str, action_type: str, place: dict):
    found_action_layout = False
    found_action = False
    for layout in place['payload']['layout']:
        if layout['type'] == 'actions':
            found_action_layout = True

            for action in layout['layout']:
                if action['id'] == action_id and action['type'] == action_type:
                    found_action = True
                    break
            break

    assert found_action_layout
    assert found_action


def find_first_meta(meta_type: str, place: dict):
    """
    Хелпер, который позволяет проверить, что в данных заведения есть
    мета преденного типа и вернуть ее
    """
    assert (
        'meta' in place['payload']['data'] and place['payload']['data']['meta']
    ), 'meta missing or empty'

    meta_found = False
    for meta in place['payload']['data']['meta']:
        if meta['type'] == meta_type:
            assert_has_meta_in_layout(meta['id'], meta_type, place)
            return meta

    assert meta_found, 'meta {} was not found'.format(meta_type)
    return None


def find_actions(action_type: str, place: dict):
    """
    Хелпер, который позволяет проверить, что в данных заведения есть
    мета преденного типа и вернуть ее
    """
    assert (
        'actions' in place['payload']['data']
        and place['payload']['data']['actions']
    ), 'actions missing or empty'

    actions = []
    for action in place['payload']['data']['actions']:
        if action['type'] == action_type:
            assert_has_action_in_layout(action['id'], action_type, place)
            actions.append(action)

    assert actions
    return actions


def assert_no_actions(action_type: str, place: dict):
    """
    Хелпер, который проверяет, что action-ов определенного типа нет в
    ресторане.
    """
    data = place['payload']['data']
    assert 'actions' in data

    for action in data['actions']:
        assert action['type'] != action_type


def assert_no_meta(place: dict, meta_type: str):
    """
    Хэлпер, который проверяет, что меты определенного типа нет в ресторане.
    """
    for meta in place['payload']['data']['meta']:
        if meta['type'] == meta_type:
            assert False, 'meta of type {} was found in data'.format(meta_type)

    for layout in place['payload']['layout']:
        if layout['type'] != 'meta':
            continue

        for meta in layout['layout']:
            if meta['type'] == meta_type:
                assert False, 'meta of type {} was found in layout'.format(
                    meta_type,
                )


def assert_has_meta(place: dict, meta_type: str):
    """
    Хэлпер, который проверяет, что мета определенного типа есть в ресторане.
    """
    meta_found = False
    for meta in place['payload']['data']['meta']:
        if meta['type'] == meta_type:
            meta_found = True
            break

    layout_meta_found = False
    for layout in place['payload']['layout']:
        if layout['type'] != 'meta':
            continue

        for meta in layout['layout']:
            if meta['type'] == meta_type:
                layout_meta_found = True
                break

    assert meta_found and layout_meta_found


def find_filter_v2(response: dict, filter_slug: str, filter_type: str) -> dict:
    """
    Хелпер, который позволяет найти и вернуть фильтр в ответе ручки
    catalog-for-layout, если фильтр найти не удалось, то фейлится аssert
    """

    filters = response['filters_v2']['list']

    for item in filters:
        if item['slug'] == filter_slug and item['type'] == filter_type:
            return item

    available_filters = [item['type'] + ':' + item['slug'] for item in filters]
    assert False, (
        f'missing filter with slug {filter_slug} and type {filter_type}, '
        f'available filters are {available_filters}'
    )

    return {}


def assert_no_filter_v2(response: dict, filter_slug: str, filter_type: str):
    """
    Проверяет, что в списке фильтров отсутсвует фильтр с переданным слагом
    и типом, если фильтр найден то фейлится assert
    """

    filters = response['filters_v2']['list']

    for item in filters:
        assert not (
            item['slug'] == filter_slug and item['type'] == filter_type
        )


class MatchingAnalyticsContext:
    def __init__(self, ctx: eats_analytics.AnalyticsContext):
        self._ctx: eats_analytics.AnalyticsContext = ctx

    def __repr__(self):
        return str(self._ctx)

    def __eq__(self, other):
        if isinstance(other, str):
            return self._ctx == eats_analytics.decode(other)

        return self._ctx == other
