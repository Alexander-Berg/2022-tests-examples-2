import json
import logging
import os
import shutil
import six
import tempfile
import time

from six.moves import urllib

import yatest.common.network as network

from sandbox.projects.autocheck.lib.reports import stream


def test_report_server():
    logging.basicConfig(level=logging.DEBUG)

    messages = []
    root = tempfile.mkdtemp()
    path1 = os.path.join(root, 'file1')
    path2 = os.path.join(root, 'file2')

    receiver1 = stream.StoringReceiver(path1)
    receiver2 = stream.StoringReceiver(path2)
    with network.PortManager() as pm:
        server = stream.StreamReportServer(stream.CompoundReceiver([receiver1, receiver2]), port=pm.get_port(52152))

        for i in range(1, 6):
            messages.append({'results': [{'data': i}]})
            res = urllib.request.urlopen(server.url, data=six.ensure_binary(json.dumps(messages[-1])))
            logging.debug('Server response: %s', res.read())
            time.sleep(i)

        server.stop()

    receiver1.close()
    receiver2.close()

    with open(path1) as d1, open(path2) as d2:
        assert messages == list(map(json.loads, d1)) == list(map(json.loads, d2))

    shutil.rmtree(root)
