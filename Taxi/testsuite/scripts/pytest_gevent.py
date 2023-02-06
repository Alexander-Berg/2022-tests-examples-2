# Run pytest with early gevent monkey patch
def pytest_gevent_main():
    import gevent.monkey
    gevent.monkey.patch_all()

    import pytest
    raise SystemExit(pytest.main())


if __name__ == '__main__':
    pytest_gevent_main()
