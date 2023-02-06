import typing

import pytest

TABLE_PATH = '//home/eda-analytics/artem-volkov/salesforce/main_kitchen'


class MainCategory(typing.NamedTuple):
    # Идентификатор заведения
    place_id: typing.Optional[int]
    # Категория
    name: typing.Optional[str]


def main(categories: typing.List[MainCategory]):
    values: typing.List[dict] = []

    for category in categories:
        values.append(
            {
                'IDAdminka__c': category.place_id,
                'Main_kitchen_type__c': category.name,
            },
        )

    return pytest.mark.yt(
        static_table_data=[{'path': TABLE_PATH, 'values': values}],
    )
