# -*- coding: utf-8 -*-

import time
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from sandbox import sdk2


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class CheckAutoMartyWorkability(sdk2.Task):
    """
        Check auto marty workability
    """

    class Parameters(sdk2.Task.Parameters):
        control_testids = sdk2.parameters.String("Control testids", default="204184,226394", required=True)
        experiment_testids = sdk2.parameters.String("Experiment testids (comma separated)", default="204185,204186", required=True)
        clickdaemon_url = sdk2.parameters.String("Clickdaemon url", default="http://yandex.ru/clck/click", required=True)
        adminka_url = sdk2.parameters.String("Ab adminka url", default="http://ab.test.yandex-team.ru", required=True)
        adminka_robot = sdk2.parameters.String("Ab adminka robot name", default="robot-eksperimentus", required=True)
        force_auto_marty_run = sdk2.parameters.Bool("Force call AutoMartyTask", default=True)
        need_fake_data_for_clicks = sdk2.parameters.Bool("Add fake data to solomon graph for clicks (shutting)", default=True)
        need_fake_data_for_server_javascript_errors = sdk2.parameters.Bool("Add fake data to solomon graph for server javascript errors (shutting)", default=True)

    TEMPLATE_CLICK_FULL_URL = '{clickdaemon_url}/events=%5B%7B%22event%22%3A%22click%22%2C%22id%22%3A%22dvrg5y%22%2C%22cts%22%3A1573487928649%2C%22fast%22%3A%7B%22organic%22%3A1%7D%2C%22service%22%3A%22web%22%2C%22subservice%22%3A%22wweb%22%7D%5D/slots={testid},0,{bucket}/%2A'

    TEMPLATE_ERROR_BOOSTER_POST_DATA = '/path=690.3698/slots={testid},0,0/vars=-msg=error-with-testid,-project=auto_marty_workability,-env=production,-yandexuid={yandexuid}/*'

    TEMPLATE_ITS_ENABLE_TESTID_URL = '{adminka_url}/api/v1/its/enable_testid/{testid}'
    TEMPLATE_ITS_DISABLE_TESTID_URL = '{adminka_url}/api/v1/its/disable_testid/{testid}'
    TEMPLATE_ITS_TESTID_STATUS_URL = '{adminka_url}/api/v1/its/testid_status/{testid}'

    ROBOT_OAUTH_KEY_NAME = 'ab_adminka_token'

    def enable_testid(self, testid):
        token = sdk2.Vault.data(
            self.Parameters.adminka_robot,
            CheckAutoMartyWorkability.ROBOT_OAUTH_KEY_NAME
        )
        requests_retry_session().post(
                CheckAutoMartyWorkability.TEMPLATE_ITS_ENABLE_TESTID_URL.format(
                    adminka_url=self.Parameters.adminka_url,
                    testid=testid
                ),
                headers={
                    'Authorization': 'OAuth {}'.format(token)
                },
                timeout=10
        )

    def disable_testid(self, testid):
        token = sdk2.Vault.data(
            self.Parameters.adminka_robot,
            CheckAutoMartyWorkability.ROBOT_OAUTH_KEY_NAME
        )
        requests_retry_session().post(
                CheckAutoMartyWorkability.TEMPLATE_ITS_DISABLE_TESTID_URL.format(
                    adminka_url=self.Parameters.adminka_url,
                    testid=testid
                ),
                headers={
                    'Authorization': 'OAuth {}'.format(token)
                },
                timeout=10
        )

    def is_disabled_testid(self, testid):
        token = sdk2.Vault.data(
            self.Parameters.adminka_robot,
            CheckAutoMartyWorkability.ROBOT_OAUTH_KEY_NAME
        )
        r = requests_retry_session().get(
                CheckAutoMartyWorkability.TEMPLATE_ITS_TESTID_STATUS_URL.format(
                    adminka_url=self.Parameters.adminka_url,
                    testid=testid
                ),
                headers={
                    'Authorization': 'OAuth {}'.format(token)
                },
                timeout=10
        )
        j = r.json()
        return j['status'] == 'disabled'

    def check_clicks(self, control, experiment):
        logging.info('check clicks')
        if self.Parameters.need_fake_data_for_clicks:
            # now we want check case if experiment has less clicks than control (15 points. Mean of each about 10 clicks per minute)
            for p in range(15):
                start_t = time.time()
                for n in range(10 * 60):
                    for bucket in range(5):
                        try:
                            # make click in experiment on every 10th request
                            if n % 10 == 0:
                                r = requests_retry_session().get(
                                    CheckAutoMartyWorkability.TEMPLATE_CLICK_FULL_URL.format(
                                        clickdaemon_url=self.Parameters.clickdaemon_url,
                                        testid=experiment,
                                        bucket=bucket,
                                    ),
                                    timeout=1
                                )

                            # make click in control on every request
                            r = requests_retry_session().get(
                                CheckAutoMartyWorkability.TEMPLATE_CLICK_FULL_URL.format(
                                    clickdaemon_url=self.Parameters.clickdaemon_url,
                                    testid=control,
                                    bucket=bucket,
                                ),
                                timeout=1
                            )
                        except Exception as e:
                            logging.error(e)
                end_t = time.time()
                sleep_t = 60 - (end_t - start_t)
                logging.info('shutting time (clicks) = {}'.format(end_t - start_t))
                if sleep_t > 0:
                    time.sleep(sleep_t)
        else:
            # sleep 15 min
            time.sleep(15 * 60)

    def check_server_javascript_errors(self, control, experiment):
        logging.info('check server javascript errors')
        if self.Parameters.need_fake_data_for_server_javascript_errors:
            for p in range(3):
                start_t = time.time()
                for n in range(60):
                    try:
                        if n % 10 == 0:
                            r = requests_retry_session().post(
                                self.Parameters.clickdaemon_url,
                                data=CheckAutoMartyWorkability.TEMPLATE_ERROR_BOOSTER_POST_DATA.format(
                                    testid=control,
                                    yandexuid=n
                                ),
                                headers={'Content-Type': 'application/octet-stream'},
                                timeout=1
                            )
                        r = requests_retry_session().post(
                                self.Parameters.clickdaemon_url,
                                data=CheckAutoMartyWorkability.TEMPLATE_ERROR_BOOSTER_POST_DATA.format(
                                    testid=experiment,
                                    yandexuid=n
                                ),
                                headers={'Content-Type': 'application/octet-stream'},
                                timeout=1
                        )
                    except Exception as e:
                        logging.error(e)
                end_t = time.time()
                sleep_t = 5 * 60 - (end_t - start_t)
                logging.info('shutting time (server_javascript_error) {}'.format(end_t - start_t))
                if sleep_t > 0:
                    time.sleep(sleep_t)
        else:
            # sleep 15 min
            time.sleep(15 * 60)

    def run(self, func, control, experiment):
        self.enable_testid(control)
        self.enable_testid(experiment)

        if self.is_disabled_testid(control) or self.is_disabled_testid(experiment):
            raise Exception('Can not enable experiment and control testids')

        func(control, experiment)

        if self.Parameters.force_auto_marty_run:
            r = requests_retry_session().get(
                '{}/_regular_?task=AutoMartyTask'.format(self.Parameters.adminka_url),
                timeout=240
            )
            logging.info(r.text)
        else:
            time.sleep(240)

        exceptions = []

        # if AutoMarty disable control or not disable experiment raise Exception
        if not self.is_disabled_testid(experiment):
            exceptions.append(Exception('ERROR: experiment not disabled by AutoMarty'))

        if self.is_disabled_testid(control):
            exceptions.append(Exception('ERROR: control disabled by AutoMarty'))

        self.enable_testid(control)
        self.enable_testid(experiment)

        if self.is_disabled_testid(control):
            exceptions.append(Exception('Can not enable control testid'))
        if self.is_disabled_testid(experiment):
            exceptions.append(Exception('Can not enable experiment testid'))

        if exceptions:
            raise Exception(exceptions)

    def on_execute(self):
        controls = self.Parameters.control_testids.replace(',', ' ').split()
        experiments = self.Parameters.experiment_testids.replace(',', ' ').split()
        if len(experiments) != 2 or len(controls) != 2:
            raise Exception('ERROR: wrong format')
        logging.info('controls = {}, experiments = {}'.format(controls, experiments))
        self.run(self.check_clicks, controls[0], experiments[0])
        # self.run(self.check_server_javascript_errors, controls[1], experiments[1])
