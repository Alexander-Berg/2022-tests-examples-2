import os
import sys
import json
import copy
import random
import struct
import urllib
import hashlib
import logging
import tarfile
import getpass
import urlparse
import contextlib
import datetime as dt
import threading as th
import subprocess as sp

import py
import pytest
import requests

from sandbox import common
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt


class TestUpload:
    # Perform upload via subprocess (using downloaded library) or in scope of the current process.
    SUBPROCESS_UPLOAD = True

    @staticmethod
    def debug(msg):
        print(msg)

    @staticmethod
    def do_upload(_, files, url, token, username, rtype, description, attributes):
        def handle_files(files):
            for fname in files:
                fh = fname.open('rb')
                fh.seek(0, os.SEEK_END)
                yield common.upload.HTTPHandle.FileMeta(fh, fh.tell(), "files/" + fname.basename)
                fh.seek(0)

        h = common.upload.HTTPHandle(
            common.upload.HTTPHandle.ResourceMeta(
                rtype, ctm.OSFamily.ANY, username, description, attributes, release_to_yd=False
            ),
            common.proxy.OAuth(token),
            url,
            30,
            *handle_files(files)
        )
        _U = ctm.Upload
        state, last_state, last_state_copy = (None, ) * 3

        ret = None
        for state in h():
            if last_state != state:  # Last operation stopped.
                if isinstance(last_state, _U.Check):
                    print(
                        "{} file(s) found totally for {}.".format(last_state.amount, last_state.size)
                    )
            else:  # Operation continues.
                if isinstance(state, _U.Prepare):
                    if last_state_copy.task_id != state.task_id:
                        link = "{}/task/{}/view".format(url, state.task_id)
                        print("Task #{} created: {}".format(state.task_id, link))
                    if last_state_copy.resource_id != state.resource_id:
                        ret = state.resource_id
                        link = "{}/resource/{}/view".format(url, state.resource_id)
                        print("Resource #{} registered: {}".format(state.resource_id, link))
                if isinstance(state, _U.Share):
                    print("Task currently is in '{}' state.".format(state.task_state))

            if last_state != state:  # Start new operation report.
                if isinstance(state, _U.Check):
                    print("Calculating total files size")
                if isinstance(state, _U.Prepare):
                    print("Preparing upload task")
                if isinstance(state, _U.Share):
                    print("Sharing uploaded data")

            last_state = state
            last_state_copy = copy.deepcopy(state)

        if isinstance(state, _U.Share):
            print("Task currently is in '{}' state.".format(state.task_state))
            msg = ''
            if state.skynet_id:
                msg = "Skybone ID is {}".format(state.skynet_id)
            if state.md5sum:
                if msg:
                    msg += ", "
                msg += "MD5 checksum is {}".format(state.md5sum)
            if msg:
                print(msg)
        return ret

    @classmethod
    def do_subprocess_upload(cls, libpath, files, *args):
        cmd = list(common.utils.chain(sys.executable, __file__, ":".join([_.strpath for _ in files]), args))
        cls.debug("Subprocess arguments: {!r}".format(cmd))
        p = sp.Popen(cmd, env={"PYTHONPATH": ":".join(["/skynet", libpath.strpath])}, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = p.communicate()
        hr = lambda l: "".join(["-" * 40, l, "-" * 40])
        if p.returncode:
            pytest.fail("Upload script failed with code {}:\n{}\n{}\n{}\n{}".format(
                p.returncode, hr("STDERR"), stderr, hr("STDOUT"), stdout
            ))
        cls.debug("Subprocess STDOUT:\n{}".format(stdout))
        return int(stdout.rstrip().split(os.linesep)[-1])

    @staticmethod
    def _client_loop(stop_event, api_su_session, client_node_id, timeout, task_state_switcher):
        import bin.client
        from sandbox.services.modules import tasks_enqueuer

        bin.client.UNPRIVILEGED_USER = bin.client.SERVICE_USER = bin.client.User(
            getpass.getuser(), os.path.expanduser("~" + getpass.getuser())
        )
        session = common.proxy.Session(api_su_session.transport.auth.token, None)
        bin.client.PingSandboxServerThread()._session = session
        bin.client.PingSandboxServerThread().storage_device_type = False
        bin.client.PingSandboxServerThread().remote = common.proxy.ReliableServerProxy(
            api_su_session.url, auth=session
        )
        bin.client.PingSandboxServerThread().command = None

        te_th = tasks_enqueuer.TasksEnqueuer()

        bin.client.PingSandboxServerThread().remote.client_started(client_node_id)
        start = dt.datetime.now()
        while not stop_event.is_set():
            now = dt.datetime.now()
            if (now - start).total_seconds() > timeout:
                pytest.fail('Watchdog timeout. Start time was: {}, current is: {}.'.format(
                    start, now
                ))
            assert bin.client.PingSandboxServerThread().make_ping(
                node_id=client_node_id,
                max_tick=100000,
                free_space_threshold=1000000000,
                sleep_time=.025,
                idle=0,
            )
            task_state_switcher.tick()
            te_th.tick()

    @pytest.mark.xfail(run=False)
    def test_upload_basic(
        self,
        server, api_su_session, api_session_login, rest_session, client, client_node_id, serviceq, tmpdir
    ):
        import common.config

        tmpdir = py.path.local(tmpdir)
        files = []
        chksums = []
        for _ in xrange(2):
            tmpfile = tmpdir.join(hex(random.randint(0, 0x10000)))
            tmpfile.write(struct.pack("100000I", *random.sample(xrange(0x100000000), 100000)), "wb")
            chksums.append(hashlib.sha1(tmpfile.read("rb")).hexdigest())
            self.debug("Tempfile {}, SHA1: {}".format(tmpfile.strpath, chksums[-1]))
            files.append(tmpfile)

        libdir = tmpdir.join("library")
        libdir.ensure(dir=1)
        with contextlib.closing(requests.get(
            "http://proxy.sandbox.yandex-team.ru/last/SANDBOX_ARCHIVE?attrs=" + urllib.quote(json.dumps({
                "released": "stable", "type": "library"
            })),
            stream=True,
        )) as r:
            with tarfile.open(None, "r|*", r.raw) as tar:
                tar.extractall(libdir.strpath)
        self.debug("Library extracted at {!r}".format(libdir.strpath))

        stop_event = th.Event()
        client = th.Thread(
            target=self._client_loop,
            args=(stop_event, api_su_session, client_node_id, 30)
        )
        client.start()

        descr = "Test upload " + hex(random.randint(0, 0x10000))
        attrs = {"version": hex(random.randint(0, 0x10000)), "revision": hex(random.randint(0, 0x10000))}
        url = list(urlparse.urlparse(server.url))
        url[2] = ""  # Reset URL path
        self.debug("Server URL: {!r}".format(url))
        try:
            resource_id = (self.do_upload if not self.SUBPROCESS_UPLOAD else self.do_subprocess_upload)(
                libdir, files, urlparse.urlunparse(url), server.transport.auth.token, api_session_login,
                "TEST_TASK_RESOURCE_2", descr, ",".join(map("=".join, attrs.iteritems()))
            )
        finally:
            stop_event.set()
            client.join()
        resource = rest_session.resource[resource_id][:]
        assert resource["description"] == descr
        assert resource["file_name"] == "files"
        assert resource["type"] == "TEST_TASK_RESOURCE_2"
        assert "backup_task" in resource["attributes"]
        for k, v in attrs.iteritems():
            assert resource["attributes"][k] == v

        dstdir = py.path.local(common.config.Registry().client.tasks.data_dir).join(*common.utils.chain(
            ctt.relpath(resource["task"]["id"]),
            resource["file_name"]
        ))

        for i, srcf in enumerate(files):
            dstf = dstdir.join(srcf.basename)
            assert chksums[i] == hashlib.sha1(dstf.read()).hexdigest()
            assert srcf.size() == dstf.size()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    resource_id = TestUpload.do_upload("", map(py.path.local, sys.argv[1].split(":")), *sys.argv[2:])
    print str(resource_id)
