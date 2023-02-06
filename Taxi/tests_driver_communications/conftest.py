# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy
import datetime

import pytest

from driver_communications_plugins import *  # noqa: F403 F401

from tests_driver_communications import consts


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


class FeedsContext:
    def __init__(self, load_json):
        self.feeds = {'driver-wall': {}}
        self.response = {consts.DEFAULT: {}}
        self.headers = {consts.DEFAULT: {}}
        self.status = {consts.DEFAULT: 200}
        self.load_json = load_json
        self.limit = 1000
        self.service_override = {}

    def set_default_feeds(self, feeds_service='driver-wall'):
        if feeds_service not in self.feeds:
            self.feeds[feeds_service] = {}
        feeds_list = [consts.TEXT_TITLE_IMAGE_PARENT, consts.NO_META]
        for elem in feeds_list:
            feed_id = consts.FEED_ID_MAP[elem]
            self.feeds[feeds_service][feed_id] = self.load_json(elem + '.json')

    def set_feeds(self, feeds_type, feeds_service='driver-wall'):
        if feeds_service not in self.feeds:
            self.feeds[feeds_service] = {}
        for elem in feeds_type:
            feed_id = consts.FEED_ID_MAP[elem]
            self.feeds[feeds_service][feed_id] = self.load_json(elem + '.json')

    def set_response(
            self,
            response,
            status=200,
            headers=None,
            handler=consts.DEFAULT,
            service=None,
    ):
        if service is None:
            self.response[handler] = response
            self.status[handler] = status
            self.headers[handler] = headers
            return
        self.service_override[service] = {
            'response': {},
            'status': {},
            'headers': {},
        }
        self.service_override[service]['response'][handler] = response
        self.service_override[service]['status'][handler] = status
        self.service_override[service]['headers'][handler] = headers

    def set_error(self, status=500, headers=None, handler=consts.DEFAULT):
        self.response[handler] = dict(statusCode=status, errorMessages=[])
        self.status[handler] = status
        self.headers[handler] = headers

    def set_limit(self, limit):
        self.limit = limit

    def clear(self):
        self.feeds = {}


@pytest.fixture(name='mock_feeds', autouse=True)
def feeds_request(mockserver, load_json):
    context = FeedsContext(load_json)

    @mockserver.json_handler('/feeds/v1/fetch')
    def _fetch(request):
        handler = 'v1/fetch'
        if context.status.get(handler, context.status[consts.DEFAULT]) == 200:
            assert 'taximeter:City:МОСКВА' in request.json['channels']
            assert 'taximeter:Driver:db1:uuid1' in request.json['channels']
            assert 'taximeter:Park:db1' in request.json['channels']
            assert 'taximeter:Country:РОССИЯ' in request.json['channels']
            # assert len(request.json['channels']) == 4
        service = request.json['service']
        if service in context.service_override:
            return mockserver.make_response(
                json=context.service_override[service]['response'].get(
                    handler, context.response[consts.DEFAULT],
                ),
                status=context.service_override[service]['status'].get(
                    handler, context.status[consts.DEFAULT],
                ),
                headers=context.service_override[service]['headers'].get(
                    handler, context.headers[consts.DEFAULT],
                ),
            )

        response = {
            'has_more': False,
            'etag': '12345',
            'polling_delay': 3,
            'feed': [],
        }
        if request.json['service'] in context.feeds:
            for _, feed in context.feeds[request.json['service']].items():
                if 'newer_than' in request.json:
                    created = datetime.datetime.strptime(
                        feed['created'][0:24], '%Y-%m-%dT%H:%M:%S.%f',
                    )
                    newer_than = datetime.datetime.strptime(
                        request.json['newer_than'][0:24],
                        '%Y-%m-%dT%H:%M:%S.%f',
                    )
                    if created > newer_than:
                        response['feed'].append(feed)
                elif 'earlier_than' in request.json:
                    created = datetime.datetime.strptime(
                        feed['created'][0:24], '%Y-%m-%dT%H:%M:%S.%f',
                    )
                    earlier_than = datetime.datetime.strptime(
                        request.json['earlier_than'][0:24],
                        '%Y-%m-%dT%H:%M:%S.%f',
                    )
                    if created < earlier_than:
                        response['feed'].append(feed)
                else:
                    response['feed'].append(feed)
        response['feed'] = sorted(
            response['feed'],
            key=lambda feed: datetime.datetime.strptime(
                feed['created'][0:24], '%Y-%m-%dT%H:%M:%S.%f',
            ),
        )
        response['feed'].reverse()
        response['feed'] = response['feed'][0 : context.limit + 1]
        return mockserver.make_response(
            json=response,
            status=context.status.get(handler, context.status[consts.DEFAULT]),
            headers=context.headers.get(
                handler, context.headers[consts.DEFAULT],
            ),
        )

    @mockserver.json_handler('/feeds/v1/batch/log_status')
    def _batch_status_log(request):
        items = []
        for message in request.json['items']:
            channel = message['channel']
            assert channel == 'taximeter:Driver:db1:uuid1'
            feed_id = message['feed_id']
            status = message['status']
            meta = message.get('meta', None)
            feeds_service = context.feeds[message['service']]
            if feed_id in feeds_service:
                feeds_service[feed_id]['last_status']['status'] = status
                if meta is not None:
                    feeds_service[feed_id]['meta'] = meta
                items.append({feed_id: 200})
            else:
                items.append({feed_id: 404})
        return mockserver.make_response(json={'items': items}, status=200)

    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def _fetch_by_id(request):
        requested_feeds = []
        result_feeds = []
        feeds_service = context.feeds[request.json['service']]
        if 'feed_id' in request.json:
            requested_feeds.append(request.json['feed_id'])
        if 'feed_ids' in request.json:
            requested_feeds = request.json['feed_ids']
        for feed_id in requested_feeds:
            if feed_id in feeds_service:
                result_feeds.append(feeds_service[feed_id])
        if result_feeds or 'feed_ids' in request.json:
            return mockserver.make_response(
                json={'feed': result_feeds}, status=200,
            )
        return mockserver.make_response(
            json={'code': '404', 'message': 'not found'}, status=404,
        )

    @mockserver.json_handler('/feeds/v1/create')
    def _create(request):
        channels = request.json['channels']
        service = request.json['service']
        assert channels == [{'channel': 'taximeter:Driver:db1:uuid1'}]
        assert request.json['ignore_filters']
        assert request.json['status'] == 'read'
        assert 'parent_feed_id' in request.json
        assert (
            request.json['meta']['source_service'] == 'driver-communications'
        )
        new_feed = {
            # feed_id for mock, feeds generate feed_id themselvs
            'feed_id': 'f6dc672653aa443d9ecf48cc5ef4cb22',
            'created': '2020-06-01T11:49:15.277047+0000',
            'last_status': {
                'status': 'read',
                'created': '2020-06-02T12:09:51.189807+0000',
            },
            'payload': request.json['payload'],
            'meta': request.json['meta'],
        }
        context.feeds[request.json['service']][
            'f6dc672653aa443d9ecf48cc5ef4cb22'
        ] = new_feed
        return mockserver.make_response(
            json={
                'service': service,
                'filtered': [],
                'feed_ids': {
                    request.json['channels'][0][
                        'channel'
                    ]: 'f6dc672653aa443d9ecf48cc5ef4cb22',
                },
            },
            status=200,
        )

    @mockserver.json_handler('/feeds/v1/summary')
    def _summary(request):
        handler = 'v1/summary'
        if context.status.get(handler, context.status[consts.DEFAULT]) == 200:
            assert 'taximeter:City:МОСКВА' in request.json['channels']
            assert 'taximeter:Driver:db1:uuid1' in request.json['channels']
            assert 'taximeter:Park:db1' in request.json['channels']
            assert 'taximeter:Country:РОССИЯ' in request.json['channels']
        published = 0
        viewed = 0
        total = 0
        read = 0
        feeds_service = context.feeds.get(request.json['service'], {})
        for _, feed in feeds_service.items():
            total += 1
            if feed['last_status']['status'] == 'published':
                published += 1
            elif feed['last_status']['status'] == 'viewed':
                viewed += 1
            elif feed['last_status']['status'] == 'read':
                read += 1
        response = {
            'counts': {
                'published': published,
                'viewed': viewed,
                'total': total,
                'read': read,
                'removed': 0,
            },
        }
        return mockserver.make_response(
            json=response,
            status=context.status.get(handler, context.status[consts.DEFAULT]),
            headers=context.headers.get(
                handler, context.headers[consts.DEFAULT],
            ),
        )

    return context


class SupportChatContext:
    def __init__(self, load_json):
        self.basic = load_json('support_chat_prequisites.json')
        self.messages = []
        self.responses = {}
        self.passed_dkvu = True

    def set_passed_dkvu(self, status_dkvu):
        self.passed_dkvu = status_dkvu

    def set_response(self, response, handler='search', code=200):
        self.responses[handler] = {'response': response, 'code': code}

    def update_basic(self, full_message, reply_to=None, attachments=None):
        if reply_to is not None:
            full_message['metadata']['reply_to'] = reply_to
        if attachments is not None:
            full_message['metadata']['attachments'] = []
            for attach_id in attachments:
                full_message['metadata']['attachments'].append(
                    {
                        'id': attach_id,
                        'mimetype': 'image/jpeg',
                        'name': '/private/var/mobile.json',
                        'preview_height': 200,
                        'preview_width': 112,
                        'size': 68992,
                        'source': 'mds',
                    },
                )
        self.messages.append(full_message)
        self.basic['newest_message_id'] = self.messages[-1]['id']
        self.basic['messages'] = self.messages

    def create_support_response(
            self, message_text, created, reply_to=None, attachments=None,
    ):
        message_id = 'message_id' + str(len(self.messages))
        full_message = {
            'id': message_id,
            'metadata': {
                'created': created,
                'custom_fields': consts.DEFAULT_CUSTOM_FIELDS,
            },
            'sender': {'id': 'support', 'role': 'support'},
            'text': message_text,
        }
        self.basic['metadata']['new_messages'] += 1
        self.update_basic(full_message, reply_to, attachments)

    def create(
            self,
            message_text,
            created,
            reply_to=None,
            attachments=None,
            communication_client_id=None,
    ):
        message_id = 'message_id' + str(len(self.messages))
        full_message = {
            'id': message_id,
            'metadata': {
                'created': created,
                'custom_fields': consts.DEFAULT_CUSTOM_FIELDS,
                'communication_client_id': communication_client_id,
            },
            'sender': {'id': 'driver', 'role': 'driver'},
            'text': message_text,
        }
        self.update_basic(full_message, reply_to, attachments)

    def read(self):
        self.basic['metadata']['new_messages'] = 0

    def set_csat(self):
        self.basic['csat_dialog'] = {
            'answers': [copy.deepcopy(consts.CSAT_MARK)],
            'new_messages_count': 1,
        }

    def set_csat_mark_reply(self, action_id, date):
        actions = self.basic['csat_dialog']['answers'][-1]['actions']
        self.basic['csat_dialog']['new_messages_count'] = 1
        for action in actions:
            if action['id'] == action_id:
                action['answered'] = date
        if action_id.startswith('mark'):
            self.basic['csat_dialog']['answers'].append(
                copy.deepcopy(consts.CSAT_REASON),
            )
        elif action_id.startswith('reason'):
            self.basic['csat_dialog']['answers'].append(
                copy.deepcopy(consts.CSAT_FINISH),
            )
        elif action_id.startswith('exit'):
            del self.basic['csat_dialog']
            if action_id == 'exit2':
                self.basic['messages'] = []
                self.messages = None
            return
        elif action_id == 'transition2':
            self.basic['csat_dialog']['answers'] = [
                self.basic['csat_dialog']['answers'][0],
            ]
            self.basic['csat_dialog']['answers'].append(
                copy.deepcopy(consts.CSAT_REASON),
            )
        else:
            self.basic['csat_dialog']['answers'] = [
                copy.deepcopy(consts.CSAT_MARK),
            ]
        self.basic['csat_dialog']['answers'][-1][
            'created'
        ] = datetime.datetime.now(datetime.timezone.utc).isoformat()


def support_common_check(request, passed_dkvu):
    if passed_dkvu:
        assert request.json['owner']['id'] == 'unique_driver_id1'
    else:
        assert request.json['owner']['id'] == 'uuid1'
    assert request.json['owner']['role'] == 'driver'
    assert request.json['owner']['platform'] == 'taximeter'


@pytest.fixture(name='mock_support_chat', autouse=True)
def support_chat_request(mockserver, load_json):
    context = SupportChatContext(load_json)

    @mockserver.json_handler('/support-chat/v1/chat/search')
    def _search(request):
        handler = 'search'
        support_common_check(request, context.passed_dkvu)
        if handler in context.responses:
            response = context.responses[handler]
            return mockserver.make_response(
                json=response['response'], status=response['code'],
            )
        if not context.messages:
            return mockserver.make_response(
                status=200, json={'chats': [], 'total': 0},
            )
        return mockserver.make_response(
            status=200, json={'chats': [context.basic], 'total': 1},
        )

    @mockserver.json_handler('/support-chat/v1/chat/attach_file')
    def _attach(request):
        handler = 'attach'
        response = context.responses[handler]
        return mockserver.make_response(
            json=response['response'], status=response['code'],
        )

    @mockserver.json_handler('/support-chat/v1/chat/12345/read')
    def _read(request):
        handler = 'read'
        support_common_check(request, context.passed_dkvu)
        if handler in context.responses:
            response = context.responses[handler]
            return mockserver.make_response(
                json=response['response'], status=response['code'],
            )
        context.read()
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/support-chat/v1/chat')
    def _create(request):
        handler = 'create'
        support_common_check(request, context.passed_dkvu)
        assert request.json['metadata']['user_application'] == 'taximeter'
        assert request.json['metadata']['user_country'] == 'rus'
        assert request.json['metadata']['db'] == 'db1'
        assert request.json['metadata']['driver_uuid'] == 'uuid1'
        assert 'communication_client_id' in request.json['message']['metadata']
        assert request.json['message']['metadata']['appeal_source'] == 'order'
        assert request.json['message']['metadata']['work_mode'] == 'some_mode'
        assert request.json['message']['metadata']['driver_on_order']
        assert request.json['create_chatterbox_task']
        if handler in context.responses:
            response = context.responses[handler]
            return mockserver.make_response(
                json=response['response'], status=response['code'],
            )
        reply_to = None
        attachments = None
        communication_client_id = request.json['message']['metadata'][
            'communication_client_id'
        ]
        if 'attachments' in request.json['message']['metadata']:
            attachments = []
            for attach_id in request.json['message']['metadata'][
                    'attachments'
            ]:
                attachments.append(attach_id['id'])
        if 'reply_to' in request.json['message']['metadata']:
            reply_to = request.json['message']['metadata']['reply_to']
        context.create(
            request.json['message']['text'],
            (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=1)
            ).isoformat(),
            reply_to=reply_to,
            attachments=attachments,
            communication_client_id=communication_client_id,
        )
        return mockserver.make_response(json=context.basic, status=200)

    @mockserver.json_handler('/support-chat/v1/chat/12345/csat')
    def _csat(request):
        handler = 'csat'
        if handler in context.responses:
            response = context.responses[handler]
            return mockserver.make_response(
                json=response['response'], status=response['code'],
            )
        context.set_csat_mark_reply(
            request.json['action_id'],
            datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        body = {'answers': []}
        if 'csat_dialog' in context.basic:
            body['answers'].append(context.basic['csat_dialog']['answers'][-1])
        return mockserver.make_response(status=200, json=body)

    return context


@pytest.fixture(name='mock_driver_diagnostics')
def mock_unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.is_enabled = True
            self.mock_categories_restrictions = {}

        def set_enabled(self, is_enabled):
            self.is_enabled = is_enabled

    context = Context()

    @mockserver.json_handler(consts.MOCK_DRIVER_DIAGNOSTICS_HANDLER)
    def _mock_categories_restrictions(request):
        return {
            'categories': [
                {'name': 'qc_block', 'is_enabled': context.is_enabled},
            ],
        }

    context.mock_categories_restrictions = _mock_categories_restrictions

    return context


@pytest.fixture(name='mock_driver_trackstory')
def driver_trackstory_(mockserver):
    class Context:
        def __init__(self):
            self.data = {}
            self.excluded_drivers = set()

        def set_data(self, driver_id, lon, lat):
            self.data[driver_id] = {'lon': lon, 'lat': lat}

        def exclude_driver(self, driver_id):
            self.excluded_drivers.add(driver_id)

    context = Context()

    @mockserver.json_handler('driver-trackstory/positions')
    def _positions(request):
        result = []
        for driver_id in request.json['driver_ids']:
            if driver_id not in context.excluded_drivers:
                data = context.data.get(driver_id, {'lon': 37.5, 'lat': 55.5})
                result.append(
                    {
                        'driver_id': driver_id,
                        'position': {
                            'lon': data['lon'],
                            'lat': data['lat'],
                            'timestamp': 1607635209,
                        },
                        'type': 'raw',
                    },
                )
        return {'results': result}

    return context
