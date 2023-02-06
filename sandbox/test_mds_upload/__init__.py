import hashlib
import requests
import json
import logging
import os.path
import random
import shutil
import string

from sandbox.common import errors as common_errors
from sandbox.common.types import task as ctt

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp

from sandbox.projects.common.arcadia import sdk as arcadia_sdk


class TestMdsUpload(sdk2.Task):
    """
    Task to test uploading to MDS in sandbox acceptance.
    Builds tool `upload` and then runs it to upload generated file to PRESTABLE sandbox.
    """
    __PRESTABLE_URL = "https://www-sandbox1.n.yandex-team.ru"
    __PRESTABLE_PROXY_URL = "http://sandbox-preprod08.search.yandex.net"

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 1024
        disk_space = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    def on_execute(self):
        with self.memoize_stage.test_upload:
            upload_binary = self.build_binary()
            metadata = self.test_upload(upload_binary)
            self.Context.upload_task_id = metadata["task"]["id"]
            raise sdk2.WaitTask(self.Context.upload_task_id, ctt.Status.Group.FINISH)

        task = sdk2.Task[self.Context.upload_task_id]
        if task.status != ctt.Status.SUCCESS:
            raise common_errors.TaskFailure("Task MDS_UPLOAD #{} finished with status {}".format(task.id, task.status))

    def build_binary(self):
        with arcadia_sdk.mount_arc_path("arcadia-arc:/#trunk") as path:
            upload_tool_path = os.path.join(path, "sandbox/scripts/tools/upload")
            ya_path = os.path.join(path, "ya")
            return_code = sp.call([ya_path, "make", upload_tool_path])
            if return_code != 0:
                raise common_errors.TaskFailure("Building upload tool failed, return code = {}".format(return_code))
            logging.info("Built upload tool successfully")
            binary_path = str(self.path("upload"))
            shutil.copyfile(os.path.join(upload_tool_path, "upload"), binary_path)
            os.chmod(binary_path, 0o755)
        return binary_path

    def test_upload(self, upload_binary):
        tmp_file = os.path.join("/tmp", "tmp_" + TestMdsUpload.random_word(6))
        data = TestMdsUpload.random_word(20)
        md5_original = hashlib.md5()
        md5_original.update(data)
        with open(tmp_file, "w") as f:
            f.write(data)
        logging.info("Temp file written to {}, original hash {}".format(tmp_file, md5_original.hexdigest()))

        logging.info("Running upload tool {}".format(upload_binary))

        meta_filename = "out.txt"

        cmd = [
            upload_binary,
            "--url={}".format(self.__PRESTABLE_URL),
            "--proxy-url={}".format(self.__PRESTABLE_PROXY_URL),
            "--owner={}".format(self.owner),
            "--mds",
            "--oauth-token=-",  # means reading value from env
            "--dump={}".format(meta_filename),
            tmp_file
        ]
        oauth_token = self.server.task_token
        try:
            output = sp.check_output(cmd, env={"OAUTH_TOKEN": oauth_token}, stderr=sp.STDOUT)
        except sp.CalledProcessError as exc:
            logging.error("Command returned with non-zero exit code %d:\n%s", exc.returncode, exc.output)
            raise common_errors.TaskFailure("Upload failed, see logs for details.\n{}".format(exc.output))
        logging.info("Upload output:\n" + output)

        with open(meta_filename, "r") as meta_file:
            metadata_json = meta_file.read()
            logging.info("Uploaded resource metadata:\n{}".format(metadata_json))

            metadata = json.loads(metadata_json)
            http_proxy_link = metadata.get("http", {}).get("proxy")
            if not http_proxy_link:
                raise common_errors.TaskFailure("Metadata doesn't contain ['http']['proxy']")
            link = "{}/{}".format(http_proxy_link, os.path.basename(tmp_file))
            response = requests.get(link)
            msg = "Status code {}, content '{}'".format(response.status_code, response.content)
            if not response.ok:
                raise common_errors.TaskFailure("Bad response from proxy:\n" + msg)
            logging.info("Proxy response:\n" + msg)

            md5_uploaded = hashlib.md5()
            md5_uploaded.update(response.content)
            if str(md5_original.hexdigest()) != str(md5_uploaded.hexdigest()):
                raise common_errors.TaskFailure(
                    "MD5 hashes of the original and downloaded files differ: {} != {}".format(
                        md5_original.hexdigest(),
                        md5_uploaded.hexdigest()
                    )
                )
        return metadata

    @staticmethod
    def random_word(length):
        random.seed()
        return "".join(random.choice(string.ascii_letters) for _ in range(length))
