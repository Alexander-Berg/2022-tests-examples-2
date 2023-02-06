# flake8: noqa: F401
# pylint: disable=import-only-modules

from .structures import Settings as SettingsStruct

# pylint: disable=invalid-name
settings: SettingsStruct


def init(*_, **kwargs) -> None:
    # pylint: disable=global-statement
    global settings
    settings = SettingsStruct(**kwargs)


def clear():
    # pylint: disable=global-statement
    global settings
    settings = SettingsStruct()
