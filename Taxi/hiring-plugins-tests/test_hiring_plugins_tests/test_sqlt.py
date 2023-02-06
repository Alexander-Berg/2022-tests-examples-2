import re


async def test_sqlt(hiring_forms_mockserver, wait_until_ready, web_context):
    await wait_until_ready()
    query, binds = web_context.sqlt(
        'template_test.sqlt', {'table': 'test', 'ids': [1, 2, 3]},
    )

    assert binds == [1, 2, 3]
    assert re.search(r'"test"', query)
    assert re.search(r'"id" IN \(\$1,\$2,\$3\)', query)
