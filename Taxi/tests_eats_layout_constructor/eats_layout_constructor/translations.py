import pytest


def eats_layout_constructor(data: dict):
    """
    Задает данные для кейсета eats-layout-constructor
    """
    return pytest.mark.translations(**{'eats-layout-constructor': data})


def eats_layout_constructor_ru(data: dict):
    """
    Задает данные для кейсета eats-layout-constructor
    и ru локали
    """
    result = {}
    for key, value in data.items():
        result[key] = {'ru': value}
    return eats_layout_constructor(result)
