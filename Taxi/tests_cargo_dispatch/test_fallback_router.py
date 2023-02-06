import pytest


@pytest.fixture(name='mock_dispatch_segments_journal')
async def _mock_dispatch_segments_journal(
        mockserver,
        happy_path_state_routers_chosen,
        read_segment_journal,
        run_segments_journal_mover,
):
    async def _wrapper(
            waybill_building_version: int = None, empty_cursor: bool = False,
    ):
        """
        :param waybill_building_version: set value for all journal events
        :param empty_cursor: replace cursor by None value
        :return:
        """

        @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
        async def _handler(request):
            # Move events from buffer to journal
            await run_segments_journal_mover()

            req_cursor = None if empty_cursor else request.json.get('cursor')
            response = await read_segment_journal(
                request.json['router_id'], req_cursor, without_duplicates=True,
            )

            for event in response['events']:
                event['waybill_building_version'] = (
                    waybill_building_version
                    or event['waybill_building_version']
                )

            return mockserver.make_response(
                headers={'X-Polling-Delay-Ms': '0'}, json=response,
            )

        return _handler

    return _wrapper


@pytest.fixture(name='mock_dispatch_segment_info', autouse=True)
async def _mock_dispatch_segment_info(
        mockserver, happy_path_state_routers_chosen, get_segment_info,
):
    async def _wrapper(
            waybill_building_awaited=True,
            add_performer_requirements=False,
            modified_classes: list = None,
            tariffs_substitution: list = None,
            performer_classes: list = None,
            expected_min_revision: str = None,
            additional_taxi_requirements: dict = None,
    ):
        @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
        async def _handler(request):
            if expected_min_revision:
                assert request.query['min_revision'] == expected_min_revision

            response = await get_segment_info(request.query['segment_id'])
            response['dispatch'][
                'waybill_building_awaited'
            ] = waybill_building_awaited

            if add_performer_requirements:
                taxi_classes = performer_classes or ['express', 'courier']
                requirements = {
                    'taxi_classes': taxi_classes,
                    'door_to_door': True,
                    'special_requirements': {'virtual_tariffs': []},
                }
                if additional_taxi_requirements:
                    requirements.update(additional_taxi_requirements)
                response['segment']['performer_requirements'] = requirements

            if modified_classes is not None:
                response['dispatch']['modified_classes'] = modified_classes

            if tariffs_substitution is not None:
                response['dispatch'][
                    'tariffs_substitution'
                ] = tariffs_substitution

            return response

        return _handler

    return _wrapper


@pytest.fixture(name='mock_waybill_propose', autouse=True)
def _mock_waybill_propose(mockserver):
    def _wrapper(response_code=200):
        @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
        def _handler(request):
            return mockserver.make_response(status=response_code, json={})

        return _handler

    return _wrapper


# dispatch-journal segments response:
# ['seg1', 'seg2', 'seg3', 'seg1', 'seg2', 'seg3']


async def test_happy_path(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info()
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }


async def test_propose_error(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
        taxi_cargo_dispatch,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info()
    mock_waybill_propose(response_code=500)

    with pytest.raises(taxi_cargo_dispatch.TestsuiteTaskFailed):
        await run_fallback_router()


async def test_waybill_building_not_awaited(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(waybill_building_awaited=False)
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 0,
    }


async def test_waybill_already_created(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal(
        waybill_building_version=1, empty_cursor=True,
    )
    await mock_dispatch_segment_info()
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }

    # Second run
    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 0,
    }


async def test_replace_old_waybill_version(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal(waybill_building_version=1)
    await mock_dispatch_segment_info()
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }

    # Second run. New waybill_building_version
    await mock_dispatch_segments_journal(
        waybill_building_version=2, empty_cursor=True,
    )

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }


async def test_cursor_updating(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    journal_handler = await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info()
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }
    assert set(journal_handler.next_call()['request'].json.keys()) == {
        'router_id',
        'without_duplicates',
    }

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 0,
        'waybills-proposed-count': 0,
    }
    assert set(journal_handler.next_call()['request'].json.keys()) == {
        'router_id',
        'cursor',
        'without_duplicates',
    }


async def test_proposed_waybill_manually(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
        request_waybill_propose,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info()
    propose_handler = mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }

    proposal_request = propose_handler.next_call()['request'].json
    waybill_ref = proposal_request['external_ref']
    assert (waybill_ref.split('/')[0], waybill_ref.split('/')[2]) == (
        'fallback_router',
        '1',
    )

    propose_response = await request_waybill_propose(proposal_request)
    assert propose_response.status_code == 200


async def test_two_events_and_old_wb_already_created(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
        request_waybill_propose,
):
    """
    The segment X has 2 events in the journal chunk:
    first with waybill_building_version = 1 and
    second with waybill_building_version = 2.
    Waybill for waybill_building_version = 1 already created
    Check that waybill for segment X with
    waybill_building_version = 2 will be created
    """

    # Prepare data. Create waybill for
    # waybill_building_version = 1
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info()
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }

    # Do check
    await mock_dispatch_segments_journal(
        waybill_building_version=2, empty_cursor=True,
    )

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }


async def test_propose_order_requirements(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(add_performer_requirements=True)
    propose_handler = mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }

    proposal_request = propose_handler.next_call()['request'].json
    assert proposal_request['taxi_order_requirements'] == {
        'taxi_classes': ['express', 'courier'],
        'door_to_door': True,
    }


async def test_modified_classes(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(
        add_performer_requirements=True, modified_classes=['eda'],
    )
    propose_handler = mock_waybill_propose()
    await run_fallback_router()

    proposal_request = propose_handler.next_call()['request'].json
    assert proposal_request['taxi_order_requirements'] == {
        'taxi_classes': ['eda'],
        'door_to_door': True,
    }


async def test_not_need_to_substitute_tariffs(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    """
    Field 'tariffs_substitution' exists, but there are
    no substitution classes in modified_classes
    """
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(
        add_performer_requirements=True,
        modified_classes=['eda'],
        tariffs_substitution=['courier', 'express'],
    )
    propose_handler = mock_waybill_propose()
    await run_fallback_router()

    proposal_request = propose_handler.next_call()['request'].json
    assert proposal_request['taxi_order_requirements'] == {
        'taxi_classes': ['eda'],
        'door_to_door': True,
    }


async def test_tariffs_substitution(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(
        add_performer_requirements=True,
        performer_classes=['courier'],
        tariffs_substitution=['courier', 'express'],
    )
    propose_handler = mock_waybill_propose()
    await run_fallback_router()

    proposal_request = propose_handler.next_call()['request'].json
    assert proposal_request['taxi_order_requirements'] == {
        'taxi_classes': ['courier', 'express'],
        'door_to_door': True,
    }


async def test_segment_after_reorder(
        happy_path_state_performer_found,
        mock_dispatch_segments_journal,
        mock_dispatch_segment_info,
        mock_waybill_propose,
        run_fallback_router,
        reorder_waybill,
        get_segment_info,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info()
    mock_waybill_propose()
    await run_fallback_router()

    propose_handler = mock_waybill_propose()
    await reorder_waybill('waybill_fb_3')

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 1,
        'waybills-proposed-count': 1,
    }
    proposal_request = propose_handler.next_call()['request'].json
    assert proposal_request['segments'][0] == {
        'segment_id': 'seg3',
        'waybill_building_version': 2,
    }


async def test_use_max_segment_revision(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(
        add_performer_requirements=True, expected_min_revision='2',
    )
    mock_waybill_propose()

    result = await run_fallback_router()
    assert result['stats'] == {
        'new-segment-events-count': 5,
        'waybills-proposed-count': 5,
    }


async def test_taxi_requirements(
        mock_dispatch_segments_journal,
        mock_waybill_propose,
        mock_dispatch_segment_info,
        run_fallback_router,
):
    await mock_dispatch_segments_journal()
    await mock_dispatch_segment_info(
        add_performer_requirements=True,
        modified_classes=['eda'],
        additional_taxi_requirements={'kirslayk_property': 'property'},
    )
    propose_handler = mock_waybill_propose()
    await run_fallback_router()

    proposal_request = propose_handler.next_call()['request'].json
    assert proposal_request['taxi_order_requirements'] == {
        'taxi_classes': ['eda'],
        'door_to_door': True,
        'kirslayk_property': 'property',
    }
