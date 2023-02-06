import os
import time
import base64
import random
import shutil
import tarfile
import httplib
import datetime as dt
import itertools as it

import py
import mock
import pytest
import requests

from sandbox import sdk2
from sandbox.sdk2 import internal as sdk2_internal
from sandbox import common
from sandbox.fileserver import fileserver as fileserver_module


@pytest.fixture()
def fileserver_url(fileserver_port):
    return "http://localhost:{}/".format(fileserver_port)


@pytest.fixture()
def directory_for_listing(tasks_dir):
    name = "directory"
    full_path = os.path.join(tasks_dir, name)
    os.mkdir(full_path)
    yield full_path
    shutil.rmtree(full_path)


@pytest.mark.usefixtures("fileserver")
class TestFileServer(object):
    @pytest.mark.xfail(run=False)  # FIXME: SANDBOX-5196
    def test__fileserver_too_many_requests(self, request, tasks_dir, fileserver_url):
        file_name = "test"
        py.path.local(tasks_dir).join(file_name).write("X" * 0x7FFFFF)  # Twice the bufsize from fileserver
        file_url = fileserver_url + file_name

        # Save requests to a list to prevent them from being garbage collected during the loop
        # Close all requests in the end, otherwise fileserver won't be able to shutdown in case of test failure
        rs = []
        request.addfinalizer(lambda: [r.close() for r in rs])

        for _ in range(32):  # Default `max_requests_in_progress` for fileserver
            r = requests.get(file_url + "?stream=tar", stream=True)
            r.raise_for_status()
            rs.append(r)

        r = requests.get(file_url)
        assert r.status_code == httplib.SERVICE_UNAVAILABLE

        # Close all requests and poke fileserver until it responds OK
        for _ in rs:
            _.close()

        now = time.time()
        while time.time() - now < 10:  # Wait for 10 seconds max
            r = requests.get(file_url)
            if r.status_code == httplib.OK:
                break
        else:
            raise Exception("Fileserver failed to respond in time after request flood")

    def test__fileserver(self, tasks_dir, fileserver_url):
        file_name = "file_name"
        text = []
        for _ in xrange(random.randrange(50, 100)):
            text.append(chr(random.randint(0, 127)))
        text = base64.b64encode("".join(text))
        text_len = len(text)
        py.path.local(tasks_dir).join(file_name).write(text)
        file_url = fileserver_url + file_name

        resp = requests.get(file_url)
        assert resp.status_code == httplib.OK
        assert text == resp.text

        resp = requests.get(file_url, headers={"Range": "bytes=0-{}".format(text_len * 2)})
        assert resp.status_code == httplib.OK
        assert text == resp.text

        resp = requests.get(file_url, headers={"Range": "bytes=-0"})
        assert resp.status_code == httplib.REQUESTED_RANGE_NOT_SATISFIABLE
        resp = requests.get(file_url, headers={"Range": "bytes={}-".format(text_len + 1)})
        assert resp.status_code == httplib.REQUESTED_RANGE_NOT_SATISFIABLE

        start, chunk_size = 0, 50
        contents = []
        while start < text_len:
            resp = requests.get(file_url, headers={"Range": "bytes={}-{}".format(start, start + chunk_size - 1)})
            assert resp.status_code == httplib.PARTIAL_CONTENT
            start += chunk_size
            contents.append(resp.text)
        assert text == "".join(contents)

    def test__fileserver_json_api(self, tasks_dir, fileserver_url, directory_for_listing):
        dir_name = os.path.basename(directory_for_listing)
        file_1_name = "file_1.txt"
        file_1_data = "data"
        link_1_name = "link_1"
        link_2_name = "link_2"
        archive_name = "archive.tar"

        py.path.local(directory_for_listing).join(file_1_name).write_binary(file_1_data)
        os.symlink(os.path.join(directory_for_listing, file_1_name), os.path.join(directory_for_listing, link_1_name))
        os.symlink(os.path.join(directory_for_listing, link_1_name), os.path.join(directory_for_listing, link_2_name))
        archive = tarfile.open(os.path.join(directory_for_listing, archive_name), "w:gz")
        archive.add(os.path.join(directory_for_listing, file_1_name), arcname=file_1_name)
        archive.close()
        dir_url = fileserver_url + dir_name

        response = requests.get(dir_url, headers={"Accept": "application/json; charset=utf-8"})
        assert response.status_code == httplib.OK
        json_response = response.json()
        for value in json_response.values():
            assert "time" in value
            assert "created" in value["time"]
            assert "modified" in value["time"]
            value.pop("time")
            if value["type"] == fileserver_module.FileServerHandler.FileInfo.Type.ARCHIVE:
                assert "size" in value
                value.pop("size")

        assert json_response == {
            file_1_name: {
                "type": fileserver_module.FileServerHandler.FileInfo.Type.REGULAR,
                "path": os.path.join(os.sep, dir_name, file_1_name),
                "url": os.path.join(dir_url, file_1_name),
                "size": len(file_1_data),
            },
            link_1_name: {
                "type": fileserver_module.FileServerHandler.FileInfo.Type.LINK,
                "path": os.path.join(os.sep, dir_name, link_1_name),
                "url": os.path.join(dir_url, link_1_name),
                "size": len(file_1_data),
                "target": os.path.join(directory_for_listing, file_1_name),
            },
            link_2_name: {
                "type": fileserver_module.FileServerHandler.FileInfo.Type.LINK,
                "path": os.path.join(os.sep, dir_name, link_2_name),
                "url": os.path.join(dir_url, link_2_name),
                "size": len(file_1_data),
                "target": os.path.join(directory_for_listing, link_1_name),
            },
            archive_name: {
                "type": fileserver_module.FileServerHandler.FileInfo.Type.ARCHIVE,
                "path": os.path.join(os.sep, dir_name, archive_name),
                "url": os.path.join(dir_url, archive_name),
            }
        }

        response = requests.get(
            "{}/{}/".format(dir_url, archive_name),
            headers={"Accept": "application/json; charset=utf-8"}
        )
        assert response.status_code == httplib.OK
        json_response = response.json()
        for value in json_response.values():
            assert "time" in value
            assert "created" in value["time"]
            assert "modified" in value["time"]
            value.pop("time")
        assert json_response == {
            file_1_name: {
                "type": fileserver_module.FileServerHandler.FileInfo.Type.REGULAR,
                "path": os.path.join(os.sep, dir_name, archive_name, file_1_name),
                "url": os.path.join(dir_url, archive_name, file_1_name),
                "size": len(file_1_data),
            }
        }


class TestLogCache(object):
    TEST_CONTENT = "mary had a little lamb\n"

    def test__logcache(self, tmpdir):
        log_path = os.path.join(tmpdir, "test__logcache.log")
        complex_line = [
            "its fleece was white as snow\n",
            "and everywhere that mary went\n",
            "the lamb was\n",
            "\n",
            "sure to 2017-05-16 13:18:28,200 ( 86400.000s) ERROR\n",
            "go\n"
        ]
        with open(log_path, "w") as log:
            log.write("2017-05-15 13:18:28,200 (     0.000s) DEBUG  (executor)       {}".format(self.TEST_CONTENT))
            log.flush()

        first = {
            "no": 0,
            "time": "2017-05-15 13:18:28,200",
            "level": "DEBUG",
            "component": "executor",
            "content": self.TEST_CONTENT.strip()
        }
        assert fileserver_module.LogCache.get(log_path, 0) == [first]
        for n in (1, 10, 100):
            assert not fileserver_module.LogCache.get(log_path, n)

        with open(log_path, "a") as log:
            log.write("".join(
                ["2017-05-16 13:18:28,200 ( 86400.000s) ERROR  (something_else) {}".format(complex_line[0])] +
                complex_line[1:]
            ))
            log.flush()

        second = {
            "no": 1,
            "time": "2017-05-16 13:18:28,200",
            "level": "ERROR",
            "component": "something_else",
            "content": "".join(complex_line).strip()
        }

        for n in (None, 0):
            assert fileserver_module.LogCache.get(log_path, n) == [first, second]

        # there's 101 line in total in the log after this
        open(log_path, "a").write("".join(["2017-05-17 13:18:28,200 ( 86400.000s) INFO  (__init__) idk\n"] * 99))
        tail = fileserver_module.LogCache.get(log_path, None)
        assert tail == fileserver_module.LogCache.get(log_path, 1) and len(tail) == 100, \
            fileserver_module.LogCache._LogCache__cache

        prefix = "2017-05-17 13:18:28,200 ERROR (xxx)\n"
        contents = [
            [
                "rooms were made for carpets",
                "towers made for spires",
                "ships were made for cannonade fire off from inside them\n"
            ],
            [
                "a9e6c14cd1721fbb\n",
                "abcdefjkflkwfjlwnfj\n"
            ]
        ]
        log_path_2 = os.path.join(tmpdir, "test__logcache_2.log")
        with open(log_path_2, "w") as log2:
            for cc in contents:
                log2.write(prefix + "\n".join(cc))

        data = fileserver_module.LogCache.get(log_path_2, 0)
        assert len(data) == 2
        for i in xrange(len(data)):
            assert data[i]["content"] == "\n".join(contents[i]).strip()

    def test__caching_ability(self, tmpdir):
        log_path = os.path.join(tmpdir, "test__caching_ability.log")
        line = "2017-05-15 13:18:28,200 (     0.000s) DEBUG  (executor)       {}".format(self.TEST_CONTENT)

        def fill_cache(lc):
            return fileserver_module.LogCache.Entry(os.path.getsize(log_path), [len(line) * j for j in xrange(lc)])

        with open(log_path, "w") as log:
            for _ in xrange(10):
                log.write(line)

        patch_obj = "fileserver.fileserver.LogCache._refresh"
        patch_dict = "fileserver.fileserver.LogCache._LogCache__cache"
        with mock.patch.dict(patch_dict, {log_path: fill_cache(10)}):
            with mock.patch(patch_obj) as wrapped:
                for i in xrange(10):
                    data = fileserver_module.LogCache.get(log_path, i)
                    expected_len = 10 if not i else 10 - i
                    assert len(data) == expected_len
                wrapped.assert_called_once()
            with mock.patch(patch_obj) as wrapped:
                data = fileserver_module.LogCache.get(log_path, 100)
                assert not data
                wrapped.assert_called()

        with open(log_path, "a") as log:
            log.write("2007-01-01 03:18:20,200 (     0.000s) ERROR  (some_component) a completely different line\n")

        with mock.patch.dict(patch_dict, {log_path: fill_cache(11)}):
            with mock.patch(patch_obj) as wrapped:
                assert fileserver_module.LogCache.get(log_path, 1)
                wrapped.assert_called()
            with mock.patch(patch_obj) as wrapped:
                for i in it.chain(xrange(0, 10), (None,)):  # LogCache.get(11) = []
                    assert fileserver_module.LogCache.get(log_path, i)
                wrapped.assert_not_called()

    def test__partial_read(self, tmpdir):
        log_path = os.path.join(tmpdir, "test__partial_read.log")
        date, rest = "2017-05-17 13:18:28,200", "( 86400.000s) INFO  (__init__) blah\n"
        line, chunk_sz = "{} {}".format(date, rest), 10
        with open(log_path, "w") as log:
            for lc in xrange(1, 11):
                offset = 0
                while offset < len(line):
                    log.write(line[offset: offset + chunk_sz])
                    log.flush()
                    offset += chunk_sz
                    fileserver_module.LogCache.get(log_path, 0)
                data = fileserver_module.LogCache.get(log_path, 0)
                assert all(_["content"] == "blah" for _ in data)
                assert len(data) == lc, "Failed to read {} lines fully".format(lc)

    def test__first_lines_without_date(self, tmpdir):
        log_path = os.path.join(tmpdir, "test__first_line_without_date.log")
        incorrect = [
            "nonsense\n",
            "asdfg 2017-01-01 12:34:56,789\n",
        ]
        content = [
            "No local virtual environment found.\n",
            "Do you want to update environment([y]/n)?\n"
        ]
        correct = [
            "2017-05-15 13:18:28,200 (     0.000s) DEBUG  (executor) {}".format(content[0]),
            "2000-01-01 13:18:28,200 (     0.000s) DEBUG  (something_new) {}".format(content[1]),
        ]

        with open(log_path, "w") as log:
            for i in xrange(len(incorrect)):
                log.write(incorrect[i])
                log.flush()
                data = fileserver_module.LogCache.get(log_path, 0)
                assert len(data) == 1 and data[0]["content"] == "".join(incorrect[:i + 1]).strip()
                assert all(data[0][k] is None for k in ("time", "component", "level"))

            for i in xrange(len(correct)):
                log.write(correct[i])
                log.flush()

                data = fileserver_module.LogCache.get(log_path, 0)
                assert len(data) == 1 + (i + 1)
                assert data[i + 1]["content"] == content[i].strip()


@pytest.mark.usefixtures("fileserver")
class TestActionStorage(object):
    @pytest.mark.usefixtures("agentr")
    def test__no_content(self, fileserver_url):
        task_id = random.randint(1, 10 ** 8)
        response = requests.get(fileserver_url + "actions/" + str(task_id))
        assert response.status_code == httplib.NO_CONTENT

    def test__read_action(self, fileserver_url, test_task_2, agentr_session_maker, monkeypatch):
        task = test_task_2(None)
        monkeypatch.setattr(type(sdk2_internal.task.Task), "current", task)
        monkeypatch.setattr(sdk2.Task, "current", task)
        task.agentr = agentr_session_maker(task, 1)

        def formatter(v):
            return "<b>{}</b>".format(v)

        message = "<marquee>1234567890BLASTOFF</marquee>"
        start = 0
        total = 100
        meter = sdk2.helpers.ProgressMeter(message, minval=start, maxval=total, formatter=formatter)
        start_time = meter.start_time

        expected_template = {
            "message": common.utils.escape(message),
            "started": start_time,
            "progress": {
                "total": common.utils.escape(formatter(total)),
            }
        }

        with mock.patch.object(meter, "UPDATE_PERIOD", dt.timedelta(seconds=0)):
            with meter:
                for _ in xrange(10):
                    meter.add(1)
                    expected = dict(expected_template)
                    expected["progress"].update({
                        "current": common.utils.escape(formatter(meter.value)),
                        "percentage": common.utils.progress(start, meter.value, total)
                    })
                    response = requests.get(fileserver_url + "actions/" + str(task.id)).json()
                    assert response["actions"] == [expected]

    def test__read_multiple_actions(self, fileserver_url, test_task_2, agentr_session_maker, monkeypatch):
        task = test_task_2(None)
        monkeypatch.setattr(type(sdk2_internal.task.Task), "current", task)
        monkeypatch.setattr(sdk2.Task, "current", task)
        task.agentr = agentr_session_maker(task, 1)

        with mock.patch.object(sdk2.helpers.ProgressMeter, "UPDATE_PERIOD", dt.timedelta(seconds=0)):
            meters = [
                (
                    dt.datetime.utcnow() + dt.timedelta(seconds=random.randint(1, 1000)),
                    sdk2.helpers.ProgressMeter("Woop", maxval=i)
                )
                for i in xrange(11)
            ]

            for fake_start_time, meter in meters:
                meter.start_time = common.api.DateTime.encode(fake_start_time)
            for _, meter in meters:
                meter.__enter__()

            expected_order = [meter.current.encode() for _, meter in sorted(meters)]
            response = requests.get(fileserver_url + "actions/" + str(task.id)).json()
            assert response["actions"] == expected_order
