import os
import random
import tempfile
from tarfile import TarFile

import pytest
import yatest.common
from PIL import Image

from favicon.util import smush, compare_images


SMUSH_TOOL = yatest.common.binary_path("robot/favicon/tools/smush/smush")


@pytest.fixture(scope='module', params=[16, 32])
def icons(request):
    tar = TarFile("icons-top1000.tar")
    tar.extractall()
    dpath = "icons-top1000/%d" % request.param
    retval = {}
    for name in os.listdir(dpath):
        fpath = os.path.join(dpath, name)
        with file(fpath) as f:
            im = Image.open(f)
            im.load()
            retval[fpath] = im
    return retval


@pytest.mark.parametrize("sprite", [1, 10, 50],
                         ids=lambda x: 's%d' % x)
@pytest.mark.parametrize("iteration", xrange(20),
                         ids=lambda x: 'i%d' % x)
def test_smush(icons, sprite, iteration):  # noqa
    random.seed(iteration * 1000 + sprite)
    sample = random.sample(icons.keys(), sprite)
    sample_data = [icons[k] for k in sample]

    with tempfile.NamedTemporaryFile(suffix='.png') as f:
        command = [SMUSH_TOOL]
        command.extend(sample)
        command.append(f.name)
        yatest.common.execute(command)

        sprite = smush(*sample_data)
        answer = Image.open(f.name)
        answer.load()
        assert sprite.size == answer.size

        diff = compare_images(sprite, answer)
        assert diff < 0.1, "Smush failed on sample %s, diff: %f" % (sample, diff)
