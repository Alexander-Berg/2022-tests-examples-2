# root conftest for service cashback-levels
import base64
import json
import pprint
from typing import Optional
from typing import Set
from typing import Type

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from event_pb2 import EventType
import google.protobuf.message
import grpc
from mission_pb2 import Customer
from mission_pb2 import UserMission
from mission_progress_notification_pb2 import MissionProgressNotification
import pytest
import segment_mission_service_api_pb2
import segment_mission_service_api_pb2_grpc
import user_mission_service_api_pb2
import user_mission_service_api_pb2_grpc


pytest_plugins = ['cashback_levels_plugins.pytest_plugins']


PROTOSEQ_SYNC_WORD = (
    b'\x1F\xF7\xF7~\xBE\xA6^\2367\xA6\xF6.\xFE\xAEG\xA7'
    b'\xB7n\xBF\xAF\x16\x9E\2377\xF6W\367f\xA7\6\xAF\xF7'
)


@pytest.fixture
def get_notification():
    def _get_notification(
            notification_status,
            yandex_uid,
            external_id,
            mission_status,
            progress_type,
            progress_status,
            counter_progress_target=None,
            counter_progress_current=None,
            cyclic_progress_target_completed_iteration=None,
            cyclic_progress_current_completed_iteration=None,
            transaction_progress_target=None,
            transaction_progress_current_achieved=None,
            transaction_progress_current_completed=None,
            start_time=None,
            stop_time=None,
            event_id=None,
            event_type=None,
            version=0,
            taxi_order_id=None,
            client_id=None,
            service=None,
            customer=Customer.CUSTOMER_LEVELS,
    ) -> bytes:
        ntf = MissionProgressNotification(
            mission=UserMission(start_time=start_time, stop_time=stop_time),
        )
        ntf.status = notification_status
        ntf.mission.puid = int(yandex_uid)
        ntf.mission.external_id = external_id
        ntf.mission.status = mission_status
        ntf.mission.customer = customer
        getattr(ntf.mission, progress_type).status = progress_status
        if counter_progress_target:
            ntf.mission.counter_progress.target = counter_progress_target
        if counter_progress_current:
            ntf.mission.counter_progress.current = counter_progress_current
        if cyclic_progress_target_completed_iteration:
            ntf.mission.cyclic_progress.target_completed_iteration = (
                cyclic_progress_target_completed_iteration
            )
        if cyclic_progress_current_completed_iteration:
            ntf.mission.cyclic_progress.current_completed_iteration = (
                cyclic_progress_current_completed_iteration
            )
        if transaction_progress_target:
            ntf.mission.transaction_progress.target = (
                transaction_progress_target
            )
        if transaction_progress_current_achieved:
            ntf.mission.transaction_progress.current_achieved = (
                transaction_progress_current_achieved
            )
        if transaction_progress_current_completed:
            ntf.mission.transaction_progress.current_completed = (
                transaction_progress_current_completed
            )
        if event_id is not None:
            ntf.event.id = event_id
        if event_type is not None:
            ntf.event.type = event_type
        if version is not None:
            ntf.mission.version = version
        if taxi_order_id is not None:
            ntf.event.type = EventType.EVENT_TYPE_TAXI_ORDER
            ntf.event.taxi_order.order_id = taxi_order_id
        if client_id is not None:
            ntf.event.notification_payload.client_id = client_id
        if service is not None:
            ntf.event.notification_payload.service = service
        return ntf.SerializeToString()

    return _get_notification


@pytest.fixture
def messages_to_b64_protoseq():
    def _messages_to_b64_protoseq(*messages: bytes) -> str:
        res = b''
        for msg in messages:
            length_prefix = len(msg).to_bytes(4, byteorder='little')
            res += length_prefix + msg + PROTOSEQ_SYNC_WORD

        return base64.b64encode(res).decode()

    return _messages_to_b64_protoseq


@pytest.fixture
def b64_protoseq_to_message():
    def _b64_protoseq_to_message(
            message_b64: str,
            message_class: Type[google.protobuf.message.Message],
    ) -> google.protobuf.message.Message:
        res = message_class()
        bytes_msg = base64.b64decode(message_b64)[4 : -len(PROTOSEQ_SYNC_WORD)]
        res.ParseFromString(bytes_msg)
        return res

    return _b64_protoseq_to_message


@pytest.fixture
async def send_message_to_logbroker(taxi_cashback_levels):
    async def _send_message_to_logbroker(
            consumer,
            topic='sometopic',
            cookie='cookie',
            data=None,
            data_b64=None,
    ):
        assert data or data_b64
        message = dict(consumer=consumer, topic=topic, cookie=cookie)
        if data:
            message['data'] = data
        else:
            message['data_b64'] = data_b64

        return await taxi_cashback_levels.post(
            'tests/logbroker/messages', data=json.dumps(message),
        )

    return _send_message_to_logbroker


class MockGrpc:
    TVM_TICKET = 'mission_control_tvm_ticket'
    PORT: Optional[int] = 1083
    HOST = 'localhost'
    TIMEOUT = 3


@pytest.fixture
def _grpc_port(get_free_port) -> int:
    if MockGrpc.PORT is None:
        MockGrpc.PORT = get_free_port()
    return MockGrpc.PORT


class GrpcServer:
    port = None

    def __init__(self, expected_requests, expected_responses):
        self.server = None
        self.servicer = None
        self.expected_requests = expected_requests
        self.expected_responses = expected_responses

    async def __aenter__(self):
        self.server = grpc.aio.server()
        self.register()
        self.server.add_insecure_port(f'{MockGrpc.HOST}:{self.port}')
        await self.server.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.server.stop(MockGrpc.TIMEOUT)

    def register(self):
        pass


class SegmentMissionServiceServer(GrpcServer):
    def register(self):
        self.servicer = SegmentMissionServiceAPIServicer(
            self.expected_requests, self.expected_responses,
        )
        segment_mission_service_api_pb2_grpc.add_SegmentMissionServiceAPIServicer_to_server(  # noqa: E501
            self.servicer, self.server,
        )


class UserMissionServiceServer(GrpcServer):
    def register(self):
        self.servicer = UserMissionServiceAPIServicer(
            self.expected_requests, self.expected_responses,
        )
        user_mission_service_api_pb2_grpc.add_UserMissionServiceAPIServicer_to_server(  # noqa: E501
            self.servicer, self.server,
        )


class SegmentMissionServiceAPIServicer(
        segment_mission_service_api_pb2_grpc.SegmentMissionServiceAPIServicer,  # noqa: E501
):
    def __init__(self, expected_requests, expected_responses):
        self.offset = 0
        self.expected_requests = expected_requests
        self.expected_responses = expected_responses
        super().__init__()

    # pylint: disable=invalid-name
    async def AssignMissionToSegment(self, request, context):
        pprint.pprint(request)
        pprint.pprint(self.expected_requests)
        pprint.pprint(self.expected_responses)
        for name, value in self.expected_requests[self.offset].items():
            assert getattr(request, name) == value

        response = (
            segment_mission_service_api_pb2.AssignMissionToSegmentResponse(
                **self.expected_responses[self.offset],
            )
        )
        self.offset += 1
        return response


class UserMissionServiceAPIServicer(
        user_mission_service_api_pb2_grpc.UserMissionServiceAPIServicer,
):
    def __init__(self, expected_requests, expected_responses):
        self.offset = 0
        self.get_missions_called = 0
        self.assign_mission_called = 0
        self.delete_mission_called = 0
        self.accept_missions_called = 0
        self.expected_requests = expected_requests
        self.expected_responses = expected_responses
        super().__init__()

    # pylint: disable=invalid-name
    async def GetUserMissions(self, request, context):
        self.get_missions_called += 1
        pprint.pprint(request)
        pprint.pprint(self.expected_requests)
        pprint.pprint(self.expected_responses)
        for name, value in self.expected_requests[self.offset].items():
            assert getattr(request, name) == value

        response = user_mission_service_api_pb2.GetUserMissionsResponse(
            **self.expected_responses[self.offset],
        )
        self.offset += 1
        return response

    # pylint: disable=invalid-name
    async def AssignMissionToUser(self, request, context):
        self.assign_mission_called += 1
        pprint.pprint(request)
        pprint.pprint(self.expected_requests)
        pprint.pprint(self.expected_responses)
        for name, value in self.expected_requests[self.offset].items():
            assert getattr(request, name) == value

        response = user_mission_service_api_pb2.AssignMissionToUserResponse(
            **self.expected_responses[self.offset],
        )
        self.offset += 1
        return response

    # pylint: disable=invalid-name
    async def DeleteMission(self, request, context):
        self.delete_mission_called += 1
        pprint.pprint(request)
        pprint.pprint(self.expected_requests)
        pprint.pprint(self.expected_responses)
        for name, value in self.expected_requests[self.offset].items():
            assert getattr(request, name) == value

        response = user_mission_service_api_pb2.DeleteMissionResponse(
            **self.expected_responses[self.offset],
        )
        self.offset += 1
        return response

    # pylint: disable=invalid-name
    async def AcceptUserMissions(self, request, context):
        self.accept_missions_called += 1
        pprint.pprint(request)
        pprint.pprint(self.expected_requests)
        pprint.pprint(self.expected_responses)
        for name, value in self.expected_requests[self.offset].items():
            assert getattr(request, name) == value

        response = user_mission_service_api_pb2.AcceptUserMissionsResponse(
            **self.expected_responses[self.offset],
        )
        self.offset += 1
        return response


@pytest.fixture(name='mock_mc_segment_mission_service')
async def _mock_mc_segment_mission_service(_grpc_port):
    SegmentMissionServiceServer.port = _grpc_port
    return SegmentMissionServiceServer


@pytest.fixture(name='mock_mc_user_mission_service')
async def _mock_mc_user_mission_service(_grpc_port):
    UserMissionServiceServer.port = _grpc_port
    return UserMissionServiceServer


def compare_dct_lists(list1, list2, excluded_fields: Set[str] = None):
    def remove_fields(lst):
        return [
            {key: value}
            for dct in lst
            for key, value in dct.items()
            if key not in excluded_fields
        ]

    if excluded_fields:
        list1 = remove_fields(list1)
        list2 = remove_fields(list2)

    def dct_comparator(dct):
        return [str(dct[key]) for key in sorted(dct.keys(), reverse=True)]

    assert sorted(list1, key=dct_comparator) == sorted(
        list2, key=dct_comparator,
    )


@pytest.fixture(name='compare_dct_lists')
def _compare_dct_lists():
    return compare_dct_lists
