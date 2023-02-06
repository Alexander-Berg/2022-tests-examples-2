# -*- coding: utf-8 -*-
from email import message_from_string
from email.header import Header
import json
import os

import mock
from nose.tools import eq_
from passport.backend.api.common import PROCESS_RESTORE
from passport.backend.api.settings.constants.restore import RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import BaseTestRestoreSemiAutoView
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    aggregated_factors,
    aggregated_statbox_entry,
    answer_factors,
    answer_statbox_entry,
    birthday_factors,
    birthday_statbox_entry,
    confirmed_emails_factors,
    confirmed_emails_statbox_entry,
    delivery_addresses_factors,
    delivery_addresses_statbox_entry,
    email_blackwhite_factors,
    email_blackwhite_statbox_entry,
    email_collectors_factors,
    email_collectors_statbox_entry,
    email_folders_factors,
    email_folders_statbox_entry,
    names_factors,
    names_statbox_entry,
    outbound_emails_factors,
    outbound_emails_statbox_entry,
    passwords_factors,
    passwords_statbox_entry,
    phone_numbers_factors,
    phone_numbers_statbox_entry,
    reg_country_city_factors,
    reg_country_city_statbox_entry,
    registration_date_factors,
    registration_date_factors_statbox_entry,
    restore_attempts_factors,
    restore_attempts_statbox_entry,
    services_factors,
    services_statbox_entry,
    social_factors,
    social_statbox_entry,
    user_env_auths_factors,
    user_env_auths_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ADM_FORM_DATA_URL,
    TEST_BODY_TEMPLATE,
    TEST_CONTACT_EMAIL,
    TEST_CONTACT_REASON,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_ENTERED_REGISTRATION_DATE,
    TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_HINT_QUESTION,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_NAMES,
    TEST_DEFAULT_PASSWORD,
    TEST_DEFAULT_REGISTRATION_COUNTRY,
    TEST_DEFAULT_UID,
    TEST_EMAILS_IN_TRACK,
    TEST_HEADERS_WITH_APPID,
    TEST_HEADERS_WITHOUT_APPID,
    TEST_IP,
    TEST_OTRS_MESSAGE_NO_PHOTO,
    TEST_OTRS_MESSAGE_WITH_PHOTO,
    TEST_PASSWORD_AUTH_DATE,
    TEST_PHONE,
    TEST_PHONE_LOCAL_FORMAT,
    TEST_REQUEST_SOURCE,
    TEST_RESTORE_ID,
    TEST_RESTORE_ID_QUOTED,
    TEST_USER_AGENT,
)
from passport.backend.api.views.bundle.restore.semi_auto.base import (
    DECISION_SOURCE_BASIC_FORMULA,
    MULTISTEP_FORM_VERSION,
    STEP_1_PERSONAL_DATA,
    STEP_2_RECOVERY_TOOLS,
    STEP_3_REGISTRATION_DATA,
    STEP_4_USED_SERVICES,
    STEP_5_SERVICES_DATA,
    STEP_6_FINAL_INFO,
    STEP_FINISHED,
)
from passport.backend.api.views.bundle.restore.semi_auto.controllers import RestoreSemiAutoViewBase
from passport.backend.api.views.bundle.restore.semi_auto.helpers import _format_delivery_addresses
from passport.backend.core.builders.mail_apis.faker import (
    collie_response,
    furita_blackwhite_response,
    rpop_list_response,
    wmi_folders_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.historydb.events import (
    ACTION_RESTORE_SEMI_AUTO_REQUEST,
    EVENT_ACTION,
    EVENT_INFO_RESTORE_ID,
    EVENT_INFO_RESTORE_REQUEST_SOURCE,
    EVENT_INFO_RESTORE_STATUS,
    RESTORE_STATUS_PENDING,
)
from passport.backend.core.mailer.faker.mail_utils import (
    assert_messages_equal,
    get_multipart_boundaries,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.tskv import tskv_bool


eq_ = iterdiff(eq_)


MAX_HEADER_LINE_LEN = 78


@with_settings_hosts()
def test_restore_id_generation():
    view = RestoreSemiAutoViewBase()
    view.account = mock.Mock(uid=TEST_DEFAULT_UID)
    view.track_id = 'track_id'
    restore_id = view.restore_id
    host, pid, time, uid, track = restore_id.split(',')
    eq_(host, '7F')
    eq_(pid, str(os.getpid()))
    eq_(time, TimeNow())
    eq_(uid, str(TEST_DEFAULT_UID))
    eq_(track, 'track_id')


class BaseTestMultiStepRestoreView(BaseTestRestoreSemiAutoView):
    def setup_statbox_templates(self, **kwargs):
        super(BaseTestMultiStepRestoreView, self).setup_statbox_templates(
            version=MULTISTEP_FORM_VERSION,
            step=STEP_1_PERSONAL_DATA,
            **kwargs
        )

    def set_track_values(self, user_entered_login=TEST_DEFAULT_LOGIN, version=MULTISTEP_FORM_VERSION,
                         emails=TEST_EMAILS_IN_TRACK, country='ru', semi_auto_step=STEP_1_PERSONAL_DATA,
                         request_source=TEST_REQUEST_SOURCE, events_info_cache=None, **params):
        params['version'] = version
        params['user_entered_login'] = user_entered_login
        if emails is not None:
            params['emails'] = emails
        if country is not None:
            params['country'] = country
        if semi_auto_step is not None:
            params['semi_auto_step'] = semi_auto_step
        if semi_auto_step is not None and semi_auto_step != STEP_1_PERSONAL_DATA:
            params['events_info_cache'] = events_info_cache or {}
        params['request_source'] = request_source
        params['process_name'] = PROCESS_RESTORE

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for attr_name, value in params.items():
                setattr(track, attr_name, value)
            self.orig_track = track.snapshot()

    def request_params_step_1(self, language='ru', real_reason='killkvko', firstname=TEST_DEFAULT_FIRSTNAME,
                              lastname=TEST_DEFAULT_LASTNAME, birthday=TEST_DEFAULT_BIRTHDAY,
                              contact_email=TEST_CONTACT_EMAIL, passwords=None,
                              password_auth_date=TEST_PASSWORD_AUTH_DATE, eula_accepted=True):
        json_data = {
            'real_reason': real_reason,
            'firstnames': [firstname],
            'lastnames': [lastname],
            'birthday': birthday,
            'contact_email': contact_email,
            'passwords': passwords or [TEST_DEFAULT_PASSWORD],
            'password_auth_date': password_auth_date,
            'eula_accepted': eula_accepted,
        }
        return {
            'language': language,
            'json_data': json.dumps(json_data),
        }

    def request_params_step_2(self, language='ru', phone_numbers=None, emails=None,
                              question='question', answer='answer', question_id=99):
        json_data = {}
        if phone_numbers is not None:
            json_data['phone_numbers'] = phone_numbers
        if emails is not None:
            json_data['emails'] = emails
        if question is not None:
            json_data['question_answer'] = {
                'question': question,
                'question_id': question_id,
                'answer': answer,
            }

        return {
            'language': language,
            'json_data': json.dumps(json_data),
        }

    def request_params_step_3(self, language='ru', registration_date=TEST_DEFAULT_ENTERED_REGISTRATION_DATE,
                              registration_country=TEST_DEFAULT_REGISTRATION_COUNTRY,
                              registration_country_id=None,
                              registration_city=None,
                              registration_city_id=None):
        json_data = {
            'registration_date': registration_date,
            'registration_country': registration_country,
        }
        if registration_city is not None:
            json_data['registration_city'] = registration_city
        if registration_city_id is not None:
            json_data['registration_city_id'] = registration_city_id
        if registration_country_id is not None:
            json_data['registration_country_id'] = registration_country_id

        return {
            'language': language,
            'json_data': json.dumps(json_data),
        }

    def request_params_step_4(self, language='ru', social_accounts=None, services=None):
        json_data = {
            'social_accounts': social_accounts or [],
            'services': services or [],
        }
        return {
            'language': language,
            'json_data': json.dumps(json_data),
        }

    def request_params_step_5(self, language='ru', delivery_addresses=None, email_folders=None,
                              outbound_emails=None, email_collectors=None, email_whitelist=None,
                              email_blacklist=None):
        json_data = {}
        if delivery_addresses is not None:
            json_data['delivery_addresses'] = delivery_addresses
        if email_folders is not None:
            json_data['email_folders'] = email_folders
        if outbound_emails is not None:
            json_data['outbound_emails'] = outbound_emails
        if email_collectors is not None:
            json_data['email_collectors'] = email_collectors
        if email_whitelist is not None:
            json_data['email_whitelist'] = email_whitelist
        if email_blacklist is not None:
            json_data['email_blacklist'] = email_blacklist

        return {
            'language': language,
            'json_data': json.dumps(json_data),
        }

    def request_params_step_6(self, language='ru', contact_reason=TEST_CONTACT_REASON, user_enabled=True,
                              photo_file=None):
        json_data = {
            'user_enabled': user_enabled,
            'contact_reason': contact_reason,
        }
        params = {
            'language': language,
            'json_data': json.dumps(json_data),
        }
        if photo_file is not None:
            params['photo_file'] = photo_file
        return params

    def make_request(self, data, headers=None, url=None):
        data = data or {}
        data['track_id'] = self.track_id
        return self.env.client.post(
            url or self.default_url,
            query_string=dict(consumer='dev'),
            data=data,
            headers=headers,
        )

    def assert_get_state_response_ok(self, resp, track_state, user_entered_login=TEST_DEFAULT_LOGIN,
                                     request_source=TEST_REQUEST_SOURCE, **kwargs):
        self.assert_ok_response(
            resp,
            track_state=track_state,
            user_entered_login=user_entered_login,
            request_source=request_source,
            **kwargs
        )


class BaseTestMultiStepWithCommitUtils(BaseTestMultiStepRestoreView):
    def make_step_1_factors(
        self,
        version=MULTISTEP_FORM_VERSION,
        is_for_learning=False,
        is_unconditional_pass=False,
        request_source=TEST_REQUEST_SOURCE,
        contact_email=TEST_CONTACT_EMAIL,
        language='ru',
        real_reason='killkvko',
        **kwargs
    ):
        factors = {
            'version': version,
            'request_info': {
                'real_reason': real_reason,
                'contact_email': contact_email,
                'language': language,
                'request_source': request_source,
                'last_step': STEP_1_PERSONAL_DATA,
                'is_unconditional_pass': is_unconditional_pass,
            },
            'is_for_learning': is_for_learning,
        }
        for factors_getter in names_factors, birthday_factors, passwords_factors:
            factors.update(factors_getter(**kwargs))
        return factors

    def make_step_1_statbox_factors(
        self,
        **kwargs
    ):
        entry = {}
        for entry_getter in names_statbox_entry, birthday_statbox_entry, passwords_statbox_entry:
            entry.update(entry_getter(**kwargs))
        return entry

    def make_step_2_factors(
        self,
        original_factors,
        **kwargs
    ):
        original_factors['request_info']['last_step'] = STEP_2_RECOVERY_TOOLS
        for factors_getter in phone_numbers_factors, confirmed_emails_factors, answer_factors:
            original_factors.update(factors_getter(**kwargs))
        return original_factors

    def make_step_2_statbox_factors(
        self,
        historydb_api_events_status=True,
        **kwargs
    ):
        entry = {}
        for entry_getter in phone_numbers_statbox_entry, confirmed_emails_statbox_entry, answer_statbox_entry:
            entry.update(entry_getter(**kwargs))
        return entry

    def make_step_3_factors(
        self,
        original_factors,
        **kwargs
    ):
        original_factors['request_info']['last_step'] = STEP_3_REGISTRATION_DATA
        for factors_getter in registration_date_factors, reg_country_city_factors, user_env_auths_factors:
            original_factors.update(factors_getter(**kwargs))
        return aggregated_factors(original_factors, **kwargs)

    def make_step_3_statbox_factors(
        self,
        **kwargs
    ):
        entry = {}
        for entry_getter in (
            registration_date_factors_statbox_entry,
            reg_country_city_statbox_entry,
            user_env_auths_statbox_entry,
            aggregated_statbox_entry,
        ):
            entry.update(entry_getter(**kwargs))
        return entry

    def make_step_4_factors(
        self,
        original_factors,
        **kwargs
    ):
        original_factors['request_info']['last_step'] = STEP_4_USED_SERVICES
        for factors_getter in social_factors, services_factors:
            original_factors.update(factors_getter(**kwargs))
        return original_factors

    def make_step_4_statbox_factors(
        self,
        **kwargs
    ):
        entry = {}
        for entry_getter in social_statbox_entry, services_statbox_entry:
            entry.update(entry_getter(**kwargs))
        return entry

    def make_step_5_factors(
        self,
        original_factors,
        restore_status=RESTORE_STATUS_PENDING,
        tensornet_estimate=0.0,
        tensornet_status=True,
        decision_source=DECISION_SOURCE_BASIC_FORMULA,
        **kwargs
    ):
        original_factors['request_info']['last_step'] = STEP_5_SERVICES_DATA
        for factors_getter in (
                delivery_addresses_factors,
                email_folders_factors,
                email_blackwhite_factors,
                email_collectors_factors,
                outbound_emails_factors,
                restore_attempts_factors,
        ):
            original_factors.update(factors_getter(**kwargs))
        original_factors.update(
            restore_status=restore_status,
            tensornet_estimate=tensornet_estimate,
            tensornet_status=tensornet_status,
            decision_source=decision_source,
        )
        return original_factors

    def make_step_5_statbox_factors(
        self,
        restore_status=RESTORE_STATUS_PENDING,
        any_check_passed=True,
        whole_check_passed=True,
        tensornet_estimate=0.0,
        tensornet_status=True,
        decision_source=DECISION_SOURCE_BASIC_FORMULA,
        restore_id=TEST_RESTORE_ID,
        **kwargs
    ):
        entry = {
            'restore_status': restore_status,
            'decision_source': decision_source,
            'any_check_passed': tskv_bool(any_check_passed),
            'whole_check_passed': tskv_bool(whole_check_passed),
        }
        if tensornet_estimate is not None:
            entry['tensornet_estimate'] = str(tensornet_estimate)
        if tensornet_status is not None:
            entry['tensornet_status'] = tskv_bool(tensornet_status)
        if restore_status != RESTORE_STATUS_PENDING:
            entry['restore_id'] = restore_id
        for entry_getter in (
                delivery_addresses_statbox_entry,
                email_folders_statbox_entry,
                email_blackwhite_statbox_entry,
                email_collectors_statbox_entry,
                outbound_emails_statbox_entry,
                restore_attempts_statbox_entry,
        ):
            entry.update(entry_getter(**kwargs))
        return entry

    def make_step_6_factors(
        self,
        original_factors,
        user_enabled=True,
        contact_reason=TEST_CONTACT_REASON,
        **kwargs
    ):
        original_factors['request_info'].update({
            'last_step': STEP_6_FINAL_INFO,
            'user_enabled': user_enabled,
            'contact_reason': contact_reason,
        })
        return original_factors

    def make_step_6_statbox_factors(
        self,
        restore_id=TEST_RESTORE_ID,
        **kwargs
    ):
        entry = {
            'restore_id': restore_id,
        }
        return entry

    def statbox_step_entries(self, factors, mode='restore_semi_auto', login=TEST_DEFAULT_LOGIN,
                             uid=TEST_DEFAULT_UID, user_agent=TEST_USER_AGENT,
                             step=STEP_1_PERSONAL_DATA, uid_in_submitted_record=False,
                             with_got_state_entry=False, is_unconditional_pass=None,
                             is_for_learning=None, request_source=TEST_REQUEST_SOURCE, **kwargs):
        extra_context = dict(
            request_source=request_source,
            step=step,
        )
        if is_unconditional_pass is not None:
            extra_context['is_unconditional_pass'] = tskv_bool(is_unconditional_pass)
        if is_for_learning is not None:
            extra_context['is_for_learning'] = tskv_bool(is_for_learning)
        extra_context = merge_dicts(kwargs, extra_context)
        if uid_in_submitted_record:
            submitted = self.env.statbox.entry('submitted', uid=str(uid), **extra_context)
        else:
            submitted = self.env.statbox.entry('submitted', **extra_context)
        compared = self.env.statbox.entry('compared', **merge_dicts(extra_context, factors))
        if with_got_state_entry:
            got_state = self.env.statbox.entry('got_state', **extra_context)
            return [got_state, submitted, compared]
        return [submitted, compared]

    def assert_compare_recorded_to_statbox(self, error=None, **kwargs):
        entries = self.statbox_step_entries(kwargs.pop('factors'), **kwargs)
        if error is not None:
            entries.append(self.env.statbox.entry('finished_with_error', error=error, **kwargs))
        self.env.statbox.assert_has_written(entries)

    def assert_track_updated(self, uid=TEST_DEFAULT_UID, login=TEST_DEFAULT_LOGIN,
                             emails=TEST_EMAILS_IN_TRACK, domain=None, factors=None, events_info_cache='{}', **params):
        params['uid'] = str(uid)
        params['login'] = login
        params['country'] = 'ru'
        if events_info_cache is not None:
            params['events_info_cache'] = events_info_cache if isinstance(events_info_cache, str) else json.dumps(events_info_cache)
        expected_track_data = dict(self.orig_track._data)
        expected_track_data.update(params)
        track = self.track_manager.read(self.track_id)
        new_track_data = dict(track._data)
        if track.is_for_learning is not None:
            new_track_data['is_for_learning'] = track.is_for_learning
        if track.is_unconditional_pass is not None:
            new_track_data['is_unconditional_pass'] = track.is_unconditional_pass
        # Отдельно проверяем факторы в JSON'е
        new_factors = json.loads(new_track_data['factors'])
        expected_track_data.pop('factors', None)
        del new_track_data['factors']
        eq_(factors, new_factors)
        eq_(expected_track_data, new_track_data)

    def assert_restore_info_in_event_log(self, uid=TEST_DEFAULT_UID, request_source=TEST_REQUEST_SOURCE,
                                         restore_status=RESTORE_STATUS_PENDING):
        expected_log_entries = {
            EVENT_ACTION: ACTION_RESTORE_SEMI_AUTO_REQUEST,
            EVENT_INFO_RESTORE_ID: TEST_RESTORE_ID,
            EVENT_INFO_RESTORE_REQUEST_SOURCE: request_source,
            EVENT_INFO_RESTORE_STATUS: restore_status,
        }
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def set_mail_api_responses(self, folders_content=None, folders_status=200,
                               blackwhite_content=None, blackwhite_status=200,
                               rpop_content=None, rpop_status=200,
                               collie_content=None, collie_status=200):

        self.env.wmi.set_response_value(
            'folders',
            folders_content if folders_content is not None else wmi_folders_response({}),
            status=folders_status,
        )
        self.env.furita.set_response_value(
            'blackwhite',
            blackwhite_content if blackwhite_content is not None else furita_blackwhite_response(),
            status=blackwhite_status,
        )
        self.env.rpop.set_response_value(
            'list',
            rpop_content if rpop_content is not None else rpop_list_response(),
            status=rpop_status,
        )
        self.env.collie.set_response_value(
            'search_contacts',
            collie_content if collie_content is not None else collie_response([]),
            status=collie_status,
        )

    def check_body(self, raw_body, real_reason='killkvko', login=None, user_enabled=True, names=TEST_DEFAULT_NAMES,
                   birthday=TEST_DEFAULT_BIRTHDAY, question=TEST_DEFAULT_HINT_QUESTION, emails=None, phone_numbers=None,
                   registration_date=TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ,
                   registration_city=None, registration_country=TEST_DEFAULT_REGISTRATION_COUNTRY,
                   delivery_addresses=None, social_accounts=None, social_accounts_present=True, outbound_emails=None,
                   email_folders=None, email_collectors=None, email_whitelist=None,
                   email_blacklist=None, contact_reason=TEST_CONTACT_REASON, request_source=None, **kwargs):
        def multiple_choice(field):
            return {
                '': u'не указано',
                None: u'не указано',
            }.get(field, field)
        body = raw_body.decode('base64')
        disable_login_message = ''
        if not user_enabled:
            disable_login_message = u'Заблокируйте мой логин на время восстановления\n'
        firstname, lastname = names.split(', ')
        adm_form_data_url = TEST_ADM_FORM_DATA_URL % dict(restore_id=TEST_RESTORE_ID_QUOTED)
        notifications = settings.translations.NOTIFICATIONS['ru']
        reason = ''
        if request_source == settings.RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT:
            reason = u'Причина обращения: %s\n' % (notifications['restore.otrs.message_type.%s' % real_reason])
        expected_body = TEST_BODY_TEMPLATE % dict(
            disable_login_message=disable_login_message,
            real_reason=reason,
            login=login,
            lastname=lastname,
            firstname=firstname,
            birthday=birthday,
            question=multiple_choice(question),
            emails=multiple_choice(emails),
            phone_numbers=multiple_choice(phone_numbers),
            registration_date=registration_date,
            registration_city=registration_city or u'не задан',
            registration_country=registration_country,
            delivery_addresses=multiple_choice(_format_delivery_addresses(delivery_addresses, 'ru')),
            social_accounts=multiple_choice(social_accounts) if social_accounts_present else '',
            outbound_emails=multiple_choice(outbound_emails),
            email_folders=multiple_choice(email_folders),
            email_collectors=multiple_choice(email_collectors),
            email_whitelist=multiple_choice(email_whitelist),
            email_blacklist=multiple_choice(email_blacklist),
            contact_reason=contact_reason,
            adm_form_data_url=adm_form_data_url,
        )
        eq_(body, expected_body.encode('utf-8'))

    def assert_mail_sent(self, login=TEST_DEFAULT_LOGIN, tld='ru',
                         photo_file_expected=False, check_passed=True,
                         photo_file_name_escaped=None, photo_file_contents=None,
                         request_source=TEST_REQUEST_SOURCE, real_reason=None, app_id=None, **kwargs):
        eq_(self.env.mailer.message_count, 1)

        message_text = self.env.mailer.get_message_content(message_index=0)
        mime_msg = message_from_string(message_text)
        boundaries = get_multipart_boundaries(message_text)

        notifications = settings.translations.NOTIFICATIONS['ru']
        expected_subject = notifications['restore.semi_auto.otrs_message_subject'] % login
        if request_source == RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT:
            expected_subject = notifications['restore.semi_auto.otrs_message_subject_for_change_hint'] % login
        parts = [msg.get_payload() for msg in mime_msg.get_payload()]
        params = dict(
            boundaries,
            login=login,
            request_source=request_source,
            to=settings.RESTORE_OTRS_ADDRESSES[tld] if check_passed else settings.RESTORE_NOT_PASSED_ADDRESS,
            subject=str(Header(
                expected_subject,
                maxlinelen=MAX_HEADER_LINE_LEN,
                header_name='Subject',
            )),
            app_id=app_id,
            headers=(TEST_HEADERS_WITH_APPID if app_id else TEST_HEADERS_WITHOUT_APPID) % dict(
                request_source=request_source,
                app_id=app_id,
                login=login,
                ip=TEST_IP,
            ),
        )
        photo_attachment = None
        if photo_file_expected:
            template = TEST_OTRS_MESSAGE_WITH_PHOTO
            body, photo_attachment = parts
            eq_(photo_attachment.decode('base64'), photo_file_contents)
        else:
            template = TEST_OTRS_MESSAGE_NO_PHOTO
            body = parts[0]
        params['body'] = body
        params['ip'] = TEST_IP

        self.check_body(body, login=login, request_source=request_source, real_reason=real_reason, **kwargs)
        if photo_file_expected:
            params['photo_file_name_escaped'] = photo_file_name_escaped
            params['photo_file_contents'] = photo_attachment
        # проверим заголовки и тело письма в целом
        assert_messages_equal(message_text, template, params)


class ProcessStepFormErrorsTests(object):

    def test_invalid_step_error(self):
        self.set_track_values(semi_auto_step='invalid_step')

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_last_step_action_not_required_error(self):
        self.set_track_values(semi_auto_step=STEP_FINISHED)

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_error_response(resp, ['action.not_required'])

    def test_contact_email_from_same_account_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)

        resp = self.make_request(self.request_params_step_1(contact_email='login@ya.ru'), self.get_headers())

        self.assert_error_response(resp, ['contact_email.from_same_account'])

    def test_eula_accepted_not_accepted_error(self):
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)

        resp = self.make_request(self.request_params_step_1(eula_accepted=False), self.get_headers())

        self.assert_error_response(resp, ['eula_accepted.not_accepted'])

    def test_phone_numbers_simple_duplicate(self):
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, country='ru')

        resp = self.make_request(
            self.request_params_step_2(phone_numbers=[TEST_PHONE, TEST_PHONE]),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['phone_numbers.duplicate'])

    def test_phone_numbers_latent_duplicate(self):
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, country='ru')

        resp = self.make_request(
            self.request_params_step_2(phone_numbers=[TEST_PHONE, TEST_PHONE_LOCAL_FORMAT]),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['phone_numbers.duplicate'])

    def test_phone_numbers_invalid(self):
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, country='tr')

        resp = self.make_request(
            self.request_params_step_2(phone_numbers=['+7av9991234567']),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['phone_numbers.invalid'])
