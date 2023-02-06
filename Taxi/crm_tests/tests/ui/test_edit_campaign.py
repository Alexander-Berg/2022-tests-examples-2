import datetime
import pytest


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'oneshot',
     'audience': 'driver',
     'campaign_name': 'test campaign name',
     'description': 'test description',
     'trend': 'Техническое > Техническое',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),  # start date
     'end': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),  # end date
     'is_creative_needed': True,
     'contact_politics': False,
     'global_control': True,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 1
     }
], indirect=True)
def test_edit_drivers_campaign_after_creation(new_campaign_card):
    created_date = datetime.datetime.now()
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    expected_salt = campaign_card.get_campaign_salt()
    expected_name = campaign_params['campaign_name']
    expected_description = campaign_params['description']
    expected_trend = campaign_params['trend']
    expected_start_date = campaign_params['start']
    expected_end_date = campaign_params['end']

    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=True)
    campaign_edit_card.verify_trend_field(is_enabled=True)
    campaign_edit_card.verify_description_input(is_enabled=True)
    campaign_edit_card.verify_salt_field_state(is_enabled=True)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=True)
    campaign_edit_card.verify_dates(are_enabled=True)

    campaign_edit_card.verify_global_control_switch(is_on=True)

    campaign_edit_card.verify_campaign_name(expected_name)
    campaign_edit_card.verify_campaign_description(expected_description)
    campaign_edit_card.verify_campaign_trend(expected_trend)
    campaign_edit_card.verify_start_date(expected_start_date)
    campaign_edit_card.verify_end_date(expected_end_date)

    new_name = "edited test campaign name"
    new_description = "edited description"
    new_trend = 'Опрос > Опрос'
    new_start_date = (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M')
    new_end_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime(
        '%d.%m.%Y %H:%M')
    new_global_control = False

    campaign_edit_card.input_campaign_fields('oneshot',
                                             'driver',
                                             campaign_name=new_name,
                                             description=new_description,
                                             trend=new_trend,
                                             start=new_start_date,
                                             end=new_end_date,
                                             global_control=new_global_control,
                                             mode='edit')
    campaign_edit_card.click_create_and_wait()
    campaign_card.wait_for_card_open()
    edit_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(new_name)
    campaign_card.verify_campaign_description(new_description)
    campaign_card.verify_campaign_trend(new_trend)
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_creative_ticket()
    campaign_card.verify_campaign_type("Разовая")
    campaign_card.verify_campaign_audience("Водители")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(expected_salt)
    campaign_card.verify_global_control_state(new_global_control)
    campaign_card.verify_contact_politics_state(False)
    campaign_card.verify_efficiency_control_state(False)
    campaign_card.verify_created_date(created_date)
    campaign_card.verify_updated_date(edit_date)
    campaign_card.verify_empty_segment_placeholder()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
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
def test_edit_users_campaign_after_creation(new_campaign_card):
    created_date = datetime.datetime.now()
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    expected_salt = campaign_card.get_campaign_salt()
    expected_name = campaign_params['campaign_name']
    expected_description = campaign_params['description']
    expected_trend = campaign_params['trend']
    expected_start_date = campaign_params['start']
    expected_end_date = campaign_params['end']

    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=True)
    campaign_edit_card.verify_trend_field(is_enabled=True)
    campaign_edit_card.verify_description_input(is_enabled=True)
    campaign_edit_card.verify_salt_field_state(is_enabled=True)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=True)
    campaign_edit_card.verify_contacts_politics_switch_state(is_enabled=True)
    campaign_edit_card.verify_discount_message_switch_state(is_enabled=True)
    campaign_edit_card.verify_efficiency_control_switch_state(is_enabled=True)
    campaign_edit_card.verify_dates(are_enabled=True)

    campaign_edit_card.verify_campaign_name(expected_name)
    campaign_edit_card.verify_campaign_description(expected_description)
    campaign_edit_card.verify_campaign_trend(expected_trend)
    campaign_edit_card.verify_contacts_politics_switch(is_on=True)
    campaign_edit_card.verify_global_control_switch(is_on=True)
    campaign_edit_card.verify_discount_message_switch(is_on=False)
    campaign_edit_card.verify_efficiency_control_switch(is_on=True)
    campaign_edit_card.verify_start_date(expected_start_date)
    campaign_edit_card.verify_end_date(expected_end_date)

    new_name = "edited test campaign name"
    new_description = "edited description"
    new_trend = 'Запуск фичей > Кондиционер'
    new_start_date = (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M')
    new_end_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime(
        '%d.%m.%Y %H:%M')
    new_global_control = False
    new_contacts_politics = False
    new_discount_message = True
    new_efficiency_control = False

    campaign_edit_card.input_campaign_fields('oneshot',
                                             'user',
                                             campaign_name=new_name,
                                             description=new_description,
                                             trend=new_trend,
                                             start=new_start_date,
                                             end=new_end_date,
                                             global_control=new_global_control,
                                             contact_politics=new_contacts_politics,
                                             discount_message=new_discount_message,
                                             efficiency_control=new_efficiency_control,
                                             mode='edit')
    campaign_edit_card.click_create_and_wait()
    campaign_card.wait_for_card_open()
    edit_date = datetime.datetime.now()
    campaign_card.verify_progress(0)
    campaign_card.verify_progress_indicator(0)
    campaign_card.verify_status("Новая")
    campaign_card.verify_status_description("Задайте параметры сегмента.")
    campaign_card.verify_campaign_name(new_name)
    campaign_card.verify_campaign_description(new_description)
    campaign_card.verify_campaign_trend(new_trend)
    campaign_card.verify_campaign_ticket()
    campaign_card.verify_campaign_ticket_status("Открыт")
    campaign_card.verify_campaign_type("Разовая")
    campaign_card.verify_campaign_audience("Пользователи")
    campaign_card.verify_author("robot-crm-tester")
    campaign_card.verify_salt(expected_salt)
    campaign_card.verify_global_control_state(new_global_control)
    campaign_card.verify_contact_politics_state(new_contacts_politics)
    campaign_card.verify_efficiency_control_state(new_efficiency_control)
    campaign_card.verify_discount_message_state(new_discount_message)
    campaign_card.verify_created_date(created_date)
    campaign_card.verify_updated_date(edit_date)
    campaign_card.verify_empty_segment_placeholder()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
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
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия']
     }}
], indirect=True)
def test_edit_campaign_after_segment_settings_saved(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.click_save_button()
    campaign_card.wait_for_card_open()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.global_control_switch_off()

    campaign_edit_card.click_create_and_wait()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.regular
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
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия']
     }}
], indirect=True)
def test_edit_drivers_campaign_after_segment_calculated(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status("Сегмент рассчитан")
    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.global_control_switch_off()

    campaign_edit_card.click_create_and_wait()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
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
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия'],
         'brand': 'Яндекс Go'
     }
     }
], indirect=True)
def test_edit_users_campaign_after_segment_calculated(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    brand = segment_filters_params['brand']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.select_brand(brand)
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status("Сегмент рассчитан")
    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.contacts_politics_switch_off()

    campaign_edit_card.click_create_and_wait()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
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
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия'],
         'brand': 'Яндекс Go'
     }
     }
], indirect=True)
def test_edit_users_campaign_while_segment_calculating(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    brand = segment_filters_params['brand']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.select_brand(brand)
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_edit_card = campaign_card.go_to_edit_campaign()
    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=False)
    campaign_edit_card.verify_description_input(is_enabled=False)
    campaign_edit_card.verify_trend_field(is_enabled=False)
    campaign_edit_card.verify_salt_field_state(is_enabled=False)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_contacts_politics_switch_state(is_enabled=False)
    campaign_edit_card.verify_discount_message_switch_state(is_enabled=False)
    campaign_edit_card.verify_efficiency_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_dates(are_enabled=False)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
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
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия'],
         'brand': 'Яндекс Go'
     }
     }
], indirect=True)
def test_edit_users_campaign_after_segment_calculated_and_idea_approved(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    brand = segment_filters_params['brand']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.select_brand(brand)
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status("Сегмент рассчитан")
    star_track = campaign_card.click_link_for_idea_approval_ticket()
    star_track.approve_idea_and_go_back()
    campaign_card.refresh()
    campaign_card.wait_for_card_open()
    campaign_card.verify_status("Настройка групп")
    campaign_card.verify_status_description("Запустите расчет групп.")
    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.contacts_politics_switch_off()
    campaign_edit_card.global_control_switch_off()

    campaign_edit_card.click_create_and_wait()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
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
     'filter_version': 0,
     'segment_filters_params': {
         'cities': ['Осло'],
         'countries': ['Россия'],
         'brand': 'Яндекс Go'
     }
     }
], indirect=True)
def test_edit_users_campaign_after_empty_segment(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    brand = segment_filters_params['brand']
    segment_filters = campaign_card.go_to_segment_settings()
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    segment_filters.select_brand(brand)
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status("Пустой сегмент")
    campaign_card.verify_status_description('Никого с такими параметрами сегмента не удалось найти.'
                                            '\nСкорректируйте параметры сегмента.'
                                            '\n Дополнительная информация')
    campaign_card.verify_progress(21)
    campaign_card.verify_progress_indicator(21)

    campaign_edit_card = campaign_card.go_to_edit_campaign()

    campaign_edit_card.contacts_politics_switch_off()
    campaign_edit_card.global_control_switch_off()

    campaign_edit_card.click_create_and_wait()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'oneshot',
     'audience': 'user',
     'campaign_name': 'test campaign name',
     'description': 'test description',
     'trend': 'Скидки/Снижение минималки/Активация',
     'start': (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime('%d.%m.%Y %H:%M'),
     'end': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     'is_creative_needed': False,
     'contact_politics': True,
     'global_control': True,
     'discount_message': False,
     'efficiency_control': True,
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия'],
         'brand': 'Яндекс Go'
     }
     }
], indirect=True)
def test_edit_users_campaign_while_segment_calculating_stopped(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    brand = segment_filters_params['brand']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.select_brand(brand)
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.stop_calculations()
    campaign_card.wait_for_status('Остановка расчётов')
    campaign_card.verify_status_description(
        'Останавливаем расчет сегмента. Ожидайте, это может занять несколько минут.')
    campaign_card.verify_progress(24)
    campaign_card.verify_progress_indicator(24)
    campaign_card.verify_empty_segment_placeholder()
    campaign_edit_card = campaign_card.go_to_edit_campaign()
    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=False)
    campaign_edit_card.verify_description_input(is_enabled=False)
    campaign_edit_card.verify_trend_field(is_enabled=False)
    campaign_edit_card.verify_salt_field_state(is_enabled=False)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_contacts_politics_switch_state(is_enabled=False)
    campaign_edit_card.verify_discount_message_switch_state(is_enabled=False)
    campaign_edit_card.verify_efficiency_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_dates(are_enabled=False)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
        {'campaign_type': 'oneshot',
         'audience': 'user',
         'campaign_name': 'test campaign name',
         'description': 'test description',
         'trend': 'Скидки/Снижение минималки/Активация',
         'start': (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime('%d.%m.%Y %H:%M'),
         'end': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
         'is_creative_needed': False,
         'contact_politics': True,
         'global_control': True,
         'discount_message': False,
         'efficiency_control': True,
         'filter_version': 1,
         'segment_filters_params': {
             'cities': ['Москва'],
             'countries': ['Россия'],
             'brand': 'Яндекс Go'
         }
         }
    ], indirect=True)
def test_edit_campaign_while_groups_calculating(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    brand = segment_filters_params['brand']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.select_brand(brand)
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status('Сегмент рассчитан')
    star_track = campaign_card.click_link_for_idea_approval_ticket()
    star_track.approve_idea_and_go_back()
    campaign_card.refresh()
    campaign_card.wait_for_card_open()
    groups_settings_screen = campaign_card.go_to_groups_settings()
    group_name = "PUSH_GROUP"
    groups_settings_screen.fill_in_group_settings(group_name, "", "", 5, 0)
    groups_settings_screen.click_save_and_calculate_button()
    campaign_card.wait_for_status('Разделение на группы')
    campaign_edit_card = campaign_card.go_to_edit_campaign()
    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=False)
    campaign_edit_card.verify_description_input(is_enabled=False)
    campaign_edit_card.verify_trend_field(is_enabled=False)
    campaign_edit_card.verify_salt_field_state(is_enabled=False)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_contacts_politics_switch_state(is_enabled=False)
    campaign_edit_card.verify_discount_message_switch_state(is_enabled=False)
    campaign_edit_card.verify_efficiency_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_dates(are_enabled=False)
