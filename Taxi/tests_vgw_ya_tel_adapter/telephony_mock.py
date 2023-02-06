import dataclasses
import datetime
import logging
import math
import typing
import uuid

from google.protobuf import duration_pb2
from google.protobuf import empty_pb2
from google.protobuf import timestamp_pb2
from google.protobuf import wrappers_pb2
import grpc
import pytz
import telephony_platform_pb2 as tel_pb  # pylint: disable=E0401
import telephony_platform_pb2_grpc as tel_pb_grpc  # pylint: disable=E0401

from tests_vgw_ya_tel_adapter import consts


logger = logging.getLogger(__name__)


@dataclasses.dataclass()
class MockedYaTelData:
    redirections: typing.Dict[str, typing.Any]
    service_numbers: typing.Dict[str, typing.Any]


class TelephonyPlatformServiceServicer(
        tel_pb_grpc.TelephonyPlatformServiceServicer,
):
    """Telephony Platform gRPC API mock. Trying to simulate actual service."""

    def __init__(
            self,
            ya_tel_data: MockedYaTelData,
            now: datetime.datetime,
            tvm_ticket: str,
            tel_ticket: str,
    ):
        self._redirections = ya_tel_data.redirections
        self._service_numbers = ya_tel_data.service_numbers
        self._now = now.replace(tzinfo=pytz.utc)
        self._tvm_ticket = tvm_ticket
        self._tel_ticket = tel_ticket

    # pylint: disable=invalid-name
    async def createRedirections(
            self,
            request: tel_pb.CreateRedirectionsRequest,
            context: grpc.aio.ServicerContext,
    ) -> tel_pb.RedirectionList:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('createRedirections request:\n%s', request)
        assert len(request.list) == 1
        req_red = request.list[0]
        db_red = self._redirections.get(req_red.redirectionID)

        if db_red is None or not _dtm_info_less(
                _dtm_info(self._now), db_red['expires'],
        ):
            timedelta = datetime.timedelta(
                seconds=req_red.durationToExpire.seconds,
                microseconds=req_red.durationToExpire.nanos // 1000,
            )
            logger.info('createRedirections timedelta: %s', timedelta)
            if (
                    timedelta > datetime.timedelta(days=30)
                    or timedelta < datetime.timedelta()
            ):
                logger.error('createRedirections: invalid argument')
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(
                    'Duration to expire is required and cannot '
                    'be more than 30 days',
                )
                return tel_pb.RedirectionList()

            service_nums = [
                (num_id, num)
                for num_id, num in self._service_numbers.items()
                if num['geo_code'] in request.geoCodes
                and num['label'] == request.label
                and num['count'] > 0
                and (
                    not request.providers
                    or num['provider'] in request.providers
                )
                and num['state'] == tel_pb.ServiceNumberState.ACTIVE
            ]
            if not service_nums:
                logger.error('createRedirections: not found')
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Not found numbers by request')
                return tel_pb.RedirectionList()
            service_nums = sorted(service_nums)
            service_num_id, service_num = service_nums[0]
            service_num['count'] -= 1
            next_ext = service_num['next_ext']
            service_num['next_ext'] += 1

            db_red = {
                'callee': req_red.calleeNum,
                'expires': _dtm_info(self._now + timedelta),
                'ext': next_ext,
                'service_number_id': service_num_id,
                'updated': _dtm_info(self._now),
            }
            self._redirections[req_red.redirectionID] = db_red

        response = tel_pb.RedirectionList(
            list=[
                _redirection_to_proto(
                    req_red.redirectionID, db_red, self._service_numbers,
                ),
            ],
        )
        logger.info('createRedirections response:\n%s', response)
        return response

    async def getRedirections(
            self,
            request: tel_pb.RedirectionRequest,
            context: grpc.aio.ServicerContext,
    ) -> tel_pb.RedirectionList:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('getRedirections request:\n%s', request)
        redirections = []
        if request.HasField('redirectionIDs'):
            redirections = [
                _redirection_to_proto(
                    red_id, self._redirections[red_id], self._service_numbers,
                )
                for red_id in getattr(request, 'redirectionIDs').ids
                if red_id in self._redirections
            ]
        elif request.HasField('filter'):
            updated = request.filter.updated
            updated_from = (
                getattr(updated, 'from') if updated.HasField('from') else None
            )
            updated_to = updated.to if updated.HasField('to') else None
            for red_id, db_red in self._redirections.items():
                ok = True
                if updated_from:
                    ok = ok and _dtm_info_less(
                        _dtm_info_from_proto(updated_from), db_red['updated'],
                    )
                if updated_to:
                    ok = ok and _dtm_info_less(
                        db_red['updated'], _dtm_info_from_proto(updated_to),
                    )
                if not request.filter.withExpired:
                    ok = ok and _dtm_info_less(
                        _dtm_info(self._now), db_red['expires'],
                    )
                    if 'removed' in db_red:
                        ok = ok and _dtm_info_less(
                            _dtm_info(self._now), db_red['removed'],
                        )
                if ok:
                    redirections.append(
                        _redirection_to_proto(
                            red_id, db_red, self._service_numbers,
                        ),
                    )

        response = tel_pb.RedirectionList(list=redirections)
        logger.info('getRedirections response:\n%s', response)
        return response

    async def removeRedirections(
            self, request: tel_pb.EntityIDs, context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('removeRedirections request:\n%s', request)
        assert len(request.ids) == 1
        for red_id in request.ids:
            if red_id in self._redirections:
                logger.info('removeRedirections id=%s', red_id)
                self._redirections[red_id]['updated'] = _dtm_info(self._now)
                self._redirections[red_id]['deleted'] = _dtm_info(self._now)
        return empty_pb2.Empty()

    async def getServiceNumbers(
            self,
            request: tel_pb.ServiceNumbersRequest,
            context: grpc.aio.ServicerContext,
    ) -> tel_pb.ServiceNumbersList:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('getServiceNumbers request:\n%s', request)
        response = tel_pb.ServiceNumbersList()
        if request.HasField('serviceNumberIDs'):
            logger.info('getServiceNumbers request with serviceNumberIDs')
            service_number_count = len(request.serviceNumberIDs.ids)
            if service_number_count > consts.SERVICE_NUM_BATCH_LIMIT:
                logger.error('getServiceNumbers invalid argument')
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Batch limit exceed')
            else:
                response = tel_pb.ServiceNumbersList(
                    numbers=[
                        tel_pb.ServiceNumber(
                            serviceNumberID=num_id,
                            num=num['number'],
                            label=num['label'],
                        )
                        for num_id, num in self._service_numbers.items()
                        if num_id in request.serviceNumberIDs.ids
                    ],
                )
        else:
            logger.info('getServiceNumbers request with filter')
            if request.filter.count > consts.SERVICE_NUM_BATCH_LIMIT:
                logger.error('getServiceNumbers invalid argument')
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Batch limit exceed')
            else:
                numbers = [
                    tel_pb.ServiceNumber(
                        serviceNumberID=num_id,
                        num=num['number'],
                        label=num['label'],
                    )
                    for num_id, num in self._service_numbers.items()
                    if num['dial_code'] == request.filter.regionCode
                    and (
                        request.filter.state
                        == tel_pb.ServiceNumberState.ANY_STATE
                        or num['state'] == request.filter.state
                    )
                ]
                response = tel_pb.ServiceNumbersList(
                    numbers=numbers[
                        request.filter.offset : request.filter.offset
                        + request.filter.count
                    ],
                )
        logger.info('getServiceNumbers response:\n%s', response)
        return response

    async def activateServiceNumberRedirections(
            self,
            request: tel_pb.ActivateServiceNumberRedirectionRequest,
            context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('activateServiceNumberRedirections request:\n%s', request)
        if len(request.serviceNumberIDs) > consts.SERVICE_NUM_BATCH_LIMIT:
            logger.error('activateServiceNumberRedirections invalid argument')
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Batch limit exceed')
            return tel_pb.ServiceNumbersList()
        for num_id in request.serviceNumberIDs:
            num = self._service_numbers[num_id]
            if num.get('locked'):
                logger.error(
                    'activateServiceNumberRedirections invalid argument',
                )
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Number is locked')
                return tel_pb.ServiceNumbersList()
            num['state'] = tel_pb.ServiceNumberState.ACTIVE
            if request.label:
                assert request.label == 'new_pool'
                assert request.promptPlaybackID == 'prompt_playback_id'
                assert (
                    request.incorrectInputPlaybackID
                    == 'incorrect_input_playback_id'
                )
                assert (
                    request.correctInputPlaybackID
                    == 'correct_input_playback_id'
                )
                if request.HasField('beforeConnectedPlaybackID'):
                    assert (
                        request.beforeConnectedPlaybackID
                        == wrappers_pb2.StringValue(
                            value='before_connected_playback_id',
                        )
                    )
                if request.HasField('beforeConversationPlaybackID'):
                    assert (
                        request.beforeConversationPlaybackID
                        == wrappers_pb2.StringValue(
                            value='before_conversation_playback_id',
                        )
                    )
                if request.HasField('dialTimeout'):
                    assert request.dialTimeout.seconds == 30
                num['label'] = request.label
        return empty_pb2.Empty()

    async def deactivateServiceNumberRedirections(
            self,
            request: tel_pb.DeactivateServiceNumberRedirectionRequest,
            context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info(
            'deactivateServiceNumberRedirections request:\n%s', request,
        )
        if len(request.ids) > consts.SERVICE_NUM_BATCH_LIMIT:
            logger.error(
                'deactivateServiceNumberRedirections invalid argument',
            )
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Batch limit exceed')
            return tel_pb.ServiceNumbersList()
        assert request.skipActiveRedirectionsCheck
        for num_id in request.ids:
            num = self._service_numbers[num_id]
            if num.get('locked'):
                logger.error(
                    'deactivateServiceNumberRedirections invalid argument',
                )
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Number is locked')
                return tel_pb.ServiceNumbersList()
            num['state'] = tel_pb.ServiceNumberState.REMOVED
        return empty_pb2.Empty()

    async def updateServiceNumber(
            self,
            request: tel_pb.UpdateServiceNumberRequest,
            context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('updateServiceNumber request:\n%s', request)
        num = self._service_numbers[request.serviceNumberID]
        if num.get('locked'):
            logger.error('updateServiceNumber invalid argument')
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Number is locked')
            return tel_pb.ServiceNumbersList()
        assert request.updateData.label == num['label']
        if request.updateData.shouldSendToQuarantine:
            assert not request.updateData.shouldRemoveFromQuarantine
            num['state'] = tel_pb.ServiceNumberState.IN_QUARANTINE
        if request.updateData.shouldRemoveFromQuarantine:
            assert not request.updateData.shouldSendToQuarantine
            num['state'] = tel_pb.ServiceNumberState.ACTIVE
        return empty_pb2.Empty()

    async def updateServiceSettings(
            self,
            request: tel_pb.UpdateServiceSettingsRequest,
            context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        self._check_grpc_headers(dict(context.invocation_metadata()))
        logger.info('updateServiceSettings request:\n%s', request)
        if request.HasField('quarantineDuration'):
            assert request.quarantineDuration == duration_pb2.Duration(
                seconds=1234,
            )
        if request.HasField('dialPlaybackSettings'):
            assert request.dialPlaybackSettings.isEnabled
            if request.dialPlaybackSettings.data:
                expected_data_list = [
                    {
                        'dial_result': tel_pb.DialResult.DIAL_REJECTED,
                        'playback_id': 'rejected_playback_id',
                    },
                    {
                        'dial_result': tel_pb.DialResult.DIAL_REJECTED,
                        'tone': tel_pb.DefaultTone.UNSPECIFIED,
                    },
                    {
                        'dial_result': tel_pb.DialResult.DIAL_UNAVAILABLE,
                        'playback_id': 'unavailable_playback_id',
                    },
                    {
                        'dial_result': tel_pb.DialResult.DIAL_NO_ANSWER,
                        'tone': tel_pb.DefaultTone.BUSY,
                    },
                    {
                        'dial_result': tel_pb.DialResult.DIAL_PAYMENT_REQUIRED,
                        'playback_id': 'payment_required_playback_id',
                    },
                    {
                        'dial_result': tel_pb.DialResult.DIAL_INVALID_NUMBER,
                        'tone': tel_pb.DefaultTone.BUSY_OVERLOAD,
                    },
                ]
                for data, expected_data in zip(
                        request.dialPlaybackSettings.data, expected_data_list,
                ):
                    assert data.dialResult == expected_data['dial_result']
                    if data.action.HasField('tone'):
                        assert data.action.tone == expected_data['tone']
                    else:
                        assert (
                            data.action.playbackId
                            == expected_data['playback_id']
                        )

        return empty_pb2.Empty()

    def _check_grpc_headers(self, headers: typing.Dict[str, str]):
        assert uuid.UUID(headers['x-request-id'])
        assert headers['x-ya-service-ticket'] == self._tvm_ticket
        assert headers['x-telephony-ticket-id'] == self._tel_ticket


def _dtm_info(dtm: datetime.datetime) -> typing.Dict[str, typing.Any]:
    return {
        'nanos': dtm.microsecond * 1000,
        'seconds': math.floor(dtm.timestamp()),
        'timestring': dtm.isoformat(),
    }


def _redirection_to_proto(
        red_id: str, db_red: typing.Dict[str, typing.Any], service_numbers,
) -> tel_pb.Redirection:
    return tel_pb.Redirection(
        redirectionID=red_id,
        serviceNumberID=db_red['service_number_id'],
        calleeNum=db_red['callee'],
        ext=str(db_red['ext']),
        created=timestamp_pb2.Timestamp(
            seconds=db_red['updated']['seconds'],
            nanos=db_red['updated']['nanos'],
        ),
        updated=timestamp_pb2.Timestamp(
            seconds=db_red['updated']['seconds'],
            nanos=db_red['updated']['nanos'],
        ),
        expiredAt=timestamp_pb2.Timestamp(
            seconds=db_red['expires']['seconds'],
            nanos=db_red['expires']['nanos'],
        ),
        removedAt=timestamp_pb2.Timestamp(
            seconds=db_red['removed']['seconds'],
            nanos=db_red['removed']['nanos'],
        )
        if 'removed' in db_red
        else None,
        serviceNumberLabel=service_numbers[db_red['service_number_id']][
            'label'
        ],
        serviceNumberNum=service_numbers[db_red['service_number_id']][
            'number'
        ],
    )


def _dtm_info_from_proto(
        proto: timestamp_pb2.Timestamp,
) -> typing.Dict[str, typing.Any]:
    dtm = datetime.datetime.utcfromtimestamp(0) + datetime.timedelta(
        seconds=proto.seconds, microseconds=proto.nanos // 1000,
    )
    return _dtm_info(dtm)


def _dtm_info_less(
        datetime_info_1: typing.Dict[str, typing.Any],
        datetime_info_2: typing.Dict[str, typing.Any],
) -> bool:
    return datetime_info_1['seconds'] < datetime_info_2['seconds'] or (
        datetime_info_1['seconds'] == datetime_info_2['seconds']
        and datetime_info_1['nanos'] < datetime_info_2['nanos']
    )
