import datetime
import pytest


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
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
def test_close_driver_campaign_after_creation(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()
    campaign_edit_card = campaign_card.go_to_edit_campaign()
    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=False)
    campaign_edit_card.verify_trend_field(is_enabled=False)
    campaign_edit_card.verify_description_input(is_enabled=False)
    campaign_edit_card.verify_salt_field_state(is_enabled=False)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=False)
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
         'start': (datetime.datetime.now(datetime.timezone.utc)).strftime('%d.%m.%Y %H:%M'),
         'end': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
         'is_creative_needed': False,
         'contact_politics': True,
         'global_control': True,
         'discount_message': False,
         'efficiency_control': False,
         'filter_version': 1}
    ], indirect=True)
def test_close_user_campaign_after_creation(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()
    campaign_edit_card = campaign_card.go_to_edit_campaign()
    campaign_edit_card.verify_campaign_selector_state(is_enabled=False)
    campaign_edit_card.verify_audience_selector_state(is_enabled=False)
    campaign_edit_card.verify_name_input(is_enabled=False)
    campaign_edit_card.verify_trend_field(is_enabled=False)
    campaign_edit_card.verify_description_input(is_enabled=False)
    campaign_edit_card.verify_discount_message_switch_state(is_enabled=False)
    campaign_edit_card.verify_efficiency_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_salt_field_state(is_enabled=False)
    campaign_edit_card.verify_global_control_switch_state(is_enabled=False)
    campaign_edit_card.verify_dates(are_enabled=False)


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
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
def test_close_campaign_after_segment_settings_saved(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]
    campaign_card.wait_for_card_open()
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
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    campaign_card.verify_empty_segment_placeholder()
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
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
def test_close_campaign_after_segment_calculated(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]
    campaign_card.wait_for_card_open()
    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    segment_filters = campaign_card.go_to_segment_settings()
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    segment_filters.click_save_and_calculate_button()
    campaign_card.wait_for_card_open()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    campaign_card.verify_updated_date(current_datetime)
    campaign_card.verify_progress(22)
    campaign_card.verify_progress_indicator(22)
    campaign_card.verify_status('Расчет сегмента')
    campaign_card.verify_status_description(f'Может длиться до часа, дождитесь статуса «Сегмент рассчитан». '
                                            f'Время начала: {current_time}')
    campaign_card.wait_for_status("Сегмент рассчитан")
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    for city in cities:
        campaign_card.verify_city_from_filter_on_card(city)
    campaign_card.verify_locales_graph_present()
    campaign_card.verify_groups_section_is_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
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
def test_close_campaign_after_segment_calculated_and_idea_approved(new_campaign_card):
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
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    for city in cities:
        campaign_card.verify_city_from_filter_on_card(city)
    campaign_card.verify_locales_graph_present()
    campaign_card.verify_groups_section_is_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
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
def test_get_segment_error_and_close_campaign(new_campaign_card):
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
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    campaign_card.verify_calculate_segment_button_not_present()
    campaign_card.verify_groups_section_is_not_displayed()


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.common
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.parametrize(
    'new_campaign_card',
    [
        {'campaign_type': 'oneshot',
         'audience': 'driver',
         'campaign_name': 'test campaign name',
         'description': 'test description',
         'trend': 'Техническое > Техническое',
         'start': (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime('%d.%m.%Y %H:%M'),  # start date
         'end': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),  # end date
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
def test_get_empty_segment_and_close_campaign(new_campaign_card):
    campaign_card = new_campaign_card[0]
    campaign_params = new_campaign_card[1]
    segment_filters_params = campaign_params['segment_filters_params']
    cities = segment_filters_params['cities']
    countries = segment_filters_params['countries']
    segment_filters = campaign_card.go_to_segment_settings()
    for city in cities:
        segment_filters.input_filter_field(city, 'city')
    for country in countries:
        segment_filters.input_filter_field(country, 'country')
    segment_filters.click_save_and_calculate_button()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
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
    campaign_card.close_campaign()
    campaign_card.wait_for_status("Отменена")
    campaign_card.verify_status_description("Кампания не согласована или заведена по ошибке — отправки не будет.")
    campaign_card.verify_progress_indicator(100)
    campaign_card.verify_calculate_segment_button_not_present()
    campaign_card.verify_groups_section_is_not_displayed()
