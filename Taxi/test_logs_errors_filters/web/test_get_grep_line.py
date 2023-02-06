import os
import stat
import subprocess
import tempfile
import urllib

import pytest

QUERY_WORD = {'matchstring': 'kibanning'}

QUERY_ANOTHER_WORD = {'matchstring': 'akibanning'}

QUERY_SPACES = {'matchstring': 'kibanning with spaces'}

QUERY_FIELD = {'field': 'message', 'matchstring': 'Message matchstring'}

RANDOM_STRINGS = [
    '7NI2nfsDrn0TUDTyXaa29rR0kTvkfH',
    'svdPkSfPDGDzqk4Svd62KyMIn0TYh3',
    'w9jcoJa1bu8440nS36vhV8IJJ3nMFU',
    'L2ixLJsGYjFPf09seg4QDN2UfE6iXI',
]

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testcreator'}


@pytest.mark.parametrize('query', [QUERY_WORD, QUERY_SPACES, QUERY_FIELD])
async def test_grep_line_word(web_app_client, create_filter, auth, query):
    _query = {'rules': [query]}

    await create_filter(_query, 'Very cool grep filter')

    args = {'mode': 'grep'}
    await auth()
    response = await web_app_client.get(
        '/v1/combine-filters/?{}'.format(urllib.parse.urlencode(args)),
        headers=HEADERS,
    )

    random_strings = iter(RANDOM_STRINGS)

    tmpfile = os.path.join(tempfile.mkdtemp(), 'greptest.txt')

    with open(tmpfile, 'w') as fwr:
        fwr.write(next(random_strings) + '\n')

        wstr = query['matchstring']
        if 'field' in query:
            wstr = '{}={}'.format(query['field'], query['matchstring'])

        fwr.write(
            '{}\t{}\t{}\n'.format(
                next(random_strings), wstr, next(random_strings),
            ),
        )
        fwr.write(next(random_strings) + '\n')

    assert response.status == 200

    content = await response.json()

    # Pipes are difficult to escape so we work around that

    patfile = tmpfile + '.pattern'

    with open(patfile, 'w') as fp:
        towrite = content['result'].split('-P')[-1].strip().strip('\'')
        fp.write(towrite)
    shfile = tmpfile + '.sh'

    with open(shfile, 'w') as fp:
        fp.write('#!/bin/bash\n')
        fp.write('grep -v -P -f {} {}'.format(patfile, tmpfile))

    status = os.stat(shfile)
    os.chmod(shfile, status.st_mode | stat.S_IEXEC)

    process = subprocess.Popen(
        [shfile], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )

    stdout, stderr = process.communicate()

    assert stdout == '{}\n{}\n'.format(
        RANDOM_STRINGS[0], RANDOM_STRINGS[-1],
    ).encode('utf-8')
    assert not stderr
