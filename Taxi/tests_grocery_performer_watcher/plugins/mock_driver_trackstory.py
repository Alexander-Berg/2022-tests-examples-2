# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

import pytest
from tests_grocery_performer_watcher.plugins.service_mock import (
    EndpointContext,
    ServiceContext,
    make_response,
)


@dataclass
class PositionContext(EndpointContext):
    performer_id: str = 'performer_id_1'
    position: List[float] = field(default_factory=list)
    timestamp: Optional[datetime] = datetime.utcnow()
    type: str = 'raw'


@pytest.fixture(name='position')
def _position(mockserver, load_json):
    @mockserver.json_handler('/driver-trackstory/position')
    async def handler(request):
        assert request.json == {
            'driver_id': context.performer_id,
            'type': context.type,
        }

        if context.error:
            return context.make_error_response()
        if context.response:
            return context.response

        track_position = {
            'direction': 0,
            'lon': context.position[0],
            'lat': context.position[1],
            'speed': 0,
            'timestamp': context.timestamp.timestamp(),
        }
        return mockserver.make_response(
            json={'position': track_position, 'type': 'raw'}, status=200,
        )

    context = PositionContext(mock=handler)
    return context


@dataclass
class DriverTrackstoryContext(ServiceContext):
    position: PositionContext


@pytest.fixture(name='driver_trackstory')
def _driver_trackstory(position):
    return DriverTrackstoryContext(position=position)
