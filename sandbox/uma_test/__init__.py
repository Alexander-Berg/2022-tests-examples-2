import os
import datetime as dt
import logging
import requests

from sandbox.sandboxsdk.environments import PipEnvironment
from sandbox.sandboxsdk import process
from sandbox import sdk2

from sandbox.projects.browser.common.git import repositories
from sandbox.projects.browser.common.hpe import HermeticPythonEnvironment

SRC = {'browser': '//logs/browser-umaproto-json-log/1d/{date}',
       'hips': '//logs/browser-hips-metrics-log/1d/{date}'}

DST = {'browser': '//home/browser/perf-stats/umaproto-browser/{date}',
       'hips': '//home/browser/perf-stats/umaproto-hips/{date}'}


class BrowserPerfYtUmaReportTest(sdk2.Task):
    """Run uma report test"""

    HISTOGRAM_JSON = 'hist.json'
    EXPERIMENTS_JSON = 'exps.json'

    class Requirements(sdk2.Requirements):
        environments = [PipEnvironment('virtualenv', '15.1.0')]

    class Parameters(sdk2.Parameters):
        kill_timeout = 20 * 60 * 60  # 20Hr

        _container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=402010931,
            required=True
        )

        with sdk2.parameters.Group('General settings') as general_settings:
            product = sdk2.parameters.String(
                'Histogram product',
                choices=[(_, _) for _ in ('browser', 'hips')],
                default='browser',
                required=True,
            )

            pool = sdk2.parameters.String(
                'YT pool',
                choices=[(_, _) for _ in ('browser', 'robot-browser-yt')],
                default='browser',
                required=True,
            )

            database = sdk2.parameters.String(
                'Database',
                choices=[(_, _) for _ in ('performance', 'performance_test')],
                default='performance',
                required=True,
            )

            date = sdk2.parameters.String("Date (YYYY-MM-DD) or yesterday",
                                          required=True)

            publish = sdk2.parameters.Bool("Publish report", default=False)

            with publish.value[True]:
                slices_url = sdk2.parameters.String(
                    'Slices destination',
                    choices=[(_, _) for _ in
                             ('performance.test.browser.yandex-team.ru',
                              'performance.browser.yandex-team.ru')],
                    default='performance.test.browser.yandex-team.ru',
                    required=True,
                )

        with sdk2.parameters.Group('Extra settings') as extra_settings:
            token = sdk2.parameters.String("Token vault", required=True,
                                           default='browser-yt-token')

            pulse_token = sdk2.parameters.String(
                'Pulse token vault', required=True,
                default='ROBOT_SPEEDY_PULSE_TOKEN')

            stat_user = sdk2.parameters.String("Statface client user name",
                                               required=True,
                                               default='browser-yt-stat-user')

            stat_passw = sdk2.parameters.String("Statface client password",
                                                required=True,
                                                default='browser-yt-stat-pass')

            branch = sdk2.parameters.String("Bryt repo branch", required=True,
                                            default='master')

    def my_path(self, *args):
        return str(self.path('bryt', *args))

    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)

    def on_execute(self):
        repositories.Stardust.bryt().clone(
            self.my_path(), self.Parameters.branch)

        with HermeticPythonEnvironment(
            python_version='2.7.17',
            pip_version='9.0.2',
            requirements_files=[sdk2.Path(self.my_path('requirements.txt'))],
            packages=['uatraits']
        ):

            os.environ['YT_TOKEN'] = sdk2.Vault.data(self.Parameters.token)
            os.environ['STAT_USER'] = \
                sdk2.Vault.data(self.Parameters.stat_user)
            os.environ['STAT_PASSWORD'] = \
                sdk2.Vault.data(self.Parameters.stat_passw)

            cmd = ['fetch_from_clickhouse',
                   '--histograms', self.HISTOGRAM_JSON,
                   '--experiments', self.EXPERIMENTS_JSON,
                   '--db', self.Parameters.database,
                   '--product', self.Parameters.product]

            process.run_process(
                cmd,
                work_dir=self.my_path(),
                log_prefix='fetch',
                outputs_to_one_file=False,
                shell=True
            )

            for _calc_date in self.Parameters.date.split(','):

                calc_date = _calc_date.strip()
                if calc_date.lower() == 'yesterday':
                    calc_date = (dt.datetime.today() - dt.timedelta(days=1))\
                        .strftime('%Y-%m-%d')

                if not calc_date:
                    continue

                if self.Parameters.publish:
                    url = 'https://{}/rest/clickhouse/profiles'\
                        .format(self.Parameters.slices_url)
                    self.logger.info('Creating slices')
                    self.logger.info('Posting to url %s' % url)
                    data = {'date': calc_date,
                            'product': self.Parameters.product}
                    pulse_token = sdk2.Vault.data(self.Parameters.pulse_token)
                    response = requests.post(
                        url, data=data,
                        headers={
                            'Authorization': 'OAuth {}'.format(pulse_token)
                        })
                    self.logger.info(
                        'Response code for slices: {}'.format(
                            response.status_code))
