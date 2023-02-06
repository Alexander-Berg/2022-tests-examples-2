import logging
import re
import time

from sandbox import sdk2
import sandbox.common.errors as errors
from sandbox.common.types.resource import State
from sandbox.common.types.task import Status
from sandbox.projects.alisa_skills_rec.common.resources import ALISA_SKILLS_REC_AMMO, ALISA_SKILLS_REC_AMMO_OLD
from sandbox.projects.common import binary_task, apihelpers
from sandbox.projects.tank.load_resources.resources import YANDEX_TANKAPI_LXC_CONTAINER
from sandbox.projects.common.nanny import nanny
from sandbox.projects.tank.ShootViaTankapi import ShootViaTankapi

logger = logging.getLogger(__name__)


def link_format(href, text, description=""):
    return "{}<a href=\"{}\">{}</a>".format(description, href, text)


class SkillRecPerfTest(binary_task.LastBinaryTaskRelease, sdk2.Task):
    """
    Task that starts the perfomance testing of SkillRec, which is a shooting to two targets (stable and testing) with
    a Yandex.Tank and comparing their results with lunapark compare.
    Snapshots are switched automatically (and are switched back after the task finishes), but you have to make sure they are deployed at nanny.
    """
    class Requirements(sdk2.Task.Requirements):
        ram = 10 * 1024  # 10 Gb
        disk_space = 30 * 1024  # 10 Gb

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 5 * 60 * 60
        startrek_ticket_id = sdk2.parameters.String(
            "StarTrek ticket id",
            required=True,
        )
        test_release_tag = sdk2.parameters.String(
            "Test release tag (for example '39-1', tag should be available as nanny snapshot)",
            required=True,
        )
        stable_release_tag = sdk2.parameters.String(
            "Stable release tag (optional). Can be set to 'auto'",
            required=False,
            default_value=""
        )
        rps_prewarm = sdk2.parameters.Integer(
            "Prewarm RPS. Prewarm stage is used to make sure joker remembers all the sources answers so they will not affect the test. Can be set to 0 (no prewarm)",
            required=True,
            default_value=100
        )
        rps_min = sdk2.parameters.Integer(
            "Starting RPS for all shootings",
            required=True,
            default_value=100
        )
        rps_max_old = sdk2.parameters.Integer(
            "Peak RPS for shooting old handlers",
            required=True,
            default_value=200
        )
        rps_max_new = sdk2.parameters.Integer(
            "Peak RPS for shooting new handlers",
            required=True,
            default_value=200
        )
        duration_old = sdk2.parameters.Integer(
            "Old handlers shooting duration, seconds",
            required=True,
            default_value=600
        )
        duration_new = sdk2.parameters.Integer(
            "New handlers shooting duration, seconds",
            required=True,
            default_value=600
        )
        ammo_old = sdk2.parameters.String(
            "Ammo for old handlers. Can be set to 'auto'",
            required=True,
            default_value="auto"
        )
        ammo_new = sdk2.parameters.String(
            "Ammo for new handlers. Can be set to 'auto'",
            required=True,
            default_value="auto"
        )
        testing_target_url = sdk2.parameters.String(
            "Testing target host[:port]. Should be under alisa-skills-rec-testing-yp-(man|sas|vla)",
            required=False,
        )
        testing_target_dc = sdk2.parameters.String(
            "Testing target DC. Should be one of (man|sas|vla)",
            required=False,
            default_value='man'
        )
        ext_params = binary_task.LastBinaryReleaseParameters()

        with sdk2.parameters.Output:
            old_handlers_testing_lunapark_job_id = sdk2.parameters.String("Old handlers. Testing lunapark job id.", default_value="")
            old_handlers_testing_lunapark_url = sdk2.parameters.String("Old handlers. Testing lunapark url.", default_value="")
            old_handlers_stable_lunapark_job_id = sdk2.parameters.String("Old handlers. Stable lunapark job id.", default_value="")
            old_handlers_stable_lunapark_url = sdk2.parameters.String("Old handlers. Stable lunapark url.", default_value="")
            old_handlers_compare_url = sdk2.parameters.String("Old handlers. Testing vs Stable shootings compare url.", default_value="")
            new_handlers_testing_lunapark_job_id = sdk2.parameters.String("New handlers. Testing lunapark job id.", default_value="")
            new_handlers_testing_lunapark_url = sdk2.parameters.String("New handlers. Testing lunapark url.", default_value="")
            new_handlers_stable_lunapark_job_id = sdk2.parameters.String("New handlers. Stable lunapark job id.", default_value="")
            new_handlers_stable_lunapark_url = sdk2.parameters.String("New handlers. Stable lunapark url.", default_value="")
            new_handlers_compare_url = sdk2.parameters.String("New handlers. Testing vs Stable shootings compare url.", default_value="")

    def on_save(self):
        super(SkillRecPerfTest, self).on_save()

    def on_execute(self):
        super(SkillRecPerfTest, self).on_execute()
        self._nanny = nanny.NannyClient(api_url="http://nanny.yandex-team.ru/", oauth_token=sdk2.Vault.data("skillrec-nanny-oauth"))
        with self.memoize_stage.prepare:
            rps_prewarm = self.Parameters.rps_prewarm
            rps_min = self.Parameters.rps_min
            target_dc = self._determine_dc() if self.Parameters.testing_target_url else self.Parameters.testing_target_dc
            self.Context.nanny_service = "alisa-skills-rec-testing-yp-{}".format(target_dc)
            self.Context.ammo = {}
            self.Context.ammo["new"] = self._get_ammo(self.Parameters.ammo_new, ALISA_SKILLS_REC_AMMO)
            self.Context.ammo["old"] = self._get_ammo(self.Parameters.ammo_old, ALISA_SKILLS_REC_AMMO_OLD)
            self.Context.load_profile = {}
            self.Context.load_profile["new"] = "line({}, {}, {}s)".format(rps_min, self.Parameters.rps_max_new, self.Parameters.duration_new)
            self.Context.load_profile["old"] = "line({}, {}, {}s)".format(rps_min, self.Parameters.rps_max_old, self.Parameters.duration_old)
            total_new = (rps_min + self.Parameters.rps_max_new) * self.Parameters.duration_new / 2
            total_old = (rps_min + self.Parameters.rps_max_old) * self.Parameters.duration_old / 2
            self.Context.prewarm = rps_prewarm > 0
            if self.Context.prewarm:
                self.Context.load_profile["new_prewarm"] = "const({}, {}s)".format(rps_prewarm, total_new / rps_prewarm)
                self.Context.load_profile["old_prewarm"] = "const({}, {}s)".format(rps_prewarm, total_old / rps_prewarm)
            self.Context.shooting = {}
            self.Context.stable_release_tag = self._get_stable_release_tag()
            self.Context.shoot_stable = bool(self.Context.stable_release_tag)
            self.Context.initial_policy = self._select_policy({"type": "NONE"})
            self.Context.initial_snapshot = self._select_snapshot(self.Parameters.test_release_tag, "test")

        if self.Context.prewarm:
            self._shoot(self.Parameters.test_release_tag, "old", "old_prewarm")  # prewarm is done for the purposes of Joker sources mocking
            self._shoot(self.Parameters.test_release_tag, "new", "new_prewarm")
        self._shoot(self.Parameters.test_release_tag, "old", "old")
        self._shoot(self.Parameters.test_release_tag, "new", "new")

        if self.Context.shoot_stable:
            self._select_snapshot(self.Context.stable_release_tag, "stable")
            if self.Context.prewarm:
                self._shoot(self.Context.stable_release_tag, "old", "old_prewarm")
                self._shoot(self.Context.stable_release_tag, "new", "new_prewarm")
            self._shoot(self.Context.stable_release_tag, "old", "old")
            self._shoot(self.Context.stable_release_tag, "new", "new")

        with self.memoize_stage.find_shooting_results:
            testing_result_test_old = self._find_shooting_result(self.Parameters.test_release_tag, "old")
            testing_result_test_new = self._find_shooting_result(self.Parameters.test_release_tag, "new")

            self.Parameters.old_handlers_testing_lunapark_job_id = testing_result_test_old.Parameters.lunapark_job_id
            self.Parameters.old_handlers_testing_lunapark_url = testing_result_test_old.Parameters.lunapark_link
            self.Parameters.new_handlers_testing_lunapark_job_id = testing_result_test_new.Parameters.lunapark_job_id
            self.Parameters.new_handlers_testing_lunapark_url = testing_result_test_new.Parameters.lunapark_link

            if self.Context.shoot_stable:
                testing_result_stable_old = self._find_shooting_result(self.Context.stable_release_tag, "old")
                testing_result_stable_new = self._find_shooting_result(self.Context.stable_release_tag, "new")

                self.Parameters.old_handlers_stable_lunapark_job_id = testing_result_stable_old.Parameters.lunapark_job_id
                self.Parameters.old_handlers_stable_lunapark_url = testing_result_stable_old.Parameters.lunapark_link
                self.Parameters.old_handlers_compare_url = self._compare(self.Parameters.old_handlers_stable_lunapark_job_id, self.Parameters.old_handlers_testing_lunapark_job_id)
                self.set_info(link_format(self.Parameters.old_handlers_compare_url, "Old handlers comparison"), do_escape=False)

                self.Parameters.new_handlers_stable_lunapark_job_id = testing_result_stable_new.Parameters.lunapark_job_id
                self.Parameters.new_handlers_stable_lunapark_url = testing_result_stable_new.Parameters.lunapark_link
                self.Parameters.new_handlers_compare_url = self._compare(self.Parameters.new_handlers_stable_lunapark_job_id, self.Parameters.new_handlers_testing_lunapark_job_id)
                self.set_info(link_format(self.Parameters.new_handlers_compare_url, "New handlers comparison"), do_escape=False)

        self._select_snapshot("", "return initial", self.Context.initial_snapshot)
        self._select_policy(self.Context.initial_policy)

    def _get_ammo(self, ammo, resource_tag):
        if (ammo == "auto"):
            return "https://proxy.sandbox.yandex-team.ru/" + str(apihelpers.get_last_resource(resource_tag).id)
        else:
            return ammo

    def _determine_dc(self):
        target_url = self.Parameters.testing_target_url
        if ".vla.yp-c.yandex.net" in target_url:
            return "vla"
        if ".man.yp-c.yandex.net" in target_url:
            return "man"
        if ".sas.yp-c.yandex.net" in target_url:
            return "sas"
        raise errors.TaskFailure("Failed to determine datacenter location from {}".format(target_url))

    def _compare(self, job_id_test, job_id_stable):
        return "https://lunapark.yandex-team.ru/compare/" \
               "#jobs={stable_id},{testing_id}&tab=test_data&mainjob={stable_id}" \
               "&helper=all&cases=&plotGroup=additional&metricGroup=&target=" \
            .format(testing_id=job_id_test, stable_id=job_id_stable)

    def _shoot(self, release_tag, ammo_type, load_profile_name):
        with self.memoize_stage["start_shooting_" + release_tag + "_" + load_profile_name]:
            target_url = self.Parameters.testing_target_url
            if not target_url:
                target_url = self._determine_target_url()
            shooting_name = release_tag + "_" + load_profile_name
            lxc_container = YANDEX_TANKAPI_LXC_CONTAINER.find(state=State.READY).order(-YANDEX_TANKAPI_LXC_CONTAINER.id).first().id
            logger.info("Found a YANDEX_TANKAPI_LXC_CONTAINER, id={}, starting shooting \"{}\"...".format(str(lxc_container), shooting_name))

            config_content = self._make_config_content(target_url, shooting_name, self.Context.ammo[ammo_type], self.Context.load_profile[load_profile_name])
            shooting_task = ShootViaTankapi(
                self,
                description="Shooting to {} target {}".format(shooting_name, target_url),
                use_public_tanks=True,
                nanny_service=self.Context.nanny_service,
                ammo_source="in_config",
                config_source="file",
                config_content=config_content,
                container=lxc_container,
            ).enqueue()
            logger.info("Started shooting task id={}".format(str(shooting_task.id)))
            self.Context.shooting[shooting_name] = shooting_task.id

            raise sdk2.WaitTask(shooting_task.id, Status.Group.FINISH | Status.Group.BREAK, wait_all=True, timeout=14400)

    def _save_info_attrs(self, service_id, info_attrs, comment):
        info_attrs["snapshot_id"] = info_attrs["_id"]
        info_attrs.pop("_id")
        info_attrs["comment"] = comment
        self._nanny.set_service_info_attrs(service_id, info_attrs)

    def _select_policy(self, policy):
        info_attrs = self._nanny.get_service_info_attrs(self.Context.nanny_service)
        old_policy = info_attrs["content"]["scheduling_policy"]
        info_attrs["content"]["scheduling_policy"] = policy
        self._save_info_attrs(self.Context.nanny_service, info_attrs, "Set scheduling policy {}".format(policy["type"]))
        return old_policy

    def _get_stable_release_tag(self):
        if self.Parameters.stable_release_tag != "auto":
            return self.Parameters.stable_release_tag
        target_state = self._nanny.get_service_target_state(self.Context.nanny_service)
        tag_re = re.compile(r"(\d+-\d+)")
        for ss in target_state["content"]["snapshots"]:
            if self.Parameters.test_release_tag not in ss["snapshot_info"]["comment"]:
                match = tag_re.search(ss["snapshot_info"]["comment"])
                if match:
                    return match.group(1)
        return None

    def _select_snapshot(self, release_tag, stage_name, snapshot_id=""):
        with self.memoize_stage[stage_name]:
            logger.info("Selecting nanny snapshot by tag: {}".format(release_tag))
            nanny_client = self._nanny
            service_id = self.Context.nanny_service
            target_state = nanny_client.get_service_target_state(service_id)
            logger.info("service_target_state: {}".format(target_state))
            initial_snapshot_id = target_state["content"]["snapshot_id"]

            is_right_snapshot_selected = False
            if snapshot_id:
                is_right_snapshot_selected = initial_snapshot_id == snapshot_id
            else:
                is_right_snapshot_selected = release_tag in target_state["content"]["snapshot_info"]["comment"]
                if is_right_snapshot_selected:
                    snapshot_id = target_state["content"]["snapshot_id"]
                else:
                    for ss in target_state["content"]["snapshots"]:
                        if release_tag in ss["snapshot_info"]["comment"]:
                            snapshot_id = ss["snapshot_id"]
                            break
                    if not snapshot_id:
                        raise errors.TaskFailure("Failed to find snapshot with tag {} at nanny {}".format(release_tag, service_id))

            if is_right_snapshot_selected:
                logger.info("No need to switch snapshot")
            else:
                nanny_client.set_snapshot_state(service_id, snapshot_id=snapshot_id, state="ACTIVE", comment="Perf testing " + release_tag, recipe="default")

            logger.info("Waiting for snapshot {} to activate".format(snapshot_id))
            activation_timeout = 300
            waitfor = time.time() + activation_timeout
            current_state = {}
            while time.time() < waitfor:
                current_state = nanny_client.get_service_current_state(service_id)
                if current_state["content"]["summary"]["value"] == "ONLINE":
                    for snapshot in current_state["content"]["active_snapshots"]:
                        if snapshot["snapshot_id"] == snapshot_id and snapshot["state"] == "ACTIVE":
                            logger.info("Snapshot successfully switched")
                            return initial_snapshot_id
                time.sleep(5)

            raise errors.TaskFailure("Failed to activate in {} seconds, last state: {}".format(activation_timeout, current_state))

    def _determine_target_url(self):
        import nanny_rpc_client
        from infra.nanny.yp_lite_api.proto import pod_sets_api_pb2
        from infra.nanny.yp_lite_api.py_stubs import pod_sets_api_stub

        client = nanny_rpc_client.RetryingRpcClient(rpc_url='https://yp-lite-ui.nanny.yandex-team.ru/api/yplite/pod-sets/',
                                                    oauth_token=sdk2.Vault.data("skillrec-nanny-oauth"))
        stub = pod_sets_api_stub.YpLiteUIPodSetsServiceStub(client)
        req = pod_sets_api_pb2.ListPodsRequest()
        req.service_id = self.Context.nanny_service
        req.cluster = self.Parameters.testing_target_dc.upper()
        reply = stub.list_pods(req)
        if not reply or len(reply.pods) < 1:
            raise errors.TaskFailure("Failed to find a pod in {}".format(req.service_id))
        url = reply.pods[0].status.dns.persistent_fqdn
        logger.info("Found a pod for target_url: {}".format(url))
        return url

    def _find_shooting_result(self, release_tag, load_profile_name):
        shooting_name = release_tag + "_" + load_profile_name
        logger.info("Searching for shooting result by name={}".format(shooting_name))
        shooting_task_id = self.Context.shooting[shooting_name]
        shooting_result = sdk2.Task.find(
            id=shooting_task_id,
            children=True
        ).first()
        logger.info("Shooting result found, id={}".format(str(shooting_result.id)))
        if shooting_result.status not in Status.Group.SUCCEED:
            raise errors.TaskError("Child task did not succeed, id={}".format(str(shooting_result.id)))
        return shooting_result

    def _make_config_content(self, target_url, tag, ammo_url, load_profile):
        config_template = """
bfg:
    package: yandextank.plugins.Bfg
console:
    enabled: false
neuploader:
    api_address: "https://back.luna.yandex-team.ru"
    db_name: luna
    enabled: true
    meta:
        tankapi_host: sas1-0021-all-rcloud-tanks-30169.gencfg-c.yandex.net
        tankapi_port: 30169
    package: yandextank.plugins.NeUploader
phantom:
    address: {target_url}
    ammofile: "{ammo_url}"
    cache_dir: /place/db/www/logs/yandex-tank/tankapi/tests/stpd-cache
    load_profile:
        load_type: rps
        schedule: "{load_profile}"
    package: yandextank.plugins.Phantom
    uris: []
telegraf:
    package: yandextank.plugins.Telegraf
uploader:
    enabled: true
    job_name: {tag}
    meta:
        use_tank: "nanny:production_yandex_tank"
    operator: lunapark
    package: yandextank.plugins.DataUploader
    task: {startrek_ticket_id}
    ver: "1"
        """
        return config_template.format(
            target_url=target_url,
            tag=tag,
            ammo_url=ammo_url,
            load_profile=load_profile,
            startrek_ticket_id=self.Parameters.startrek_ticket_id,
        )
