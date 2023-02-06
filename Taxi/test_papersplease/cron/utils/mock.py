def get_requests(mocked_handler) -> list:
    return [
        mocked_handler.next_call()['request'].json
        for _ in range(mocked_handler.times_called)
    ]
