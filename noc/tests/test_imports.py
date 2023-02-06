import pytest


def test_import_modules():
    import aiohttp
    import aiozk
    import click
    import motor
    import pydantic
    import pymongo
    import requests
    import urllib3
    import dateutil
    # import aioalexandria
    import aioblackbox
    import annlib
    import authen
    import rtapi


def test_import_failure():
    with pytest.raises(ImportError):
        import unexpected_module
