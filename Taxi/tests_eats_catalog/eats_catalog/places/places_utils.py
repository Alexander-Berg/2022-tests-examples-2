import typing

from dateutil import parser

from eats_catalog import storage


def create_place(
        eats_catalog_storage,
        place_id: int,
        place_slug: str,
        closed: bool,
        features=storage.Features(),
):
    """
    Хелпер для создания плейсов.
    """

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )
    if closed:
        schedule = storage.WorkingInterval(
            start=parser.parse('2021-03-16T10:00:00+00:00'),
            end=parser.parse('2021-03-16T22:00:00+00:00'),
        )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            brand=storage.Brand(brand_id=place_id),
            slug=place_slug,
            features=features,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=place_id, place_id=place_id, working_intervals=[schedule],
        ),
    )


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


def find_block_stats(block_id: str, data: dict) -> dict:
    """
    Хелпер для поиска статистики блока. В случае если блок не найден,
    то тест упадет с ошибкой.
    """

    # NOTE: переменная нужна только для понятности сообщения об ошибке
    block_found = False

    for block in data['blocks']:
        if block['id'] == block_id:
            assert block['stats'], 'block with id {} is empty'.format(block_id)
            return block['stats']

    assert block_found, 'block with id "{}" not found'.format(block_id)
    return {}


def assert_no_block_or_empty(block_id: str, data: dict):
    """
    Хелпер, который позволяет проверить, что в выдаче нет блока
    с данным идентфикатором или в блоке пустой список заведений.
    """

    block_found = False

    for block in data['blocks']:
        if block['id'] == block_id:
            assert not block['list']

    assert not block_found, 'block with id "{}" found'.format(block_id)


def find_place_by_slug(slug: str, data: typing.Optional[list]) -> dict:
    """
    Хелпер, который позволяет получить заведение по слагу.
    В случае если заведение не найдено тест упадет с ошибкой.
    """
    # NOTE: переменная нужна только для понятности сообщения об ошибке
    place_found = False

    if data is not None:
        for place in data:
            if place['slug'] == slug:
                return place

    assert place_found, 'place with slug "{}" not found'.format(slug)
    return {}


def assert_no_slug(slug: str, data: typing.Optional[list]):
    """
    Хелпер, который позволяет проверить, что в списке нет заведения
    с переданным слагом
    """

    if data is not None:
        for place in data:
            message = 'found unenexpected place "{}"'.format(slug)
            assert place['slug'] != slug, message


def check_block_with_single_place(
        place_id: str, brand_id: str, data: typing.Optional[list],
) -> dict:
    """
    Хелпер, который проверяет, что в блоке присутствует только одно
    заведение и с переданными значениями.
    В противном случае тест упадет с ошибкой.
    """
    # NOTE: переменная нужна только для понятности сообщения об ошибке
    place_found = False

    if data is not None and len(data) == 1:
        for place in data:
            if brand_id is None:
                if place_id is not None and place['id'] == place_id:
                    return place
            elif place_id is None:
                if place['brand']['id'] == brand_id:
                    return place
            else:
                if (
                        place['id'] == place_id
                        and place['brand']['id'] == brand_id
                ):
                    return place

    assert place_found, (
        'place with place_id={} and brand_id={} not found'.format(
            place_id, brand_id,
        )
    )
    return {}
