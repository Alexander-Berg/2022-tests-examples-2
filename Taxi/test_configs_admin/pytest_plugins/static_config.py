import pytest


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'disable_check_namespace: disable check namespace',
    )


@pytest.fixture(autouse=True)
def disable_check_namespace(request, monkeypatch):
    disable = request.node.get_closest_marker('disable_check_namespace')
    if not disable:
        return
    monkeypatch.setattr('configs_admin.settings.ENABLE_CHECK_NAMESPACE', False)
