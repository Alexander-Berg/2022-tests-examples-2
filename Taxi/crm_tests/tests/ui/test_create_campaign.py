import datetime
import pytest


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
def test_default_form_state_of_form(campaign_form):
    campaign_form.verify_campaign_selector_default_state()
    campaign_form.verify_audience_selector_default_state()
    campaign_form.verify_create_button(is_enabled=False)
    campaign_form.verify_name_input(is_enabled=False)
    campaign_form.verify_description_input(is_enabled=False)
    campaign_form.verify_trend_field(is_enabled=False)
    campaign_form.verify_dates(are_enabled=False)
    campaign_form.verify_creative_needed_switch_visibility(is_visible=False)
    campaign_form.verify_global_control_switch_visibility(is_visible=False)
    campaign_form.verify_discount_message_switch_visibility(is_visible=False)
    campaign_form.verify_contacts_politics_switch_visibility(is_visible=False)
    campaign_form.verify_efficiency_control_switch_visibility(is_visible=False)


@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
def test_default_form_state_for_users(campaign_form):
    campaign_form.select_users()
    campaign_form.verify_users_selected()
    campaign_form.verify_name_input(is_enabled=True)
    campaign_form.verify_description_input(is_enabled=True)
    campaign_form.verify_trend_field(is_enabled=True)
    campaign_form.verify_dates(are_enabled=True)
    campaign_form.verify_contacts_politics_switch(is_on=True)
    campaign_form.verify_global_control_switch(is_on=True)
    campaign_form.verify_discount_message_switch(is_on=False)
    campaign_form.verify_efficiency_control_switch(is_on=True)
    campaign_form.verify_creative_needed_switch_visibility(is_visible=False)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.regular
def test_default_form_state_for_drivers(campaign_form):
    campaign_form.select_drivers()
    campaign_form.verify_drivers_selected()
    campaign_form.verify_name_input(is_enabled=True)
    campaign_form.verify_description_input(is_enabled=True)
    campaign_form.verify_trend_field(is_enabled=True)
    campaign_form.verify_dates(are_enabled=True)
    campaign_form.verify_creative_needed_switch(is_on=True)
    campaign_form.verify_global_control_switch_visibility(is_visible=False)
    campaign_form.verify_discount_message_switch_visibility(is_visible=False)
    campaign_form.verify_contacts_politics_switch_visibility(is_visible=False)
    campaign_form.verify_efficiency_control_switch_visibility(is_visible=False)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.eats_users
@pytest.mark.oneshot
@pytest.mark.regular
def test_default_form_state_for_eats_users(campaign_form):
    campaign_form.select_eats_users()
    campaign_form.verify_eats_users_selected()
    campaign_form.verify_name_input(is_enabled=True)
    campaign_form.verify_description_input(is_enabled=True)
    campaign_form.verify_trend_field(is_enabled=True)
    campaign_form.verify_dates(are_enabled=True)
    campaign_form.verify_contacts_politics_switch(is_on=True)
    campaign_form.verify_global_control_switch(is_on=True)
    campaign_form.verify_efficiency_control_switch(is_on=False)
    campaign_form.verify_creative_needed_switch_visibility(is_visible=False)
    campaign_form.verify_discount_message_switch_visibility(is_visible=False)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'oneshot',
     'audience': 'driver',
     'campaign_name': 'test campaign name',
     'description': 'test description',
     'trend': 'Техническое > Техническое',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),  # start date
     'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     # end date
     'is_creative_needed': True,
     'contact_politics': False,
     'global_control': True,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 1}
], indirect=True)
def test_oneshot_drivers_campaign_verify_card_fields_default(new_campaign_card):
    campaign_card = new_campaign_card[0]
    expected_campaign_params = new_campaign_card[1]
    campaign_id = campaign_card.get_campaign_id()
    current_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(expected_campaign_params["campaign_name"])
    campaign_card.verify_campaign_description(expected_campaign_params["description"])
    campaign_card.verify_campaign_trend(expected_campaign_params["trend"])
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_creative_ticket()
    campaign_card.verify_campaign_type("Разовая")
    campaign_card.verify_campaign_audience("Водители")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(f"__campaign_{campaign_id}__")
    campaign_card.verify_global_control_state(expected_campaign_params["global_control"])
    campaign_card.verify_contact_politics_state(expected_campaign_params["contact_politics"])
    campaign_card.verify_efficiency_control_state(expected_campaign_params["efficiency_control"])
    campaign_card.verify_created_date(current_date)
    campaign_card.verify_updated_date(current_date)
    campaign_card.verify_empty_segment_placeholder()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.regular
@pytest.mark.drivers
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'regular',
     'audience': 'driver',
     'campaign_name': 'test campaign name',
     'description': 'test description',
     'trend': 'Техническое > Техническое',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),  # start date
     'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     # end date
     'is_creative_needed': True,
     'contact_politics': False,
     'global_control': True,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 1}
], indirect=True)
def test_regular_drivers_campaign_verify_card_fields_default(new_campaign_card):
    campaign_card = new_campaign_card[0]
    expected_campaign_params = new_campaign_card[1]
    campaign_id = campaign_card.get_campaign_id()
    current_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(expected_campaign_params["campaign_name"])
    campaign_card.verify_campaign_description(expected_campaign_params["description"])
    campaign_card.verify_campaign_trend(expected_campaign_params["trend"])
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_creative_ticket()
    campaign_card.verify_campaign_type("Регулярная")
    campaign_card.verify_campaign_audience("Водители")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(f"__campaign_{campaign_id}__")
    campaign_card.verify_global_control_state(expected_campaign_params["global_control"])
    campaign_card.verify_contact_politics_state(expected_campaign_params["contact_politics"])
    campaign_card.verify_efficiency_control_state(expected_campaign_params["efficiency_control"])
    campaign_card.verify_created_date(current_date)
    campaign_card.verify_updated_date(current_date)
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_schedule("В 12:00")
    campaign_card.verify_period_start(expected_campaign_params["start"])
    campaign_card.verify_period_end(expected_campaign_params["end"])


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'oneshot',
     'audience': 'user',
     'campaign_name': 'test campaign name',
     'description': 'test description',
     'trend': 'Скидки/Снижение минималки/Активация',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),
     'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     'is_creative_needed': False,
     'contact_politics': True,
     'global_control': True,
     'discount_message': False,
     'efficiency_control': True,
     'filter_version': 1}
], indirect=True)
def test_oneshot_users_campaign_verify_card_fields_default(new_campaign_card):
    campaign_card = new_campaign_card[0]
    expected_campaign_params = new_campaign_card[1]
    campaign_id = campaign_card.get_campaign_id()
    current_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(expected_campaign_params["campaign_name"])
    campaign_card.verify_campaign_description(expected_campaign_params["description"])
    campaign_card.verify_campaign_trend(expected_campaign_params["trend"])
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_campaign_type("Разовая")
    campaign_card.verify_campaign_audience("Пользователи")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(f"__campaign_{campaign_id}__")
    campaign_card.verify_global_control_state(expected_campaign_params["global_control"])
    campaign_card.verify_contact_politics_state(expected_campaign_params["contact_politics"])
    campaign_card.verify_discount_message_state(expected_campaign_params["discount_message"])
    campaign_card.verify_efficiency_control_state(expected_campaign_params["efficiency_control"])
    campaign_card.verify_created_date(current_date)
    campaign_card.verify_updated_date(current_date)
    campaign_card.verify_create_ticket_for_creative_present()
    campaign_card.verify_empty_segment_placeholder()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.regular
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'regular',
     'audience': 'user',
     'campaign_name': 'test campaign name',
     'description': 'test description',
     'trend': 'Скидки/Снижение минималки/Активация',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),
     'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     'is_creative_needed': False,
     'contact_politics': True,
     'global_control': True,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 1}
], indirect=True)
def test_regular_users_campaign_verify_card_fields_default(new_campaign_card):
    campaign_card = new_campaign_card[0]
    expected_campaign_params = new_campaign_card[1]
    campaign_id = campaign_card.get_campaign_id()
    current_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(expected_campaign_params["campaign_name"])
    campaign_card.verify_campaign_description(expected_campaign_params["description"])
    campaign_card.verify_campaign_trend(expected_campaign_params["trend"])
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_campaign_type("Регулярная")
    campaign_card.verify_campaign_audience("Пользователи")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(f"__campaign_{campaign_id}__")
    campaign_card.verify_global_control_state(expected_campaign_params["global_control"])
    campaign_card.verify_contact_politics_state(expected_campaign_params["contact_politics"])
    campaign_card.verify_discount_message_state(expected_campaign_params["discount_message"])
    campaign_card.verify_efficiency_control_state(expected_campaign_params["efficiency_control"])
    campaign_card.verify_created_date(current_date)
    campaign_card.verify_updated_date(current_date)
    campaign_card.verify_create_ticket_for_creative_present()
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_schedule("В 12:00")
    campaign_card.verify_period_start(expected_campaign_params["start"])
    campaign_card.verify_period_end(expected_campaign_params["end"])


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.eats_users
@pytest.mark.oneshot
@pytest.mark.parametrize(
    'new_campaign_card',
    [
        {'campaign_type': 'oneshot',
         'audience': 'eats_user',
         'campaign_name': 'test campaign name',
         'description': 'test description',
         'trend': 'Продвижение еды',
         'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),
         'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
         'is_creative_needed': False,
         'contact_politics': True,
         'global_control': True,
         'discount_message': False,
         'efficiency_control': False,
         'filter_version': 1}
    ], indirect=True)
def test_oneshot_eats_users_campaign_verify_card_fields_default(new_campaign_card):
    campaign_card = new_campaign_card[0]
    expected_campaign_params = new_campaign_card[1]
    campaign_id = campaign_card.get_campaign_id()
    current_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(expected_campaign_params["campaign_name"])
    campaign_card.verify_campaign_description(expected_campaign_params["description"])
    campaign_card.verify_campaign_trend(expected_campaign_params["trend"])
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_campaign_type("Разовая")
    campaign_card.verify_campaign_audience("Пользователи Еды")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(f"__campaign_{campaign_id}__")
    campaign_card.verify_global_control_state(expected_campaign_params["global_control"])
    campaign_card.verify_contact_politics_state(expected_campaign_params["contact_politics"])
    campaign_card.verify_efficiency_control_state(expected_campaign_params["efficiency_control"])
    campaign_card.verify_created_date(current_date)
    campaign_card.verify_updated_date(current_date)
    campaign_card.verify_create_ticket_for_creative_present()
    campaign_card.verify_empty_segment_placeholder()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.eats_users
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
        {'campaign_type': 'regular',
         'audience': 'eats_user',
         'campaign_name': 'test campaign name',
         'description': 'test description',
         'trend': 'Продвижение еды',
         'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),
         'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
         'is_creative_needed': False,
         'contact_politics': True,
         'global_control': True,
         'discount_message': False,
         'efficiency_control': False,
         'filter_version': 1}
    ], indirect=True)
def test_regular_eats_users_campaign_verify_card_fields_default(new_campaign_card):
    campaign_card = new_campaign_card[0]
    expected_campaign_params = new_campaign_card[1]
    campaign_id = campaign_card.get_campaign_id()
    current_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(expected_campaign_params["campaign_name"])
    campaign_card.verify_campaign_description(expected_campaign_params["description"])
    campaign_card.verify_campaign_trend(expected_campaign_params["trend"])
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_campaign_type("Регулярная")
    campaign_card.verify_campaign_audience("Пользователи Еды")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(f"__campaign_{campaign_id}__")
    campaign_card.verify_global_control_state(expected_campaign_params["global_control"])
    campaign_card.verify_contact_politics_state(expected_campaign_params["contact_politics"])
    campaign_card.verify_efficiency_control_state(expected_campaign_params["efficiency_control"])
    campaign_card.verify_created_date(current_date)
    campaign_card.verify_updated_date(current_date)
    campaign_card.verify_create_ticket_for_creative_present()
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_schedule("В 12:00")
    campaign_card.verify_period_start(expected_campaign_params["start"])
    campaign_card.verify_period_end(expected_campaign_params["end"])
