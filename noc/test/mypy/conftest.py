def mypy_check_root() -> str:
    return "noc/grad/grad"


def mypy_config_resource() -> tuple[str, str]:
    return "__tests__", "noc/grad/grad/test/mypy/mypy.ini"
