# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import urlparse
import uuid

import bson
import pytest

from taxi.external import zendesk


from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal import driver_manager
from taxi.internal import zendesk_forms
from taxi.internal import user_manager
from taxi.internal import user_support_chat
from taxi.internal import experiment_manager
from taxi.internal.order_kit import feedback_report
from taxi.external import archive
from taxi.external import pymlaas
from taxi.external import tvm

TRANSLATIONS = [
    ('zendesk_forms', 'invalid', 'ru', 'txt'),
    ('tariff', 'detailed.minutes', 'ru', u'%(value).0f мин'),
    ('tariff', 'detailed.minute', 'ru', u'%(value).0f мин'),
    ('tariff', 'detailed.hour', 'ru', u'%(value).0f ч'),
    ('tariff', 'detailed.hours', 'ru', u'%(value).0f ч'),
    ('tariff', 'detailed.kilometers_meters', 'ru', u'%(value).3f км'),
    ('tariff', 'detailed.kilometers', 'ru', u'%(value).3f км'),
    ('tariff', 'detailed.kilometer', 'ru', u'%(value).3f км'),
    ('client_messages', 'feedback_choice.low_rating_reason.nochange',
     'ru', u'Не было сдачи'),
    ('client_messages', 'feedback_choice.low_rating_reason.car_condition',
     'ru', u'Состояние автомобиля'),
    ('client_messages', 'feedback_choice.low_rating_reason.driverlate',
     'ru', u'Водитель опоздал'),
    ('client_messages', 'feedback_choice.low_rating_reason.rudedriver',
     'ru', u'Грубый водитель'),
    ('client_messages', 'feedback_choice.low_rating_reason.smellycar',
     'ru', u'Запах в машине'),
    ('client_messages', 'feedback_choice.low_rating_reason.badroute',
     'ru', u'Ездил кругами'),
    ('client_messages', 'feedback_choice.low_rating_reason.notrip',
     'ru', u'Поездки не было'),
]
UUID = '00000000000040008000000000000000'


@pytest.fixture(autouse=True)
def patch_userapi_phone_id(patch):
    @patch('taxi.internal.userapi.get_user_phone')
    @async.inline_callbacks
    def impl(
            phone_id,
            primary_replica=False,
            fields=None,
            log_extra=None,
    ):
        doc = yield dbh.user_phones.Doc.find_one_by_id(
            phone_id,
            secondary=not primary_replica,
            fields=fields,
        )
        async.return_value(doc)


@pytest.fixture(autouse=True)
def patch_userapi_get_user_emails(patch):
    @patch('taxi.external.userapi.get_user_emails')
    @async.inline_callbacks
    def mock_userapi(
            brand,
            email_ids=None,
            phone_ids=None,
            yandex_uids=None,
            fields=None,
            primary_replica=False,
            log_extra=None,
    ):
        yield async.return_value(
            [
                {
                    'id': 'userphone1',
                    'phone_id': 'userphone1',
                    'confirmed': True,
                    'confirmation_code': 'code',
                    'personal_email_id': 'personal_email_id',
                },
            ],
        )


@pytest.fixture(autouse=True)
def patch_personal_retrieve(patch):
    @patch('taxi.external.personal.retrieve')
    @async.inline_callbacks
    def mock_personal(data_type, request_id, log_extra=None, **kwargs):
        yield async.return_value(
            {
                'id': request_id,
                'email': 'email',
            },
        )


@pytest.fixture
def mock_get_urgency(monkeypatch, mock):
    @mock
    @async.inline_callbacks
    def _dummy_get_urgency(request_data, log_extra=None):
        yield
        if request_data['comment'] == 'ужасно':
            async.return_value(0.8)
        async.return_value(0.2)

    monkeypatch.setattr(
        pymlaas,
        'urgent_comments_detection',
        _dummy_get_urgency
    )
    return _dummy_get_urgency


@pytest.fixture
def mock_detect_language(patch):
    @patch('taxi.external.translate.detect_language')
    @async.inline_callbacks
    def detect_language(text, log_extra=None):
        yield
        assert text
        async.return_value('ru')
    return detect_language


@pytest.fixture
def mock_get_tags(monkeypatch, mock):
    @mock
    @async.inline_callbacks
    def fake_get_tags_by_entity_id(entity_id, entity_type, src_service,
                                   tags_service, log_extra=None):
        yield
        if entity_id == 'blogger_license':
            async.return_value(['vip', 'blogger', 'other'])
        elif entity_id in ['userphone1']:
            async.return_value(['business_client'])
        else:
            async.return_value([])
    monkeypatch.setattr(
        'taxi.external.tags_service.get_tags_by_entity_id',
        fake_get_tags_by_entity_id,
    )

    return fake_get_tags_by_entity_id


@pytest.fixture(autouse=True)
def mock_meta_from_support_info(patch, request):
    if 'no_mock_support_info_meta' in request.keywords:
        return

    @patch('taxi.internal.order_kit.feedback_report.get_chatterbox_fields_from_py3')
    @async.inline_callbacks
    def _dummy_get_fields(*args, **kwargs):
        yield async.return_value({})


@pytest.fixture(autouse=True)
def patch_support_chat_ml_request_id(patch):
    @patch('taxi.internal.user_support_chat.get_ml_request_id')
    @async.inline_callbacks
    def get_ml_request_id(phone_id, platform, log_extra):
        yield async.return_value(UUID)


@pytest.fixture
def mock_uuid_uuid4(monkeypatch, mock):
    @mock
    def _dummy_uuid4():
        return uuid.UUID(int=0, version=4)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)


@pytest.fixture
def zclient(monkeypatch):

    class Client(object):
        id = None

    zclient = Client()

    def get_zendesk_client(id):
        zclient.id = id
        return zclient

    monkeypatch.setattr(
        zendesk, 'get_zendesk_client_by_id', get_zendesk_client
    )

    return zclient


@pytest.fixture
def forms_db(monkeypatch):

    class FormsDB(object):
        def __init__(self):
            self.data = {
                'msg1': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'comment': 'pay',
                        'field_52923': 'it is not bad comment',
                    },
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order1'
                },
                'msg2': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {},
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order1'
                },
                'msg3': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'field_52923': 'it is not bad comment',
                        'comment': u'pain было ужасно',
                        'field_52926': 'hello my friend',
                    },
                    'user_id': 'user_staff',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                },
                'msg4': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {},
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order1'
                },
                'msg5': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': u'не понравилось'},
                    'user_id': 'user_taxi',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                },
                'msg6': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': u'совсем не понравилось'},
                    'user_id': 'user_taxi',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                },
                'msg_without_driver': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {},
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order2'
                },
                'msg_without_driver_profile': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {},
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order1',
                },
                'msg_no_order': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {},
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order_not_exists'
                },
                'msg_custom_fields': {
                    'form_id': 2,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'field_1': 'comment',
                        'field_2': '2018-01-01T12:00:00Z',
                        'field_3': 'some_coupon',
                    },
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                },
                'msg_to_chatterbox': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber'
                },
                'msg_to_chatterbox_with_order': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber',
                    'order_id': 'order_id'
                },
                'msg_to_chatterbox_with_zone': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber',
                    'zone': 'moscow'
                },
                'msg_to_chatterbox_with_bad_zone': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber',
                    'zone': 'Москва'
                },
                'msg_to_chatterbox_with_phone_permission': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': None,
                    'pass_phone_permission': True,
                    'fields': {
                        'comment': 'pay',
                    },
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber',
                    'zone': 'Москва'
                },
                'msg_with_user_without_phone_id': {
                    'form_id': 1,
                    'phone': '+79000000000',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user_without_phone_id',
                    'authorized': True,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber',
                    'zone': 'moscow'
                },
                'msg_without_payment': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'field_52923': 'comment',
                    },
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'order_id': 'order1'
                },
                'msg_with_taxi_service': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'yandex',
                    'service': 'taxi',
                    'order_id': 'order1'
                },
                'msg_with_eats_service': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'comment': 'pay'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'yandex',
                    'service': 'eats',
                    'eats_order_id': 'eats_order_id'
                },
                'msg_with_carsharing_service': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'comment': 'pay',
                        'field_52923': 'it is not bad comment',
                    },
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'service': 'drive',
                    'order_id': 'order1',
                },
                'msg_with_attachments': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'comment': 'pay',
                        'field_52923': 'it is not bad comment',
                    },
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': ['some_attachment_id'],
                    'support_chat_attachments': [
                        {
                            'id': 'other_attachment_id',
                            'name': 'some.name',
                        },
                    ],
                    'order_id': 'order1',
                },
                'msg_with_user_comment': {
                    'form_id': 1,
                    'phone': '+79999999999',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {'user_comment': 'hello'},
                    'user_id': 'user1',
                    'authorized': False,
                    'locale': 'en',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': [],
                    'user_platform': 'uber',
                    'zone': 'moscow'
                },
                'msg_with_cyrillic_attachments': {
                    'form_id': 1,
                    'phone': '',
                    'source': zendesk_forms.SOURCE_APP,
                    'fields': {
                        'comment': 'pay',
                        'field_52923': 'it is not bad comment',
                    },
                    'user_id': 'user1',
                    'authorized': True,
                    'locale': 'ru',
                    'email': '',
                    'name': 'user_name',
                    'attachment_ids': ['cyrillic_attachment_id'],
                    'support_chat_attachments': [
                        {
                            'id': 'cyrillic_attachment_id',
                            'name': '\u0411\u0435\u0437 \u043d\u0430\u0437'
                                    '\u0432\u0430\u043d\u0438\u044f.pdf',
                        },
                    ],
                    'order_id': 'order1',
                },
            }

        def find_one(self, data):
            return self.data[data['_id']]

        def update(self, selector, operator):
            for k, v in operator.get('$set', {}).iteritems():
                self.data[selector['_id']][k] = v
            for k, v in operator.get('$currentDate', {}).iteritems():
                self.data[selector['_id']][k] = datetime.datetime.utcnow()

        def __getitem__(self, item):
            return self.data[item]

    res = FormsDB()
    monkeypatch.setattr(db, 'zendesk_form_integrations', res)
    return res


@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
)
@pytest.mark.parametrize(
    'message_id,is_urgent,is_payment',
    [
        ('msg3', True, True),
        ('msg1', False, True),
    ]
)
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_fetch_and_check_urgent_payment(forms_db, zclient, message_id,
                                        is_urgent, is_payment,
                                        mock_detect_language):

    form_data = yield db.zendesk_form_integrations.find_one({
        '_id': message_id
    })
    ctx = zendesk_forms.FormFeedbackContext()
    ctx.form_data = form_data
    ctx.message_id = message_id

    yield zendesk_forms.fetch_data_for_zendesk_form(ctx)
    assert ctx.urgent == is_urgent
    assert ctx.payment == is_payment
    assert ctx.ml_request_id is not None


@pytest.mark.config(
    FEEDBACK_CLIENT_TICKETS_ROUTING_PERCENTAGE=100,
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
)
@pytest.mark.parametrize(
    'message_id,predicted_class,is_urgent,use_routing',
    [
        ('msg_with_user_comment', 'urgent', True, True),
        ('msg_with_user_comment', 'other', False, True),
    ]
)
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_fetch_predicted_class(forms_db, zclient, message_id, predicted_class,
                               is_urgent, use_routing, mock_detect_language,
                               areq_request):

    @areq_request
    def request(method, url, **kwargs):
        return areq_request.response(
            200,
            body=json.dumps(
                {
                    'predicted_class_name': predicted_class,
                    'ml_class_name': 'ml_class',
                    'urgent_keywords_triggered': True,
                    'lost_item_second_keywords_triggered': True,
                    'probabilities': [0.0, 0.5, 1.0],
                },
            )
        )

    form_data = yield db.zendesk_form_integrations.find_one({
        '_id': message_id
    })
    ctx = zendesk_forms.FormFeedbackContext()
    ctx.form_data = form_data
    ctx.message_id = message_id

    yield zendesk_forms.fetch_data_for_zendesk_form(ctx)
    assert ctx.urgent == is_urgent
    assert ctx.use_client_tickets_routing_ml == use_routing
    if use_routing:
        assert ctx.chatterbox_fields['predicted_class_name'] == predicted_class


@pytest.mark.parametrize(
    'message_id,service,order_field,order_id',
    [
        ('msg_with_taxi_service', 'taxi', 'order_id', 'order1'),
        ('msg_with_eats_service', 'eats', 'eats_order_id', 'eats_order_id'),
    ]
)
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_check_service(forms_db, zclient, message_id, service, order_field,
                       order_id, mock_detect_language):

    form_data = yield db.zendesk_form_integrations.find_one({
        '_id': message_id
    })
    ctx = zendesk_forms.FormFeedbackContext()
    ctx.form_data = form_data
    ctx.message_id = message_id

    yield zendesk_forms.fetch_data_for_zendesk_form(ctx)
    assert ctx.custom_fields['service'] == service
    assert ctx.chatterbox_fields['service'] == service
    assert ctx.custom_fields[order_field] == order_id
    assert ctx.chatterbox_fields[order_field] == order_id
    assert ctx.chatterbox_fields['ticket_source'] == 'тикет_из_приложения'


@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
)
@pytest.mark.parametrize(
    'message_id,is_payment,zclient_calls',
    [
        ('msg3', True, [{
            'desc': True,
            'query_args': [
                u'type:ticket',
                u'created>30days'],
            'query_kwargs': {u'requester': u'+79000000001'},
            'sort_by': u'created_at'
        }]),
        ('msg_without_payment', False, []),
    ]
)
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_fetch_payment_data(forms_db, zclient, mock, message_id, is_payment,
                            zclient_calls, mock_detect_language):

    form_data = yield db.zendesk_form_integrations.find_one({
        '_id': message_id
    })
    ctx = zendesk_forms.FormFeedbackContext()
    ctx.form_data = form_data
    ctx.message_id = message_id

    yield zendesk_forms.fetch_data_for_zendesk_form(ctx)
    assert ctx.payment == is_payment


@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=[],  # don't use ml check urgent
)
@pytest.mark.parametrize(
    'comments,is_urgent,is_payment',
    [
        (['не все так плохо', 'ужасно', 'и тут не плохо'], True, False),
        (['не все так плохо', 'payment', 'и тут не плохо'], False, True),
        (['петя', 'вася', 'мариша'], False, False),
        (['петя', 'ужасно', 'мариша', 'payment'], True, True),
    ],
)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_check_urgent_by_keywords(comments, is_urgent, is_payment):

    ctx = zendesk_forms.FormFeedbackContext()
    ctx.user_country = 'rus'
    urgent, _, _, _ = yield feedback_report.check_urgent(
        ctx=ctx, texts=comments, request_id='request_id',
    )
    payment, _ = yield feedback_report.check_payment(
        ctx=ctx, texts=comments,
    )
    assert urgent == is_urgent
    assert payment == is_payment


@pytest.mark.parametrize(
    'comments,is_urgent',
    [
        (['urgent_comment', 'а эт не ургент коммент'], True),
        (['а эт не ургент коммент', 'и этот тоже'], False),
    ],
)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_check_urgent_from_ml(patch, mock, mock_detect_language, comments,
                              is_urgent):

    zendesk_form_ctx = zendesk_forms.FormFeedbackContext()

    @mock
    @patch('taxi.internal.order_kit.feedback_report.ml_check_urgent')
    @async.inline_callbacks
    def ml_check_urgent(ctx, text, request_id=None, log_extra=None):
        yield

        assert ctx is zendesk_form_ctx
        number_urgency = 0.0
        _is_urgent = False
        failed_request = False
        if text == 'urgent_comment':
            _is_urgent = True
            number_urgency = 0.8
        async.return_value((_is_urgent, number_urgency, failed_request))

    zendesk_form_ctx.user_country = 'rus'
    urgent, _, _, _ = yield feedback_report.check_urgent(
        ctx=zendesk_form_ctx,
        texts=comments,
        request_id='request_id',
    )
    assert urgent == is_urgent
    assert len(ml_check_urgent.calls) == len(comments)


@pytest.mark.parametrize('msg_id', [
    ('msg_without_driver_profile'),
])
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.config(FEEDBACK_EXTERNAL_TAGS_ENABLED=True)
def test_not_found_driver_profile(zclient, forms_db, msg_id, mock_get_urgency,
                                  mock_get_tags, monkeypatch, areq_request):

    monkeypatch.setattr(
        user_manager,
        'user_support_chat', lambda *args, **kwargs: True
    )

    def not_found_driver(*args, **kwargs):
        raise dbh.drivers.NotFound()

    monkeypatch.setattr(
        driver_manager,
        'get_driver_by_park_driver_id',
        not_found_driver
    )

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        request = kwargs['json']
        if 'support-chat' in url:
            json.dumps(request)
            assert url.startswith('http://support-chat.taxi.yandex.net')
            result = {'id': str(bson.ObjectId()), 'metadata': {}}
            return areq_request.response(200, body=json.dumps(result))
        if 'chatterbox' in url:
            json.dumps(request)
            assert url.startswith('http://chatterbox.taxi.yandex.net')
            result = {'id': str(bson.ObjectId()), 'metadata': {}}
            return areq_request.response(200, body=json.dumps(result))

    yield zendesk_forms.create_forms_ticket(msg_id)


@pytest.mark.config(MAX_ZENDESK_EMAIL_LENGTH=20)
@pytest.mark.parametrize('email, expected_result', [
     (
         'test@email.email',
         'test@email.email'
     ),
     (
         'too_long_email_for_this_test@taxi.yandex.ru',
         'noname'
     )
]
)
@pytest.inlineCallbacks
def test_validate_email(email, expected_result):

    email = yield zendesk_forms._validate_email(email)
    assert email == expected_result


@pytest.mark.parametrize(
    'message_id, next_message_id, user_phone_id, expected_tags,'
    'expected_order_id, expected_country, expected_application,'
    'expected_locale, expected_next_locale, expected_meta_values,'
    'expected_sender_id, expected_sender_role',
    [
        (
            'msg1',
            'msg2',
            'userphone1',
            ['business_client'],
            'order1',
            'rus',
            'iphone',
            'en',
            'ru',
            {
                'order_id': 'order1',
                'order_alias_id': '22c6f49e8a944fb48fe91bda0fb9ce97',
                'driver_id': 'clid_uuid',
                'park_db_id': 'park',
                'user_id': 'user1',
                'user_phone_id': 'userphone1',
                'user_phone': '+79000000000',
                'phone_type': 'yandex',
                'zone': 'moscow',
                'ml_request_id': UUID,
            },
            'userphone1',
            'client',
        ),
        (
            'msg5',
            'msg6',
            'userphone_taxi_staff',
            [],
            None,
            '',
            '',
            'ru',
            'ru',
            {
                'user_phone': '+79000000002',
                'phone_type': 'uber',
                'ml_request_id': UUID,
            },
            'userphone_taxi_staff',
            'client',
        ),
        (
            'msg_with_attachments',
            None,
            'userphone1',
            ['business_client'],
            'order1',
            'rus',
            'iphone',
            'ru',
            None,
            {
                'order_id': 'order1',
                'order_alias_id': '22c6f49e8a944fb48fe91bda0fb9ce97',
                'driver_id': 'clid_uuid',
                'park_db_id': 'park',
                'user_id': 'user1',
                'user_phone_id': 'userphone1',
                'user_phone': '+79000000000',
                'phone_type': 'yandex',
                'zone': 'moscow',
                'ml_request_id': UUID,
            },
            'userphone1',
            'client',
        ),
        (
            'msg_with_carsharing_service',
            None,
            'userphone1',
            ['business_client'],
            'order1',
            'rus',
            'iphone',
            'ru',
            None,
            {
                'order_id': 'order1',
                'order_alias_id': '22c6f49e8a944fb48fe91bda0fb9ce97',
                'driver_id': 'clid_uuid',
                'park_db_id': 'park',
                'user_id': 'user1',
                'user_phone_id': 'userphone1',
                'user_phone': '+79000000000',
                'phone_type': 'yandex',
                'zone': 'moscow',
                'ml_request_id': UUID,
            },
            'uid1',
            'carsharing_client',
        ),
    ],
)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.asyncenv('async')
@pytest.mark.config(FEEDBACK_EXTERNAL_TAGS_ENABLED=True)
@pytest.mark.usefixtures('mock_get_tags')
def test_send_zendesk_with_chat_support_api(
        zclient, areq_request, forms_db, monkeypatch, mock_get_urgency,
        message_id, next_message_id, user_phone_id,
        expected_tags, expected_order_id, expected_country,
        expected_application, expected_locale, expected_next_locale,
        expected_meta_values, expected_sender_id, expected_sender_role,
        mock_detect_language, mock_uuid_uuid4):

    def get_experiments(doc1, doc2):
        return ['user_chat', 'feedback_user_chat', 'use_support_chat_api']

    monkeypatch.setattr(
        user_manager,
        'user_support_chat', lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        experiment_manager,
        'get_experiments_for_user',
        get_experiments
    )

    monkeypatch.setattr(
        experiment_manager,
        'get_experiments',
        get_experiments
    )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name in ['support_chat', 'chatterbox']
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        parsed_url = urlparse.urlparse(url)
        request = kwargs['json']
        if 'support-chat' in url:
            assert url.startswith('http://support-chat.taxi.yandex.net')
            if 'add_update' in url:
                chat_id = parsed_url.path.split('/')[3]
                assert request['update_metadata']['author_id'] == 'STUB_ID'
                assert request['update_metadata']['ticket_id'] == 1
                db.user_chat_messages._collection.update(
                    {
                        '_id': bson.ObjectId(chat_id)
                    },
                    {
                        '$set': {
                            'author_id': 'STUB_ID',
                            'ticket_id': 1
                        }
                    }
                )
                return areq_request.response(200, body=json.dumps({}))
            else:
                if 'attachments' in request['message']['metadata']:
                    for attachment in (
                        request['message']['metadata']['attachments']
                    ):
                        assert attachment['id'] == 'other_attachment_id'
                if request['request_id'] == 'msg1':
                    assert request['metadata']['user_locale'] == 'en'
                else:
                    assert request['metadata']['user_locale'] == 'ru'
                assert request['metadata']['tags'] == expected_tags
                assert (
                    request['message']['metadata'].get('order_id') ==
                    expected_order_id
                )
                if expected_application:
                    assert request['owner']['platform'] == expected_application
                else:
                    assert request['owner']['platform'] == ''
                assert request['message']['metadata']['source'] == 'form'
                assert request['metadata']['user_country'] == expected_country
                assert (
                    request['metadata']['user_application'] ==
                    expected_application
                )
                assert request['metadata']['ml_request_id'] is not None
                assert request['owner']['id'] == expected_sender_id
                assert request['owner']['role'] == expected_sender_role
                assert request['message']['sender']['id'] == expected_sender_id
                assert request['message']['sender']['role'] == (
                    expected_sender_role
                )
                chat_doc, _ = dbh.user_chat_messages.Doc.open_new_chat(
                    request['metadata']['user_id'],
                    request['owner']['id'],
                    request['request_id'],
                    request['message']['text'],
                    request['metadata']['user_locale']
                ).result
                result = {
                    'id': str(chat_doc.pk),
                    'metadata': {
                        'ticket_id': chat_doc.get('ticket_id'),
                        'author_id': chat_doc.get('author_id')
                    }
                }
                return areq_request.response(
                    200, body=json.dumps(result)
                )
        if 'chatterbox' in url:
            assert url.startswith('http://chatterbox.taxi.yandex.net')
            if 'update_meta' in url:
                chatterbox_id = parsed_url.path.split('/')[3]
                assert chatterbox_id == 'chatterbox_id'
                assert 'update_meta' in request
                meta_values = _get_updated_meta(request['update_meta'])
                tags_values = _get_updated_tags(
                    request['update_tags'],
                )
                assert meta_values == expected_meta_values
                assert 'chat_draft' in tags_values
                assert 'chat' in tags_values
                assert not 'readonly' in tags_values
                return areq_request.response(200, body=json.dumps({}))
            else:
                assert request['type'] == 'chat'
                result = {
                    'id': 'chatterbox_id',
                    'status': 'new'
                }
                tags_values = _get_updated_tags(
                    request['metadata']['update_tags'],
                )
                meta_values = _get_updated_meta(
                    request['metadata']['update_meta'],
                )
                assert meta_values == expected_meta_values
                if forms_db[message_id].get('service') == 'drive':
                    assert 'carsharing' in tags_values
                return areq_request.response(200, body=json.dumps(result))

    def check_chat(chat, msg_id):
        assert 'ticket_id' not in chat
        assert 'author_id' not in chat
        assert forms_db[msg_id]['ticket_created']

    yield zendesk_forms.create_forms_ticket(message_id)
    open_chat = yield dbh.user_chat_messages.Doc.find_open_chat(
        expected_sender_id,
    )
    check_chat(open_chat, message_id)
    assert open_chat.user_locale == expected_locale

    # check idempotentcy
    yield zendesk_forms.create_forms_ticket(message_id)
    open_chat = yield dbh.user_chat_messages.Doc.find_open_chat(
        expected_sender_id,
    )
    check_chat(open_chat, message_id)

    if next_message_id is not None:
        # add to the same chat
        yield zendesk_forms.create_forms_ticket(next_message_id)
        open_chat = yield dbh.user_chat_messages.Doc.find_open_chat(
            expected_sender_id,
        )
        check_chat(open_chat, next_message_id)
        # locale changed after message with another locale
        assert open_chat.user_locale == expected_next_locale


@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.asyncenv('async')
@pytest.mark.config(
    FEEDBACK_EXTERNAL_TAGS_ENABLED=True,
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
)
def test_chat_with_close_ticket(zclient, areq_request, forms_db,
                                monkeypatch, mock_get_urgency, mock_get_tags,
                                mock_detect_language):

    def get_experiments(doc1, doc2):
        return ['user_chat', 'feedback_user_chat', 'use_support_chat_api']

    monkeypatch.setattr(user_manager, 'user_support_chat', lambda *args, **kwargs: True)
    monkeypatch.setattr(
        experiment_manager,
        'get_experiments_for_user',
        get_experiments
    )

    monkeypatch.setattr(
        experiment_manager,
        'get_experiments',
        get_experiments
    )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name in ['support_chat', 'chatterbox']
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        parsed_url = urlparse.urlparse(url)
        request = kwargs['json']
        if 'support-chat' in url:
            assert url.startswith('http://support-chat.taxi.yandex.net')
            if 'add_update' in url:
                chat_id = parsed_url.path.split('/')[3]
                assert request['update_metadata']['author_id'] == 'STUB_ID'
                assert request['update_metadata']['ticket_id'] == 1
                db.user_chat_messages._collection.update(
                    {
                        '_id': bson.ObjectId(chat_id)
                    },
                    {
                        '$set': {
                            'author_id': 'STUB_ID',
                            'ticket_id': 1
                        }
                    }
                )
                return areq_request.response(200, body=json.dumps({}))
            else:
                assert request['metadata']['user_locale'] == 'en'
                assert request['metadata']['user_country'] == 'rus'
                assert request['metadata']['user_application'] == 'iphone'
                assert request['owner']['platform'] == 'iphone'
                chat_doc, _ = dbh.user_chat_messages.Doc.open_new_chat(
                    request['metadata']['user_id'],
                    request['owner']['id'],
                    request['request_id'],
                    request['message']['text'],
                    request['metadata']['user_locale']
                ).result
                result = {
                    'id': str(chat_doc.pk),
                    'metadata': {
                        'ticket_id': chat_doc.get('ticket_id'),
                        'author_id': chat_doc.get('author_id')
                    }
                }
                return areq_request.response(
                    200, body=json.dumps(result)
                )
        if 'chatterbox' in url:
            json.dumps(request)
            assert url.startswith('http://chatterbox.taxi.yandex.net')
            result = {'id': str(bson.ObjectId()), 'metadata': {}}
            return areq_request.response(200, body=json.dumps(result))

    query = {
        'user_phone_id': 'userphone1'
    }

    yield zendesk_forms.create_forms_ticket('msg1')
    chat = yield dbh.user_chat_messages.Doc.find_one_or_not_found(query)
    assert chat['open'] is True
    assert chat['visible'] is False
    assert 'ticket_status' not in chat

    assert len(mock_get_urgency.calls) == 2  # for 2 comment
    assert len(mock_detect_language.calls) == 2


@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.parametrize('msg_to_chatterbox, expected_response', [
    (
        'msg_to_chatterbox',
        {
            'message_text': 'txt',
            'request_id': 'msg_to_chatterbox',
            'user_platform': 'uber',
            'user_phone': '+79999999999',
            'tags': ['non-call-center-tag'],
        },
    ),
    (
        'msg_to_chatterbox_with_order',
        {
            'message_text': 'txt',
            'request_id': 'msg_to_chatterbox_with_order',
            'user_platform': 'uber',
            'user_phone': '+79999999999',
            'order_id': 'order_id',
            'tags': ['non-call-center-tag'],
        },
    ),
    (
        'msg_to_chatterbox_with_zone',
        {
            'message_text': 'txt',
            'request_id': 'msg_to_chatterbox_with_zone',
            'user_platform': 'uber',
            'user_phone': '+79999999999',
            'country': 'rus',
            'zone': 'moscow',
            'tags': ['non-call-center-tag'],
        },
    ),
    (
            'msg_to_chatterbox_with_bad_zone',
            {
                'message_text': 'txt',
                'request_id': 'msg_to_chatterbox_with_bad_zone',
                'user_platform': 'uber',
                'user_phone': '+79999999999',
                'zone': 'Москва',
                'tags': ['non-call-center-tag'],
            },
    ),
])
@pytest.mark.usefixtures(
    'zclient', 'forms_db', 'mock_get_urgency', 'mock_get_tags'
)
def test_send_to_support_info(
        areq_request, monkeypatch, msg_to_chatterbox, expected_response,
        mock_detect_language, forms_db
):

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        request = kwargs['json']
        if url == 'http://support-info.taxi.yandex.net/v1/forms/fos':
            assert request == expected_response
            return areq_request.response(200, body=json.dumps({}))
        else:
            assert False, url

    def get_order_proc_by_id(order_id, lookup_yt=True, src_tvm_service=None,
                             log_extra=None):
        return {'doc': None}

    monkeypatch.setattr(archive, 'get_order_proc_by_id', get_order_proc_by_id)
    monkeypatch.setattr(archive, 'get_order_by_exact_id', get_order_proc_by_id)

    yield zendesk_forms.create_forms_ticket(msg_to_chatterbox)
    assert forms_db[msg_to_chatterbox]['ticket_created']


@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.asyncenv('async')
@pytest.mark.config(
    FEEDBACK_EXTERNAL_TAGS_ENABLED=True,
)
def test_no_need_to_add(zclient, areq_request, forms_db,
                        monkeypatch, mock_get_urgency, mock_get_tags,
                        mock_detect_language):

    def get_experiments(doc1, doc2):
        return ['user_chat', 'feedback_user_chat', 'use_support_chat_api']

    monkeypatch.setattr(user_manager, 'user_support_chat', lambda *args, **kwargs: True)
    monkeypatch.setattr(
        experiment_manager,
        'get_experiments_for_user',
        get_experiments
    )

    monkeypatch.setattr(
        experiment_manager,
        'get_experiments',
        get_experiments
    )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name in [
            'chatterbox', 'support_chat', 'support_info'
        ]
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        parsed_url = urlparse.urlparse(url)
        request = kwargs['json']
        if 'support-chat' in url:
            assert url.startswith('http://support-chat.taxi.yandex.net')
            if 'add_update' in url:
                chat_id = parsed_url.path.split('/')[3]
                assert request['update_metadata']['author_id'] == 'STUB_ID'
                assert request['update_metadata']['ticket_id'] == 1
                db.user_chat_messages._collection.update(
                    {
                        '_id': bson.ObjectId(chat_id)
                    },
                    {
                        '$set': {
                            'author_id': 'STUB_ID',
                            'ticket_id': 1
                        }
                    }
                )
                return areq_request.response(200, body=json.dumps({}))
            else:
                assert request['metadata']['user_locale'] == 'en'
                assert request['metadata']['user_country'] == 'rus'
                assert request['metadata']['user_application'] == 'iphone'
                chat_doc, _ = dbh.user_chat_messages.Doc.open_new_chat(
                    request['metadata']['user_id'],
                    request['owner']['id'],
                    request['request_id'],
                    request['message']['text'],
                    request['metadata']['user_locale']
                ).result
                result = {
                    'id': str(chat_doc.pk),
                    'metadata': {
                        'ticket_id': chat_doc.get('ticket_id'),
                        'author_id': chat_doc.get('author_id')
                    }
                }
                return areq_request.response(
                    200, body=json.dumps(result)
                )
        if 'chatterbox' in url:
            json.dumps(request)
            assert url.startswith('http://chatterbox.taxi.yandex.net')
            result = {'id': str(bson.ObjectId()), 'metadata': {}}
            return areq_request.response(200, body=json.dumps(result))

    query = {
        'user_phone_id': 'userphone1'
    }

    yield zendesk_forms.create_forms_ticket('msg1')
    chat = yield dbh.user_chat_messages.Doc.find_one_or_not_found(query)
    assert chat['open'] is True
    assert chat['visible'] is False
    assert 'ticket_status' not in chat


@pytest.mark.parametrize(
    'message_id',
    ['msg_with_user_without_phone_id'],
)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.asyncenv('async')
@pytest.mark.config(
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=[],
)
@pytest.mark.usefixtures('mock_get_tags', 'forms_db')
def test_send_zendesk_with_chat_support_api_without_driver_id(
        zclient, areq_request, patch, message_id, mock_detect_language
):

    """
    Check that for user without completed registration creating
    chatterbox sms chat or zendesk ticket.
    """
    @patch('taxi_stq._client.put')
    def put(queue=None, **kwargs):
        pass

    @patch('taxi.internal.user_manager.user_support_chat')
    def user_support_chat(*args, **kwargs):
        return True

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == 'http://support-info.taxi.yandex.net/v1/forms/fos'
        return areq_request.response(200, body=json.dumps({}))

    yield zendesk_forms.create_forms_ticket(message_id)

    assert len(requests_request.calls) == 1
    assert len(put.calls) == 0


@pytest.mark.parametrize(
    'message_id,chat_status,expected_exception,expected_comment',
    [
        ('msg_with_attachments', None, None, 'Failed attachments: some.name'),
        (
            'msg_with_attachments',
            404,
            user_support_chat.ChatNotFoundError,
            None,
        ),
        (
            'msg_with_cyrillic_attachments',
            None,
            None,
            'Failed attachments: Без названия.pdf',
        ),
    ],
)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.asyncenv('async')
@pytest.mark.config(
    FEEDBACK_EXTERNAL_TAGS_ENABLED=True,
)
@pytest.mark.usefixtures('mock_get_tags')
def test_error_send_attachments_with_chat_support_api(
        zclient,
        areq_request,
        forms_db,
        monkeypatch,
        mock_get_urgency,
        mock_detect_language,
        message_id,
        chat_status,
        expected_exception,
        expected_comment
):

    def get_experiments(doc1, doc2):
        return ['user_chat', 'feedback_user_chat', 'use_support_chat_api']

    monkeypatch.setattr(
        user_manager,
        'user_support_chat', lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        experiment_manager,
        'get_experiments_for_user',
        get_experiments
    )

    monkeypatch.setattr(
        experiment_manager,
        'get_experiments',
        get_experiments
    )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name in ['support_chat', 'chatterbox']
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        request = kwargs['json']
        if 'support-chat' in url:
            assert url.startswith('http://support-chat.taxi.yandex.net')
            if 'add_update' in url:
                return areq_request.response(200, body=json.dumps({}))
            else:
                if 'attachments' in request['message']['metadata']:
                    return areq_request.response(404)
                if chat_status is not None:
                    return areq_request.response(chat_status)
                chat_doc, _ = dbh.user_chat_messages.Doc.open_new_chat(
                    request['metadata']['user_id'],
                    request['owner']['id'],
                    request['request_id'],
                    request['message']['text'],
                    request['metadata']['user_locale']
                ).result
                result = {
                    'id': str(chat_doc.pk),
                    'metadata': {
                        'ticket_id': chat_doc.get('ticket_id'),
                        'author_id': chat_doc.get('author_id')
                    }
                }
                return areq_request.response(
                    200, body=json.dumps(result)
                )
        if 'chatterbox' in url:
            assert url.startswith('http://chatterbox.taxi.yandex.net')
            assert request['hidden_comment'] == expected_comment
            result = {
                'id': 'chatterbox_id',
                'status': 'new'
            }
            return areq_request.response(200, body=json.dumps(result))

    if expected_exception is None:
        yield zendesk_forms.create_forms_ticket(message_id)
    else:
        with pytest.raises(expected_exception):
            yield zendesk_forms.create_forms_ticket(message_id)


@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.asyncenv('async')
def test_get_form_data_fields_has_phone_permission(
        forms_db
):

    message_id = 'msg_to_chatterbox_with_phone_permission'
    form_data = yield db.zendesk_form_integrations.find_one({
        '_id': message_id,
    })
    ctx = zendesk_forms.FormFeedbackContext()
    ctx.form_data = form_data
    ctx.message_id = message_id

    meta_fields = yield zendesk_forms.get_form_data_fields(ctx)
    assert 'pass_phone_permission' in meta_fields
    assert meta_fields['pass_phone_permission'] is True


def _get_updated_tags(tags):
    tags_values = []
    for item in tags:
        assert item['change_type'] == 'add'
        tags_values.append(item['tag'])
    return tags_values


def _get_updated_meta(meta):
    chatterbox_field_names = (
        'driver_id', 'order_id', 'order_alias_id', 'park_db_id',
        'user_id', 'user_phone', 'user_phone_id', 'phone_type',
        'zone', 'ml_request_id',
    )
    meta_values = {}
    for item in meta:
        assert item['change_type'] == 'set'
        if item['field_name'] == 'zendesk_profile':
            assert item['value'] == 'yataxi'
        if item['field_name'] in chatterbox_field_names:
            meta_values[item['field_name']] = item['value']
    return meta_values
