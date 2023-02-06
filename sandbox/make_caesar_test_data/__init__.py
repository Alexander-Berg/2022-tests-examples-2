# -*- coding: utf-8 -*-

import logging
import os
import re
import subprocess

import sandbox.projects.resource_types as rt
from sandbox import sdk2
from sandbox.projects.bsyeti.common import get_yt_token_path
from sandbox.projects.common import vcs

DEFAULT_BRANCH = "trunk"
TESTS_DIR = "ads/bsyeti/caesar/tests/b2b/diff_test"
SECRET_PATH = "sec-01ectkqh09zcgzn0h7p0zpqtag"
SECRET_YT_TOKEN = "yt_token"
SECRET_TVM_SECRECT_KEY = "resharder_tvm_secret"
SECRET_TVM_ID = "resharder_tvm_id"

SAMPLER_ARCADIA_PATH = "ads/bsyeti/caesar/tools/logtests/sampler"
REVIEW_BRANCH = "update-caesar-b2b-tests"
# TODO: determine by token
ROBOT_NAME = "robot-srch-releaser"
SAMPLER_RESOURCE_TAG = "LOG SAMPLES"
RESOURCE_FILE_PATH = "ads/bsyeti/caesar/tests/lib/b2b/ya.make.inc"

USE_SAMPLER_RESOURCE = False


class MakeCaesarSamplerBin(rt.ARCADIA_PROJECT):
    """
    resource with sampler bin
    """


def update_ya_make(path, tag, new_val):
    with open(path) as f:
        data = f.read().split("\n")

    cnt = 0
    for idx, row in enumerate(data):
        if tag in row:
            spaces = data[idx + 1].index(data[idx + 1].strip())
            data[idx + 1] = " " * spaces + new_val
            with open(path, "w") as f:
                f.write("\n".join(data))
            cnt += 1
    if not cnt:
        raise RuntimeError("tag not found")


def build(arc_path, target):
    ya = os.path.join(arc_path, "ya")
    sampler_path = os.path.join(arc_path, target)
    subprocess.check_call([ya, "make", sampler_path, "--yt-token-path", get_yt_token_path()])
    return os.path.join(sampler_path, "sampler")


def get_sampler_path(arc, arc_path):
    # for debug only
    if USE_SAMPLER_RESOURCE:
        resource = sdk2.Resource[2581333975]
        data = sdk2.ResourceData(resource)
        return str(data.path)
    return build(arc_path, SAMPLER_ARCADIA_PATH)


def get_source_lists(sampler_path):
    output = subprocess.check_output([sampler_path, "show_sources"]).decode()
    keys = "LogBroker", "YtQueue", "YtDirectory"
    res = {}
    for row in output.split("\n"):
        for key in keys:
            prefix = "{} : ".format(key)
            if row.startswith(prefix):
                res[key] = row[len(prefix) :].split()
    return res


def parse_resource_id(output):
    return re.search("resource_id is sbr://([0-9]+)", output).groups()[0]


def _check_tests(arc_path, ya, path):
    # check that current tests are ok
    subprocess.check_call(
        [
            ya,
            "make",
            "-rA",
            "--yt-token-path", get_yt_token_path(),
            os.path.join(arc_path, path),
        ]
    )


def _canonize_tests(arc_path, ya, path):
    subprocess.check_call(
        [
            ya,
            "make",
            "-rAZ",
            "--yt-token-path", get_yt_token_path(),
            os.path.join(arc_path, path),
        ]
    )


def _make_pr(arc, arc_path, author, branch, message):
    arc.commit(arc_path, message, all_changes=True)
    arc.push(
        arc_path,
        upstream="users/{}/{}".format(author, branch),
        force=True,
    )
    try:
        arc.pr_create(arc_path, message=message, publish=True, auto=True)
    except vcs.arc.ArcCommandFailed as exc:
        # unfortunately sdk does not provide a better way of handling it
        if "already exists" not in exc.args[0]:
            raise


def _update_logbroker(sampler_path, ya, secret, env, sources, base_resource):
    proc = subprocess.Popen(
        [sampler_path]
        + ["--no-perm-check"]
        + ["--yapath", ya]
        + ["update_source"]
        + ["--dev-key", "7"]
        + sources
        + ["--allow-empty"]
        + ["--tvm-id", secret[SECRET_TVM_ID]]
        + ["--update-now"]
        + ["--base-resource", str(base_resource)]
        + ["--no-check"],
        env=env,
        stderr=subprocess.PIPE,
    )
    output = []
    for row in proc.stderr:
        output.append(row.decode())
    output = "\n".join(output)
    proc.wait()
    logging.info("output %s", output)
    assert proc.returncode == 0
    resource_id = parse_resource_id(output)
    return resource_id


# copy-pasted to avoid dependencies :(
def get_resource_by_tag(content, tag):
    lines = [line.strip() for line in content.split("\n")]
    for idx, val in enumerate(lines):
        if tag in val:
            assert val[0] == "#"
            val = lines[idx + 1]
            prefix = "sbr://"
            assert val.startswith(prefix)
            return int(val[len(prefix) :])
    raise RuntimeError("failed to find the resource")


def _update_yt_and_qyt(sampler_path, ya, secret, env, sources, base_resource):
    proc = subprocess.Popen(
        [sampler_path]
        + ["--yapath", ya]
        + ["update_source"]
        + ["--dev-key", "7"]
        + sources
        + ["--allow-empty"]
        + ["--base-resource", str(base_resource)]
        + ["--update-now"]
        + ["--no-check"],
        env=env,
        stderr=subprocess.PIPE,
    )
    output = []
    for row in proc.stderr:
        output.append(row.decode())
    output = "\n".join(output)
    proc.wait()
    logging.info("output %s", output)
    assert proc.returncode == 0
    resource_id = parse_resource_id(output)
    return resource_id


class MakeCaesarTestData(sdk2.Task):
    """
    task to make test data for caesaer testing
    """

    class Requirements(sdk2.Requirements):
        ram = 16 * 1024
        cores = 4
        privileged = False

        class Caches(sdk2.Requirements.Caches):
            pass

    def on_execute(self):
        secret = sdk2.yav.Secret(SECRET_PATH).data()
        env = {
            "YT_TOKEN": secret[SECRET_YT_TOKEN],
            "TVM_SECRET": secret[SECRET_TVM_SECRECT_KEY],
        }
        arc = vcs.arc.Arc()
        with arc.mount_path("", changeset="trunk", fetch_all=False) as arc_path:
            sampler_path = get_sampler_path(arc, arc_path)
            logging.info("sampler_path %s", sampler_path)
            source_lists = get_source_lists(sampler_path)
            logging.info("source_lists %s", source_lists)
            ya = os.path.join(arc_path, "ya")
            env["YA_TOKEN"] = os.environ["ARC_TOKEN"]
            yamake_path = os.path.join(arc_path, RESOURCE_FILE_PATH)
            with open(yamake_path) as yamake:
                resource_id = get_resource_by_tag(yamake.read(), SAMPLER_RESOURCE_TAG)

            resource_id = _update_logbroker(
                sampler_path,
                ya,
                secret,
                env,
                source_lists["LogBroker"],
                base_resource=resource_id,
            )
            resource_id = _update_yt_and_qyt(
                sampler_path,
                ya,
                secret,
                env,
                source_lists["YtDirectory"] + source_lists["YtQueue"],
                base_resource=resource_id,
            )

            arc.checkout(arc_path, branch=REVIEW_BRANCH, create_branch=True, force=True)

            _check_tests(arc_path, ya, TESTS_DIR)
            update_ya_make(
                yamake_path, SAMPLER_RESOURCE_TAG, "sbr://{}".format(resource_id)
            )
            _make_pr(
                arc,
                arc_path,
                author=(self.author if self.author == self.owner else ROBOT_NAME),
                branch=REVIEW_BRANCH,
                message="tests: updated b2b tests data. BIGB-1572",
            )
