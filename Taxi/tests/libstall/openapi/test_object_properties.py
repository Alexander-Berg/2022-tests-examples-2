import pytest

from libstall import oa


@pytest.mark.skip(reason="not done yet")
def test_drop_properties(tap):
    with tap.plan(1):
        spec = oa.Spec(
            {
                'paths': {
                    '/': {
                        'post': {
                            'requestBody': {
                                'content':
                                    {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'properties': {
                                                    'foo': {
                                                        'type': 'string',
                                                    },
                                                    'bar': {
                                                        'type': 'number',
                                                    },
                                                }
                                            }
                                        }
                                    }
                            },
                            'responses': {},
                        }
                    },
                }
            },
            validate=False,
        )

        r = spec.validate_request(
            '/',
            'post',
            content_type='application/json',
            body={'foo': 'x', 'bar': 300, 'spam': 'eggs'},
        )

        tap.eq(
            r.body,
            {'foo': 'x', 'bar': 300},
            'оставили только то, что есть в схеме',
        )
