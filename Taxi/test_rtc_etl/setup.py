SERVICE_NAME = 'test_rtc_etl'
DISTRIBUTION_NAME = 'yandex-taxi-dmp-test-rtc-etl'

if __name__ == '__main__':
    from tools.setup_utils import setup_etl_project
    setup_etl_project(SERVICE_NAME, DISTRIBUTION_NAME)
