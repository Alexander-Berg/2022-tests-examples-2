import pytest
import random

import google.protobuf.text_format as pbtext
from google.protobuf.message import Message
from mapreduce.yt.python.yt_stuff import yt_stuff  # noqa

from favicon.config import CONFIG
from favicon import yt

import yatest.common


@pytest.fixture(scope='function')  # noqa
def config(yt_stuff, request):
    test_id = str(random.random())
    CONFIG.Cluster = yt_stuff.get_server()
    CONFIG.Home = "//home/mutation/" + test_id
    CONFIG.Tmp = "//tmp/mutation/" + test_id
    if hasattr(request.module, "JOB_BINARY"):
        CONFIG.JobBinary = request.module.JOB_BINARY

    prefix = "//tmp/%s" % test_id
    yt._client = yt_stuff.get_yt_client()
    yt._client.config["prefix"] = prefix + '/'
    yt._client.config["proxy"]["content_encoding"] = "gzip"
    yt._client.config["proxy"]["accept_encoding"] = "gzip, identity"
    yt.create('map_node', prefix)
    yt.create('map_node', CONFIG.Home, recursive=True)
    yt.create('map_node', CONFIG.Tmp, recursive=True)

    CONFIG.BinDir = yatest.common.build_path("robot/favicon/packages/cm_binaries")
    return CONFIG


# Utilities to expose protobuf fields for pytest and hamcrest comparators

def message_to_text(message, description=None):
    content = pbtext.MessageToString(message, as_one_line=True)
    content = "{} {{ {} }}".format(message.DESCRIPTOR.full_name, content)
    if description is None:
        return content
    else:
        description.append('<')
        description.append(content)
        description.append('>')


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, Message) and isinstance(right, Message) and op == '==':
        left = message_to_text(left)
        right = message_to_text(right)
        return ['Comparing protobuf messages:',
                '    left: %s' % left,
                '!= right: %s' % right]


Message.describe_to = message_to_text
