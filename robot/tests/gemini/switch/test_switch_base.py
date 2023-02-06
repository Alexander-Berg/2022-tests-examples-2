import os
import signal
import string
import shutil
import time

from plugins.gemini import *
from common.libs.plugins.reporter import *
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge
from common.libs.plugins.runners import KWProgram
import pytest


def pytest_funcarg__html_config(request):
    return html_config(
        name="switch_base",
        description="""Test checks switching between current and new bases""",
        directory="switch",
        scope="function"
    )

def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://www.cur.ru/": "http://www.cur.ru/",
        "http://www.both.ru/": "http://www.both.ru/",
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr"
    }
    def exec_after(gemini):
        gemini.run_pollux([
            "-w2",
            "-le",
            "-m1",
            "--verbose-main"
        ])
        gemini.run_castor([
            "-w2",
            "-le",
            "-m1"
        ])


    return gemini_config(main_url, exec_after=exec_after, scope="function")


def check_url(gemini, url, in_base=True):

    (out, err, retcode) = gemini.geminicl.request(
        url="%s" % url
    )
    pb = TResultInfo()
    Merge(out, pb)

    if in_base:
        expected_response = """
            Response {
                OriginalUrl: "%s"
                CanonizedUrl: "%s"
                MainUrl: "%s"
                CanonizationType: WEAK
                Error: URL_NOT_FOUND
                BaseInfo {
                  IndexTimestamp: 1364188709
                  MirrorsTimestamp: 1363264068
                  RflTimestamp: 1363593273
                }
            }""" % (url,url,url)
    else:
        expected_response = """
            Response {
                OriginalUrl: "%s"
                CanonizedUrl: "%s"
                MainUrl: "%s"
                CanonizationType: WEAK
                Error: URL_NOT_FOUND
            }
            Status: 0""" % (url,url,url)

    message = "Wrong response from gemini:\n%s" % expected_received_table(expected_response, out)
    assert pb.Response.OriginalUrl  == "%s" % url, message
    assert pb.Response.CanonizedUrl == "%s" % url, message
    assert pb.Response.MainUrl[0]   == "%s" % url, message

    if in_base:
        message = "Expected url is not in base:\n%s" % expected_received_table(expected_response, out)
        assert not "Error: URL_NOT_FOUND" in out, message
    if not in_base:
        message = "Unexpected url is in base:\n%s" % expected_received_table(expected_response, out)
        assert "Error: URL_NOT_FOUND" in out, message


#@pytest.mark.skipif("True")
def test_switch_to_new_base(gemini, narrator, html):

    html.test(
        name="Switch pollux to new base",
        suite="switch",
        description="Load base and new base. Remove pollux_started.flag and send SIGUSR1, SIGUSR2. Check new url is in base, old url is not in base."
    )

    #check current base
    check_url(gemini, "http://www.cur.ru/")
    check_url(gemini, "http://www.both.ru/")
    check_url(gemini, "http://www.new.ru/", in_base=False)

    #create new base
    new_base_dir = gemini.homeDir + "new"
    os.mkdir(new_base_dir)
    main_Url = {
        "http://www.both.ru/": "http://www.both.ru/",
        "http://www.new.ru/": "http://www.new.ru/",
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr"
    }

    homeDir = gemini.homeDir
    gemini.homeDir += "new"
    gemini.main_url = main_Url
    gemini.prepare(gemini, False)
    gemini.homeDir = homeDir

    shutil.rmtree(gemini.homeDir + "/BASE/0/new")
    shutil.rmtree(new_base_dir   + "/BASE/0/new")
    os.rename(new_base_dir + "/BASE/0/cur", new_base_dir   + "/BASE/0/new")
    shutil.copytree( new_base_dir + "/BASE/0/new", gemini.homeDir + "/BASE/0/new")

    assert gemini.pollux.get_new_base_state() == 0

    gemini.pollux.daemon.send_signal(signal.SIGUSR1)
    i=0
    while( not gemini.pollux.get_new_base_state() == 2 and i < 10):
        narrator.pause(1)
        i += 1

    assert gemini.pollux.get_new_base_state() == 2

    gemini.pollux.daemon.send_signal(signal.SIGUSR2)

    narrator.wait(lambda: gemini.pollux.get_new_base_state() == 0, timeout=5)
    assert gemini.pollux.get_new_base_state() == 0

    #check new base
    check_url(gemini, "http://www.cur.ru/", in_base=False)
    check_url(gemini, "http://www.both.ru/")
    check_url(gemini, "http://www.new.ru/")


#@pytest.mark.skipif("True")
def test_switch_to_empty_base(gemini, narrator, html):

    html.test(
        name="Switch pollux to empty base",
        suite="switch",
        description="Load base and empty new base. Remove pollux_started.flag and send SIGUSR1, SIGUSR2. Check pollux stopped."
    )

    #check current base
    check_url(gemini, "http://www.cur.ru/")
    check_url(gemini, "http://www.both.ru/")
    check_url(gemini, "http://www.new.ru/", in_base=False)

    #set base empty
    for fn in os.listdir(gemini.homeDir + "/BASE/0/new"):
        fo = open(gemini.homeDir + "/BASE/0/new" + "/" + fn, "w")
        fo.close()

    gemini.pollux.daemon.send_signal(signal.SIGUSR1)
    i=0
    while( not gemini.pollux.get_new_base_state() == 2 and i < 10):
        narrator.pause(1)
        i += 1

    assert gemini.pollux.get_new_base_state() == 3
    gemini.pollux.daemon.send_signal(signal.SIGUSR2)

    narrator.pause(3)

    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.cur.ru/"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected_response = """
        Response {
          OriginalUrl: "http://www.cur.ru/"
          CanonizedUrl: "http://www.cur.ru/"
          MainUrl: "http://www.cur.ru/"
          CanonizationType: WEAK
        }
        Status: 0"""
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected_response, out)
    assert pb.Response.CanonizedUrl == "http://www.cur.ru/", message
    assert pb.Response.MainUrl[0] == "http://www.cur.ru/", message


#@pytest.mark.skipif("True")
def test_switch_with_started_flag(gemini, narrator, html):

    html.test(
        name="Switch pollux to new base with not removed started_flag",
        suite="switch",
        description="Load base and new base. Don't remove pollux_started.flag and send SIGUSR1, SIGUSR2. Check pollux stopped."
    )

    #check current base
    check_url(gemini, "http://www.cur.ru/")
    check_url(gemini, "http://www.both.ru/")
    check_url(gemini, "http://www.new.ru/", in_base=False)

    #create new base
    new_base_dir = gemini.homeDir + "new"
    os.mkdir(new_base_dir)
    main_Url = {
        "http://www.both.ru/": "http://www.both.ru/",
        "http://www.new.ru/": "http://www.new.ru/",
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr"
    }

    homeDir = gemini.homeDir
    gemini.homeDir += "new"
    gemini.main_url = main_Url
    gemini.prepare(gemini, False)
    gemini.homeDir = homeDir

    shutil.rmtree(gemini.homeDir + "/BASE/0/new")
    shutil.rmtree(new_base_dir   + "/BASE/0/new")
    os.rename(new_base_dir + "/BASE/0/cur", new_base_dir   + "/BASE/0/new")
    shutil.copytree( new_base_dir + "/BASE/0/new", gemini.homeDir + "/BASE/0/new")

    gemini.pollux.daemon.send_signal(signal.SIGUSR1)
    i=0
    while( not gemini.pollux.get_new_base_state() == 2 and i < 10):
        narrator.pause(1)
        i += 1
    narrator.pause(1)
    assert gemini.pollux.get_new_base_state() == 2
    gemini.pollux.daemon.send_signal(signal.SIGUSR2)

    check_url(gemini, "http://www.cur.ru/", in_base=False)
    check_url(gemini, "http://www.both.ru/")
    check_url(gemini, "http://www.new.ru/")
