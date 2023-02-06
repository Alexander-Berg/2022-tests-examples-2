import datetime
import pytest


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
     'global_control': False,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия']
     }}
], indirect=True)
def test_save_segment_card_state(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    segment_filters = campaign_card.go_to_segment_settings()
    segment_filters.wait_for_segment_filters_open()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.click_save_button()
    campaign_card.wait_for_card_open()
    current_datetime = datetime.datetime.now()
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)
    campaign_card.verify_status('Сегмент настроен')
    campaign_card.verify_status_description('Запустите расчёт сегмента.')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_calculate_segment_button_present()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.click_calculate_segment()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_summon_analyst_button_present()
    campaign_card.verify_stop_calculating_button_present()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'oneshot',
     'audience': 'driver',
     'campaign_name': 'test driver name',
     'description': 'test description',
     'trend': 'Техническое > Техническое',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),  # start date
     'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     # end date
     'is_creative_needed': True,
     'contact_politics': False,
     'global_control': False,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 0,
     'segment_filters_params': {
         'cities': ['Москва', 'Люберцы', 'Балашиха'],
         'countries': ['Россия']
     }}
], indirect=True)
def test_save_and_calculate_driver_segment_card_state(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    audience = campaign_params['audience']
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
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_summon_analyst_button_present()
    campaign_card.verify_stop_calculating_button_present()
    campaign_card.wait_for_status("Сегмент рассчитан")
    current_datetime = datetime.datetime.now()
    campaign_card.verify_updated_date(current_datetime)
    ticket_id = campaign_card.get_campaign_ticket_id()
    campaign_card.verify_status_description(f'Необходимо согласовать идею кампании в тикете {ticket_id}. '
                                            f'Согласующие автоматически призваны в тикет.')
    campaign_card.verify_progress(29)
    campaign_card.verify_progress_indicator(29)
    campaign_card.verify_locales_graph_present()
    for city in cities:
        campaign_card.verify_city_from_filter_on_card(city)
    campaign_card.verify_global_control_value(audience)
    campaign_card.verify_control_value(audience)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.users
@pytest.mark.eats_users
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize('new_campaign_card', [
    {'campaign_type': 'oneshot',
     'audience': 'user',
     'campaign_name': 'test user name',
     'description': 'test description',
     'trend': 'Техническое > Техническое',
     'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),  # start date
     'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
     # end date
     'is_creative_needed': True,
     'contact_politics': False,
     'global_control': False,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 0,
     'segment_filters_params': {
         'cities': ['Москва', 'Люберцы', 'Балашиха'],
         'countries': ['Россия'],
         'brand': 'Яндекс Go'
     }}
], indirect=True)
def test_save_and_calculate_user_segment_card_state(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]

    audience = campaign_params['audience']
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
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_summon_analyst_button_present()
    campaign_card.verify_stop_calculating_button_present()
    campaign_card.wait_for_status("Сегмент рассчитан")
    current_datetime = datetime.datetime.now()
    campaign_card.verify_updated_date(current_datetime)
    ticket_id = campaign_card.get_campaign_ticket_id()
    campaign_card.verify_status_description(f'Необходимо согласовать идею кампании в тикете {ticket_id}. '
                                            f'Согласующие автоматически призваны в тикет.')
    campaign_card.verify_progress(29)
    campaign_card.verify_progress_indicator(29)
    campaign_card.verify_locales_graph_present()
    for city in cities:
        campaign_card.verify_city_from_filter_on_card(city)
    campaign_card.verify_global_control_value(audience)
    campaign_card.verify_control_value(audience)
    campaign_card.verify_contacts_politics_value()
    campaign_card.verify_available_to_send_value(audience)


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
     'global_control': False,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 1,
     'segment_filters_params': {
         'cities': ['Москва'],
         'countries': ['Россия']
     }}
], indirect=True)
def test_stop_calculating(new_campaign_card):
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
    campaign_card.wait_for_card_open()
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.stop_calculations()
    campaign_card.wait_for_status('Остановка расчётов')
    campaign_card.verify_status_description(
        'Останавливаем расчет сегмента. Ожидайте, это может занять несколько минут.')
    campaign_card.verify_progress(24)
    campaign_card.verify_progress_indicator(24)
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.wait_for_status('Сегмент настроен')
    campaign_card.verify_progress(15)
    campaign_card.verify_progress_indicator(15)


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
     'global_control': False,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 0,
     'segment_filters_params': {
         'cities': ['Осло'],
         'countries': ['Россия']
     }}
], indirect=True)
def test_empty_segment(new_campaign_card):
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
     'global_control': False,
     'discount_message': False,
     'efficiency_control': False,
     'filter_version': 0
     }
], indirect=True)
def test_error_segment(new_campaign_card):
    campaign_card = new_campaign_card[0]
    segment_filters = campaign_card.go_to_segment_settings()
    segment_filters.break_default_driver_segment()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status("Ошибка")
    campaign_card.verify_status_description('Ошибка при формировании сегмента. Обратитесь в чат поддержки.'
                                            '\n Дополнительная информация')
    campaign_card.verify_progress_indicator(26)
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_calculate_segment_button_present()
    campaign_card.verify_groups_section_is_not_displayed()
