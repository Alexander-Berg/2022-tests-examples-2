import pytest


@pytest.fixture(name='st_execute_transaction')
def _st_execute_transaction(patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def _handler(*args, **kwargs):
        return {}

    return _handler


@pytest.fixture(name='st_get_ticket')
def _st_get_ticket(patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _handler(*args, **kwargs):
        return {'key': 'TAXIADMIN-1', 'status': {'key': 'closed'}}

    return _handler


@pytest.fixture(name='st_create_ticket')
def _st_create_ticket(patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _handler(**kwargs):
        return {'key': 'TAXIADMIN-1'}

    return _handler


@pytest.fixture(name='st_create_comment')
def _st_create_comment(patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _handler(ticket, text, *args, **kwargs):
        assert ticket

    return _handler


@pytest.fixture(name='st_get_myself')
def _st_get_myself(patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _handler(*args, **kwargs):
        return {'login': 'robot-taxi-clown'}

    return _handler


@pytest.fixture(name='st_get_comments_value')
def _st_get_comments_value():
    def _wrapper(*args, **kwargs):
        return []

    return _wrapper


@pytest.fixture(name='st_get_comments')
def _st_get_comments(patch, st_get_comments_value):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _handler(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return st_get_comments_value(*args, **kwargs)

    return _handler
