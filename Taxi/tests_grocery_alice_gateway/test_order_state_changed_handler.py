from tests_grocery_alice_gateway import events


async def test_basic(taxi_grocery_alice_gateway, testpoint, push_event):
    event = events.OrderStateChangedEvent(
        order_id='23gsd34e223je21-grocery', order_status='performer_found',
    )

    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    await push_event(event, event.consumer)

    await taxi_grocery_alice_gateway.run_task(
        f'{event.consumer}-consumer-task',
    )

    await event_commit.wait_call()

    # WRITE YOUR TEST CODE HERE AFTER ADD HANDLE-LOGIC
