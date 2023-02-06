import datetime
import pytest


@pytest.mark.skip(reason="Тест не используется.")
@pytest.mark.drivers
@pytest.mark.oneshot
@pytest.mark.regular
@pytest.mark.xfail(reason="https://st.yandex-team.ru/TAXICRMDEV-980")
@pytest.mark.parametrize(
    'new_campaign_card', [
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
def test_calculate_groups_just_after_segment_ready(new_campaign_card):
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
    campaign_card.click_calculate_groups()
    campaign_card.wait_for_status('Разделение на группы', timeout=30)


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
         'global_control': True,
         'discount_message': False,
         'efficiency_control': False,
         'filter_version': 1,
         'segment_filters_params': {
             'cities': ['Москва'],
             'countries': ['Россия']
         }}
    ], indirect=True)
def test_set_groups_and_then_calculate(new_campaign_card):
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
    groups_settings_screen = campaign_card.go_to_groups_settings()
    group_name = "PUSH_GROUP"
    groups_settings_screen.fill_in_group_settings(group_name, "", "", 5, 0)
    groups_settings_screen.click_save_button()
    campaign_card.wait_for_card_open()
    campaign_card.verify_progress(45)
    campaign_card.verify_progress_indicator(45)
    campaign_card.verify_status('Настройка групп')
    campaign_card.verify_status_description('Запустите расчет групп.')
    campaign_card.verify_summon_analyst_button_present()
    campaign_card.verify_close_campaign_button_present()
    campaign_card.verify_groups_configuration_section_present()
    groups = ["Основная", group_name]
    campaign_card.verify_groupы_names(groups)
    for group in groups:
        campaign_card.verify_group_status(group, "Новая")
        campaign_card.verify_group_channel(group, "")
    campaign_card.click_calculate_groups()
    campaign_card.wait_for_status('Разделение на группы')
