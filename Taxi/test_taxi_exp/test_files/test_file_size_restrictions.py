import random
import string

import pytest

from test_taxi_exp.helpers import files


def _gen_content(lines, size_line):
    random.seed(1111)
    content = [
        ''.join([random.choice(string.digits) for n in range(size_line)])
        for _ in range(lines)
    ]
    o_content = ('\n'.join(content)) + '\n'
    return o_content.encode('utf-8')


@pytest.mark.config(EXP_ALLOWED_FILE_SIZE=1000)
@pytest.mark.pgsql('taxi_exp')
async def test_file_restrictions(taxi_exp_client):
    big_file = _gen_content(1001, 0)
    assert len(big_file) == 1001
    response = await files.post_file(taxi_exp_client, 'file_1.txt', big_file)
    assert response.status == 413
