import typing


def mypy_check_root() -> str:
    # Из-за того что у нас спрямлен NAMESPACE тут
    # нужно указывать не абсолютный аркадийный путь
    return "checkist"


def mypy_config_resource() -> typing.Tuple[str, str]:
    return "__tests__", "noc/checkist/mypy.ini"
