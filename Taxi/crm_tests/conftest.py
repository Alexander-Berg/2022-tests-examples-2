import allure
import datetime
import os
import pytest
import random
import requests
import string
import time

from appium import webdriver as appium_webdriver
from filelock import FileLock
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium import webdriver as selenium_webdriver
from tvmauth import BlackboxTvmId
from tvm2 import TVM2
from vault_client.instances import Production as VaultClient

from apis.api_helper import ApiHelper
from screens.campaign_card_screen import CampaignCardScreen
from screens.campaign_form_screen import CampaignFormScreen

# в тикете EFFICIENCYTEST-448 будет доработка, чтобы ошибку 500 оставить только для unstable API
STATUSES_TO_RETRY = [500, 502, 503, 504]


def pytest_addoption(parser):
    parser.addoption(
        "--platform", action="store", default="android", help="permitted values: android, ios"
    )
    parser.addoption(
        "--app", action="store", default="pro", help="permitted values: pro, go"
    )
    parser.addoption(
        "--link", action="store", default="https://campaign-management-unstable.taxi.tst.yandex-team.ru/campaigns",
        help="URL for test environment"
    )
    parser.addoption(
        "--api_url", action="store", default="http://crm-admin.taxi.tst.yandex.net", help="URL for crm-admin API"
    )
    parser.addoption(
        "--startrack_url", action="store", default="https://st-api.yandex-team.ru/v2", help="URL for startrack api"
    )
    parser.addoption(
        "--audience", action="store", default="Driver", help="Campaign audience: Driver, User, EatsUser, LavkaUser, Geo"
    )
    parser.addoption(
        "--campaign_type", action="store", default="oneshot", help="Campaign type: oneshot or regular"
    )
    parser.addoption(
        # "--yql_url", action="store", default="https://yql.yandex-team.ru/api/v2/operations/", help="URL for YQL api"
        "--yql_url", action="store", default="https://yql.yandex.net/api/v2/operations/", help="URL for YQL api"
    )
    parser.addoption(
        "--vault_url", action="store", default="https://vault-api.passport.yandex.net", help="URL for vault api"
    )
    parser.addoption(
        "--author", action="store", default="robot-crm-tester", help="Author of campaigns in CRM."
    )

    parser.addoption(
        '--test_suite', action='store', default="api_main", help="Which test suite to use in API tests "
                                                                 "(api_main, integration)"
    )

    parser.addoption(
        '--frontend_api', action='store', default="api-t", help="Which API frontend will use"
                                                                "(api-t, api-u)"
    )


main_test_cases = [
    pytest.param({"audience": "Driver", "campaign_type": "oneshot", "channel": "PUSH",
                  "com_politic": True, "efficiency": False, "segment_version": "1",
                  "global_control": False, "extra_data": "csv", "groups_count": 1,
                  "group_limit": 10, "segment_type": "default"},
                 marks=[pytest.mark.api_driver_oneshot, pytest.mark.driver_integration],
                 id="Driver_oneshot"),
    pytest.param({"audience": "User", "campaign_type": "oneshot", "channel": "PUSH",
                  "com_politic": False, "efficiency": True, "extra_data": "yt",
                  "segment_version": "0", "global_control": True, "groups_count": 5,
                  "group_limit": 1000, "segment_type": "100K"},
                 marks=pytest.mark.api_user_oneshot,
                 id="User_oneshot"),
    pytest.param({"audience": "EatsUser", "campaign_type": "oneshot", "channel": "PUSH",
                  "com_politic": True, "efficiency": False, "segment_version": "1",
                  "global_control": True, "extra_data": "csv", "groups_count": 2,
                  "group_limit": 20, "segment_type": "default"},
                 marks=pytest.mark.api_eats_oneshot,
                 id="EatsUser_oneshot"),
    pytest.param({"audience": "LavkaUser", "campaign_type": "oneshot", "channel": "random",
                  "com_politic": True, "efficiency": False, "segment_version": "1",
                  "global_control": False, "extra_data": "csv", "groups_count": 1,
                  "group_limit": 10, "segment_type": "default"},
                 marks=pytest.mark.api_lavka_oneshot,
                 id="LavkaUser_oneshot"),
    pytest.param({"audience": "Geo", "campaign_type": "oneshot", "channel": "PUSH",
                  "com_politic": False, "efficiency": False, "segment_version": "0",
                  "global_control": True, "extra_data": None, "groups_count": 3,
                  "group_limit": 2000, "segment_type": "100K"},
                 marks=pytest.mark.api_geo_oneshot,
                 id="Geo_oneshot"),
    pytest.param({"audience": "Driver", "campaign_type": "regular", "channel": "SMS",
                  "segment_version": "0", "global_control": False, "extra_data": "yt",
                  "groups_count": 1, "group_limit": 2000, "segment_type": "200K"},
                 marks=pytest.mark.api_driver_regular,
                 id="Driver_regular"),
    pytest.param({"audience": "User", "campaign_type": "regular", "channel": "SMS",
                  "segment_version": "1", "global_control": False, "extra_data": "yt",
                  "groups_count": 1, "group_limit": 10, "segment_type": "default"},
                 marks=pytest.mark.api_user_regular,
                 id="User_regular"),
    pytest.param({"audience": "EatsUser", "campaign_type": "regular", "channel": "SMS",
                  "segment_version": "0", "global_control": True, "extra_data": "yt",
                  "groups_count": 5, "group_limit": 2000, "segment_type": "300K"},
                 marks=pytest.mark.api_eats_regular,
                 id="EatsUser_regular"),
    pytest.param({"audience": "LavkaUser", "campaign_type": "regular", "channel": "promo.fs",
                  "segment_version": "0", "global_control": True, "extra_data": None,
                  "groups_count": 3, "group_limit": 1000, "segment_type": "100K"},
                 marks=pytest.mark.api_lavka_regular,
                 id="LavkaUser_regular"),
    pytest.param({"audience": "Geo", "campaign_type": "regular", "channel": "random",
                  "segment_version": "0", "global_control": False, "extra_data": None,
                  "groups_count": 2, "group_limit": 3000, "segment_type": "default"},
                 marks=pytest.mark.api_geo_regular,
                 id="Geo_regular")
]

integration_test_cases = [
    pytest.param({"audience": "Driver", "campaign_type": "oneshot", "channel": "PUSH",
                  "com_politic": False, "efficiency": False, "segment_version": "1",
                  "global_control": False, "extra_data": "csv", "groups_count": 1,
                  "group_limit": 10, "segment_type": "default", "creatives": True},
                 marks=pytest.mark.driver_integration,
                 id="Driver_oneshot_integration"),
    pytest.param({"audience": "User", "campaign_type": "oneshot", "channel": "PUSH",
                  "com_politic": False, "efficiency": False, "extra_data": "csv",
                  "segment_version": "1", "global_control": False, "groups_count": 1,
                  "group_limit": 10, "segment_type": "default", "creatives": True},
                 marks=pytest.mark.user_integration,
                 id="User_oneshot_integration"),
]


def pytest_generate_tests(metafunc):
    if 'test_suite' in metafunc.fixturenames:
        test_suite = metafunc.config.getoption('test_suite')
        if test_suite == "api_main":
            metafunc.parametrize("campaign_params", main_test_cases)
        elif test_suite == "integration":
            metafunc.parametrize("campaign_params", integration_test_cases)
        else:
            pass


@pytest.fixture(scope="session")
def test_suite(request):
    return request.config.getoption("--test_suite")


@pytest.fixture(scope="session")
def author(request):
    return request.config.getoption("--author")


@pytest.fixture(scope="session")
def platform(request):
    return request.config.getoption("--platform")


@pytest.fixture(scope="session")
def app(request):
    return request.config.getoption("--app")


@pytest.fixture(scope="session")
def link(request):
    return request.config.getoption("--link")


@pytest.fixture(scope="session")
def frontend_api(request):
    return request.config.getoption("--frontend_api")


@pytest.fixture(scope="session")
def api_url(request):
    return request.config.getoption("--api_url")


@pytest.fixture(scope="session")
def startrack_url(request):
    return request.config.getoption("--startrack_url")


@pytest.fixture(scope="session")
def yql_url(request):
    return request.config.getoption("--yql_url")


@pytest.fixture(scope="session")
def vault_url(request):
    return request.config.getoption("--vault_url")


@pytest.fixture(scope="session")
def tvm_ticket_crm_admin(vault_client):
    head_version = vault_client.get_version(f"{os.environ['SECRET_ID']}")
    service_secret = head_version['value']['SERVICE_SECRET']
    tvm = TVM2(
        client_id='2031669',
        secret=service_secret,
        blackbox_client=BlackboxTvmId.Prod,
        allowed_clients=(),
        destinations=(2018384,),
    )
    service_tickets = tvm.get_service_tickets('2018384')
    return service_tickets.get('2018384')


@pytest.fixture(scope="session")
def audience(request):
    return request.config.getoption("--audience")


@pytest.fixture(scope="session")
def campaign_type(request):
    return request.config.getoption("--campaign_type")


def random_string():
    return ''.join([random.choice(string.ascii_lowercase) for i in range(10)])


@pytest.fixture()
def custom_param(tmp_path_factory, worker_id):
    if not worker_id:
        return random_string()

    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "custom_param.txt"
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            data = fn.read_text()
        else:
            data = random_string()
            fn.write_text(data)
    return data


@pytest.fixture()
def web_driver(request):
    options = selenium_webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")  # чтобы не появлялись разные попапы про возможности браузера
    options.add_argument("--headless")  # раскомментировать, чтобы запускать в headless режиме
    options.add_argument('--disable-gpu')  # раскомментировать, чтобы запускать в headless режиме
    options.add_argument('window-size=1920x1080')  # раскомментировать, чтобы запускать в headless режиме
    options.add_argument('ignore-certificate-errors')  # без этого не работает в виртуалке
    binary_yandex_driver_file = '/usr/local/bin/yandexdriver'  # path to YandexDriver
    web_driver = selenium_webdriver.Chrome(binary_yandex_driver_file, options=options)
    web_driver.implicitly_wait(5)
    web_driver.get(f"https://aqua.yandex-team.ru/auth-html?login=robot-crm-tester&secretId={os.environ['SECRET_ID']}")
    request.addfinalizer(web_driver.quit)
    return web_driver


@pytest.fixture()
def appium_driver(request, platform, app):
    android_pro_capabilities = {
        'platformName': 'Android',
        'platformVersion': '10',
        'deviceName': 'avd29',
        'avd': 'avd29',
        'appActivity': '.LoginActivity',
        'appPackage': 'ru.yandex.taximeter',
        'androidDeviceReadyTimeout': 120,
        'autoGrantPermissions': True,
        'fullReset': False,
        'isHeadless': True
    }

    android_go_capabilities = {
        'platformName': 'Android',
        'platformVersion': '10',
        'deviceName': 'avd29_1',
        'avd': 'avd29_1',
        'appActivity': 'ru.yandex.taxi.activity.StartActivity',
        'appPackage': 'ru.yandex.taxi.develop',
        'androidDeviceReadyTimeout': 120,
        'autoGrantPermissions': True,
        'fullReset': False,
        'noReset': True,
        'isHeadless': True
    }

    url = 'http://localhost:4723/wd/hub'
    appium_driver = None
    if platform == 'ios':
        pass
    elif platform == 'android':
        if app == 'pro':
            appium_driver = appium_webdriver.Remote(url, android_pro_capabilities)
        elif app == 'go':
            appium_driver = appium_webdriver.Remote(url, android_go_capabilities)

    def tear_down():
        try:
            appium_driver.back()
        except Exception:
            pass
        appium_driver.quit()
    request.addfinalizer(tear_down)
    return appium_driver


@pytest.fixture()
def campaign_form(web_driver, link):
    campaign_form = CampaignFormScreen(web_driver, link)
    campaign_form.open()
    return campaign_form


@pytest.fixture()
def existing_campaign_card(request, web_driver, link):
    campaign_id = request.param
    campaign_card = CampaignCardScreen(web_driver, link, campaign_id=campaign_id)
    campaign_card.open()
    campaign_card.wait_for_card_open()
    return campaign_card


@pytest.fixture()
def new_campaign_card(request, web_driver, link, session, api_url):
    campaign_form = CampaignFormScreen(web_driver, link)
    campaign_form.open()
    campaign_params = request.param
    campaign_form.create_campaign(campaign_params['campaign_type'],
                                  campaign_params['audience'],
                                  campaign_params['campaign_name'],
                                  campaign_params['description'],
                                  campaign_params['trend'],
                                  campaign_params['start'],
                                  campaign_params['end'],
                                  campaign_params['is_creative_needed'],
                                  campaign_params['contact_politics'],
                                  campaign_params['global_control'],
                                  campaign_params['discount_message'],
                                  campaign_params['efficiency_control'],
                                  campaign_params['filter_version'])
    campaign_id = campaign_form.get_campaign_id()
    campaign_card = CampaignCardScreen(web_driver, link, campaign_id)
    campaign_card.wait_for_card_open()

    def teardown():
        session.delete(api_url + f'/v1/internal/campaign/clear?id={campaign_id}')

    request.addfinalizer(teardown)
    return campaign_card, campaign_params


def log_error_response_body(r, *args, **kwargs):
    if 400 <= r.status_code < 600:
        response_info = f'''
        Request URL: {r.url}
        Request Body: {r.request.body}
        Response code: {r.status_code}
        Response body: {r.text}
        '''
        allure.attach(body=response_info, name="Response log", attachment_type=allure.attachment_type.TEXT)
        if r.status_code not in STATUSES_TO_RETRY:
            r.raise_for_status()


def make_session():
    session = requests.Session()
    session.hooks = {
        'response': log_error_response_body
    }
    retries = Retry(total=3, backoff_factor=1, status_forcelist=STATUSES_TO_RETRY)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


@pytest.fixture()
def session(tvm_ticket_crm_admin, author):
    session = make_session()
    session.headers.update({'X-Ya-Service-Ticket': tvm_ticket_crm_admin})
    session.headers.update({'X-Yandex-Login': author})
    return session


@pytest.fixture(scope="session")
def session_for_deleting(tvm_ticket_crm_admin, author):
    session = make_session()
    session.headers.update({'X-Ya-Service-Ticket': tvm_ticket_crm_admin})
    session.headers.update({'X-Yandex-Login': author})
    return session


@pytest.fixture(scope="session")
def startrack_token(vault_client):
    head_version = vault_client.get_version(f"{os.environ['SECRET_ID']}")
    startrack_token = head_version['value']['STARTRACK_TOKEN']

    return startrack_token


@pytest.fixture(scope="session")
def yql_token(vault_client):
    head_version = vault_client.get_version(f"{os.environ['SECRET_ID']}")
    yql_token = head_version['value']['YQL_TOKEN']

    return yql_token


@pytest.fixture(scope="session")
def vault_client():
    vault_client = VaultClient(
        authorization=f"OAuth {os.environ['VAULT_TOKEN']}",
        decode_files=True,
    )
    return vault_client


@pytest.fixture()
def startrack_session(startrack_token):
    session = make_session()
    session.headers.update({"Authorization": f"OAuth {startrack_token}"})
    return session


@pytest.fixture()
def yql_session(yql_token):
    session = make_session()
    session.headers.update({"Authorization": f"OAuth {yql_token}"})
    session.headers.update({"Content-Type": "application/json"})
    session.headers.update({"Accept": "application/json"})
    return session


@pytest.fixture(scope="session")
def delete_old_campaigns(worker_id, session_for_deleting, api_url, author, save_days=1):
    # save_days - сохраним кампании, созданные X дней назад
    # save_days = 0 - удалятся все кампании, кроме созданных сегодня
    if worker_id not in ["gw0", "master"]:
        return
    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset, name='МСК')
    x = datetime.timedelta(days=save_days)
    dt = datetime.datetime.combine(datetime.date.today() - x, datetime.datetime.min.time(), tz)

    api_helper = ApiHelper(api_url, session_for_deleting, startrack_url, startrack_session)
    campaigns = api_helper.get_campaigns_list(author)

    campaigns_to_delete = []
    campaigns_to_wait_and_delete = []

    for campaign in campaigns:
        campaign_id, \
        campaign_name, \
        campaign_type, \
        campaign_state, \
        is_campaign_active, \
        campaign_created_dt = api_helper.get_campaign_params(campaign)
        if "BUG" in campaign['name']:
            print(f"Кампания {campaign_id} нужна для отладки. Не удаляем.")
            continue
        if campaign_created_dt < dt:
            if api_helper.is_terminate_state(campaign_state):
                print(f"Кампания {campaign_id} в терминальном статусе. Можем удалять.")
                campaigns_to_delete.append(campaign_id)
                continue
            if api_helper.can_stop(campaign_type, is_campaign_active):
                print(f"Кампания {campaign_id} регулярная и активная. Можем остановить. Перед удалением будем ждать.")
                api_helper.stop_regular_campaign(campaign_id)
                campaigns_to_wait_and_delete.append(campaign_id)
                continue
            if api_helper.can_terminate(campaign_type, campaign_state):
                print(f"Кампания {campaign_id} может быть переведена в терминальный статус. Останавливаем. "
                      f"Перед удалением будем ждать.")
                api_helper.terminate(campaign_id, campaign_type, campaign_state)
                campaigns_to_wait_and_delete.append(campaign_id)
                continue
            print(f"Кампания {campaign_id}. Не в терминальном статусе и не можем остановить. Не удаляем.")

    if campaigns_to_wait_and_delete:
        timeout = 180
        print(f"Ждем {timeout} секунд перед удалением.")
        time.sleep(timeout)
        campaigns_to_delete.extend(campaigns_to_wait_and_delete)
    for campaign_id in campaigns_to_delete:
        api_helper.delete_campaign(campaign_id)
