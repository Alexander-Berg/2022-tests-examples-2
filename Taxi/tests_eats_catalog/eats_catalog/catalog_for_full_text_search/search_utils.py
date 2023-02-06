import typing


def find_block(block_id: str, data: dict) -> list:
    """
    Хелпер для поиска заведений в блоке. В случае если блок не найден,
    то тест упадет с ошибкой.
    """

    # NOTE: переменная нужна только для понятности сообщения об ошибке
    block_found = False

    for block in data['blocks']:
        if block['id'] == block_id:
            assert block['list'], f'block with id {block_id} is empty'
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
            if place['slug'] == slug:
                return place

    assert place_found, f'place with slug "{slug}" not found'
    return {}


def assert_no_slug(slug: str, data: typing.Optional[list]):
    """
    Хелпер, который позволяет проверить, что в списке нет завения
    с переданным слагом
    """

    if data is not None:
        for place in data:
            message = f'found unenexpected place "{slug}"'
            assert place['slug'] != slug, message


def assert_no_block_or_empty(block_id: str, data: dict):
    """
    Хелпер, который позволяет проверить, что в выдаче нет блока
    с данным идентфикатором или в блоке пустой список заведений.
    """

    block_found = False

    for block in data['blocks']:
        if block['id'] == block_id:
            assert block == {'id': block_id, 'list': []}

    assert not block_found, f'block with id "{block_id}" found'


def get_slugs_order(data: typing.Optional[list]) -> list:
    """
    Возвращает слаги в том порядке, в котором
    они расположены в блоке
    """

    result = []
    if data is not None:
        for place in data:
            result.append(place['slug'])
    return result
