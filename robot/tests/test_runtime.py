import logging
import json
import random
import socket
import urllib2
import urlparse
from StringIO import StringIO
from contextlib import closing

import pytest
import yatest.common
from yatest.common import network

from PIL import Image, ImageChops


BINARY = yatest.common.binary_path('robot/favicon/runtime/favicond')


class FaviconAPI(object):

    def __init__(self, path, separator, host_api):
        self.path = path
        self.separator = separator
        self.host_api = host_api

    def make_request(self, keys, cgi):
        if self.host_api:
            new_keys = []
            for k in keys:
                if "://" not in k:
                    k = "http://" + k
                new_keys.append(urlparse.urlparse(k).netloc)
            keys = new_keys

        request = self.path
        if keys:
            request += self.separator.join(keys)
        if cgi:
            request += "?" + "&".join("{}={}".format(key, value) for key, value in cgi.items())
        return request


class FaviconRequester(object):
    API_VERSIONS = {
        1: FaviconAPI("/favicon/", "/", True),
        2: FaviconAPI("/favicon/v2/", ";", False),
    }

    def __init__(self, port, db, attrs_trie, keys, api_version=1):
        self.api = self.API_VERSIONS[api_version]
        self.port = port
        self.db = db
        self.attrs_trie = attrs_trie
        self.address = "http://localhost:{}".format(port)
        self.keys = set(keys)

    def __enter__(self):
        # use random path in order to keep logs from previous favicond runs
        favicond_log = yatest.common.output_path("favicond_{}.log".format(random.randint(0, 100500)))
        cmd = [
            BINARY,
            "--port", str(self.port),
            "--attrs", self.attrs_trie,
            "--access-log", favicond_log,
            "--icons-base", self.db,
        ]
        self.process = yatest.common.execute(cmd, wait=False)
        yatest.common.wait_for(self.port_open, 30, "Port not opened")
        return self

    def __exit__(self, type, value, traceback):
        if self.process.running:
            self.process.kill()

    def port_open(self):
        with closing(socket.socket()) as sock:
            return sock.connect_ex(('localhost', self.port)) == 0

    def send_request(self, request):
        full_request = self.address + request
        logging.info("Requesting %s", full_request)
        with closing(urllib2.urlopen(self.address + request)) as r:
            ctype = r.info().getheader('Content-Type')
            if ctype == 'application/json':
                return json.loads(r.read())
            else:
                im = Image.open(StringIO(r.read()))
                im.load()
                return im

    def __call__(self, *keys, **cgi):
        return self.send_request(self.api.make_request(keys, cgi))


@pytest.yield_fixture(scope='module', params=[1, 2], ids=["host-api", "url-api"])
def favicon(request):
    attrs = 'trie-sample/favicon_attrs_trie.data'
    db = 'trie-sample/favicon.db'
    with open('trie-sample/keys.txt') as f:
        keys = f.read().split("\n")

    with network.PortManager() as pm:
        port = pm.get_port()
        with FaviconRequester(port, db, attrs, keys, request.param) as r:
            yield r


def test_accepted_size(favicon):
    accepted = []
    for size in xrange(-500, 500):
        try:
            favicon("ya.ru", size=size)
            accepted.append(size)
        except urllib2.HTTPError:
            pass
    return accepted


def test_empty_dot(favicon):
    assert "example.org" not in favicon.keys
    dot = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    box_16x32 = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
    box_32x64 = Image.new("RGBA", (32, 64), (0, 0, 0, 0))

    resp = favicon("example.org")
    assert ImageChops.difference(dot, resp).getbbox() is None
    resp = favicon("example.org", "example.org")
    assert ImageChops.difference(box_16x32, resp).getbbox() is None
    resp = favicon("example.org", "example.org", size=32)
    assert ImageChops.difference(box_32x64, resp).getbbox() is None
    resp = favicon("example.org", size=32, stub=1)
    assert resp.size == (32, 32)


def test_validation(favicon):
    favicon()
    favicon("a", "b", "c", "", "", "a", "", "aq", "aa")
    favicon("", "", "", "", "")
    with pytest.raises(urllib2.HTTPError):
        favicon.send_request("/favicon")
    with pytest.raises(urllib2.HTTPError):
        favicon.send_request("/admin")
    with pytest.raises(urllib2.HTTPError):
        favicon(*(["a"] * 200))
    with pytest.raises(urllib2.HTTPError):
        favicon(size=0)

    for param in ["size", "stub", "json"]:
        with pytest.raises(urllib2.HTTPError):
            favicon("ya.ru", **{param: -1})
        with pytest.raises(urllib2.HTTPError):
            favicon("ya.ru", **{param: ""})
        with pytest.raises(urllib2.HTTPError):
            favicon("ya.ru", **{param: "kwerjqwer"})
        with pytest.raises(urllib2.HTTPError):
            favicon("ya.ru", **{param: 9999999999999999})


def test_sample(favicon):
    random.seed(239)
    #  sample = random.sample(favicon.keys, 20) TODO(niknik): should sample new favicon_trie
    sample = []
    sample.extend(["{}://{}.example.org/".format("http" if x % 2 == 0 else "https", str(x)) for x in range(10)])
    random.shuffle(sample)

    r1 = favicon(*sample, json=1, size=16)
    r2 = favicon(*sample, json=1, size=32)
    r3 = favicon(*sample, json=1, size=120)
    assert map(len, [r1, r2, r3]) == [len(sample)] * 3
    for key, i1, i2, i3 in zip(sample, r1, r2, r3):
        i = i1['image'] or i2['image'] or i3['image']
        if key in favicon.keys:
            assert i is not None
        else:
            assert i is None


@pytest.mark.parametrize("size", [16, 32, 120])
def test_stub(favicon, size):
    assert "example.org" not in favicon.keys
    r1 = favicon("example.org", "example.org", size=size)
    r2 = favicon("example.org", "example.org", size=size, stub=1)
    assert ImageChops.difference(r1, r2).getbbox() is not None
