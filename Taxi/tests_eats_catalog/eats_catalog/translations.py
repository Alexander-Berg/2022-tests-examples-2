import pytest


def eats_catalog(data: dict):
    """
    Задает данные для кейсета eats-catalog
    """
    return pytest.mark.translations(**{'eats-catalog': data})


def eats_catalog_ru(data: dict):
    """
    Задает данные для кейсета eats-catalog
    и ru локали
    """
    result = {}
    for key, value in data.items():
        result[key] = {'ru': value}
    return eats_catalog(result)
