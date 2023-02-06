import pytest


@pytest.mark.skip()
async def test_preload(logistic_dispatcher_client):
    """
        1. run testsuite with LD_PRELOAD.
        
        pass `env` to create_daemon_scope like this:
        env={
            'LD_PRELOAD': '/usr/lib/x86_64-linux-gnu/libjemalloc.so.2',
            'MALLOC_CONF': (
                'prof:true,prof_active:false,lg_prof_sample:14,'
                'prof_prefix:/tmp/jeprof-logistic-dispatcher'
            ),
        },

        2. uncomment this test
    """
    # test Dump
    response = await logistic_dispatcher_client.post(
        '/service/jemalloc/prof', json={'command': 'Dump'},
    )
    assert response.json() == {'message': 'OK'}

    # test Enable
    response = await logistic_dispatcher_client.post(
        '/service/jemalloc/prof', json={'command': 'Enable'},
    )
    assert response.json() == {'message': 'OK'}

    # test Disable
    response = await logistic_dispatcher_client.post(
        '/service/jemalloc/prof', json={'command': 'Disable'},
    )
    assert response.json() == {'message': 'OK'}

    # test Stat
    response = await logistic_dispatcher_client.post(
        '/service/jemalloc/prof', json={'command': 'Stat'},
    )
    assert response.status_code == 200
