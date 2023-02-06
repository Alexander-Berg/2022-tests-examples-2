import grpc
import logging
import random
import requests
import textwrap
import time
from threading import Thread
from typing import Iterable, List
from urllib.request import urlretrieve

from ci.tasklet.common.proto import service_pb2 as ci
from mds.valve.proto import valve_pb2, valve_pb2_grpc
from noc.ci.valve_test_working.proto import valve_test_working_tasklet


class ValveTestWorkingImpl(valve_test_working_tasklet.ValveTestWorkingBase):
    def __init__(self, model):
        self._logger = None
        self._progress = None

        self.cert_path = "./allCAs.pem"

        super(ValveTestWorkingImpl, self).__init__(model)

    def _get_cert(self) -> None:
        urlretrieve(self.input.config.cert_url, filename=self.cert_path)

    def _get_reals(self) -> List[str]:
        response = requests.get(self.input.config.conductor_url, verify=False)
        reals = response.text.strip().split("\n")
        random.shuffle(reals)
        return reals[:self.input.config.reals_number]

    def run(self):
        try:
            self.progress.status = ci.TaskletProgress.Status.RUNNING
            self.ctx.ci.UpdateProgress(self.progress)

            self._get_cert()

            reals = self._get_reals()

            monitors = []
            for i in range(len(reals)):
                monitors.append(MonitorUptimeThread(uptime_check_duration=self.input.config.uptime_check_duration,
                                                    base_url=reals[i],
                                                    info_url=self.input.config.info_url,
                                                    host=self.input.config.host,
                                                    target_revision=self.input.context.target_revision.number,
                                                    rev_change_timeout=self.input.config.rev_change_timeout))

            checker = RulesCheckerThread(duration=self.input.config.rule_break_check_duration,
                                         iters=self.input.config.rule_break_check_iterations,
                                         samples_url=self.input.config.samples_url,
                                         hbf_url_tmpl=self.input.config.hbf_url_tmpl,
                                         valve_grpc_server=self.input.config.valve_grpc_server,
                                         min_ratio=self.input.config.min_ratio,
                                         cert_path=self.cert_path)

            for i in range(len(reals)):
                monitors[i].start()
            checker.start()

            for i in range(len(reals)):
                monitors[i].join(timeout=4000)
            checker.join(timeout=4000)

            self.output.state.success = True
            self.progress.status = ci.TaskletProgress.Status.SUCCESSFUL
            self.ctx.ci.UpdateProgress(self.progress)
        except Exception as err:
            self.logger.error(err, exc_info=True)
            self.output.state.success = False
            self.progress.status = ci.TaskletProgress.Status.FAILED
            self.progress.text = err
            self.ctx.ci.UpdateProgress(self.progress)

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._logger = _create_logger()
        return self._logger

    @property
    def progress(self) -> ci.TaskletProgress:
        if self._progress is None:
            self._progress = ci.TaskletProgress()
            self._progress.job_instance_id.CopyFrom(self.input.context.job_instance_id)
        return self._progress


class MonitorUptimeThread(Thread):
    def __init__(self,
                 uptime_check_duration: int,
                 base_url: str,
                 info_url: str,
                 host: str,
                 target_revision: int,
                 rev_change_timeout: int):
        self.uptime_check_duration = uptime_check_duration

        self.base_url = base_url
        self.info_url = info_url
        self.host = host

        self.target_revision = target_revision
        self.rev_change_timeout = rev_change_timeout

        self.latest_uptime = 0
        self.current_uptime = 0

        self.error = None

        super().__init__()

    """Fetches info from self.info_url

    Updates self.current_uptime and returns current revision
    """
    def _get_info(self) -> str:
        response = requests.get("https://" + self.base_url + self.info_url,
                                verify=False,
                                headers={"Host": f"{self.host}"})
        response.raise_for_status()

        info = response.json()
        self.current_uptime = info["uptime"]
        return f'{info["revision"]}'

    def run(self) -> None:
        try:
            start_time = time.time()

            curr_revision = "-1"
            while f'{self.target_revision}' != curr_revision:
                if time.time() - start_time > self.rev_change_timeout:
                    raise RuntimeError(f"revision not published in {self.rev_change_timeout}")
                time.sleep(1)
                curr_revision = self._get_info()

            for _ in range(self.uptime_check_duration):
                self.latest_uptime = self.current_uptime
                self._get_info()
                if self.current_uptime < self.latest_uptime:
                    raise RuntimeError(f"uptime decreased from {self.latest_uptime} to {self.current_uptime}")
                time.sleep(1)
        except Exception as err:
            self.error = err

    def join(self, timeout=None):
        super(MonitorUptimeThread, self).join(timeout)
        if self.error is not None:
            raise self.error


class RulesCheckerThread(Thread):
    def __init__(self,
                 duration: int,
                 iters: int,
                 samples_url: str,
                 hbf_url_tmpl: str,
                 valve_grpc_server: str,
                 cert_path: str,
                 min_ratio: float) -> None:
        self.duration = duration
        self.iters = iters

        self.samples_url = samples_url
        self.hbf_url_tmpl = hbf_url_tmpl

        self.valve_grpc_server = valve_grpc_server
        self.cert_path = cert_path

        self.min_ratio = min_ratio

        self.error = None

        super().__init__()

    def _get_grpc_creds(self, cert_path: str) -> grpc.ChannelCredentials:
        with open(cert_path, "rb") as f:
            return grpc.ssl_channel_credentials(f.read())

    def _get_hosts(self, cert_path: str, count: int) -> List[str]:
        resp = requests.get(self.samples_url, verify=cert_path)
        resp.raise_for_status()
        samples = resp.json()
        return random.sample({s["FQDN"] for s in samples if s["Origin"] == "HBF"}, count)

    def _get_rules(self, host) -> str:
        resp = requests.get(self.hbf_url_tmpl % host)
        resp.raise_for_status()
        return resp.text

    def _break_rules(self, host: str, rules: Iterable[str]) -> str:
        return textwrap.dedent("""
        #BEGIN IP6TABLES
        *filter
        -A INPUT -j REJECT
        -A OUTPUT -j REJECT
        -A FORWARD -j REJECT
        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        -A INPUT -j REJECT
        -A OUTPUT -j REJECT
        -A FORWARD -j REJECT
        COMMIT
        #END IPTABLES""")

    def _get_verdict(self, grpc_creds: grpc.ChannelCredentials,
                     hosts: Iterable[str],
                     rules: Iterable[str]) -> valve_pb2.ProcessSampleBatchResponse:
        channel = grpc.secure_channel(
            self.valve_grpc_server,
            grpc_creds,
            options=[('grpc.max_receive_message_length', 20971520)],  # 20 MB
        )
        stub = valve_pb2_grpc.ValveServiceStub(channel)
        response = stub.ProcessSampleBatch(valve_pb2.ProcessSampleBatchRequest(
            hosts=hosts,
            HBFRules="\n".join(rules).encode("utf8"),
        ))
        return response

    def _verdicts_differ(self, verdict: valve_pb2.ProcessSampleBatchResponse,
                         broken: valve_pb2.ProcessSampleBatchResponse) -> bool:
        ratio = (len(broken.dropsOrRejects) + 1) / (len(verdict.dropsOrRejects) + 1)
        return ratio > self.min_ratio

    def _run(self) -> None:
        grpc_creds = self._get_grpc_creds(self.cert_path)

        hosts = self._get_hosts(self.cert_path, count=1)
        rules = []
        broken_rules = []
        for host in hosts:
            rules.append(self._get_rules(host))
            broken_rules.append(self._break_rules(host, rules))

        verdict = self._get_verdict(grpc_creds, hosts, rules)
        broken_verdict = self._get_verdict(grpc_creds, hosts, broken_rules)

        if not self._verdicts_differ(verdict, broken_verdict):
            raise RuntimeError("verdicts on correct and broken rules do not differ")

    def run(self) -> None:
        try:
            for _ in range(self.iters):
                self._run()
                time.sleep(self.duration // self.iters)
        except Exception as err:
            self.error = err

    def join(self, timeout=None):
        super(RulesCheckerThread, self).join(timeout)
        if self.error is not None:
            raise self.error


def _create_logger() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(pathname)s:%(lineno)d %(message)s"))

    log = logging.getLogger(__name__)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    return log
