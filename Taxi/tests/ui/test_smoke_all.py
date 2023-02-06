import allure
import datetime
import pytest
import time
from screens.campaigns_screen import CampaignsScreen
from screens.campaign_card_screen import CampaignCardScreen
from screens.campaign_form_screen import CampaignFormScreen


@allure.suite('UI Smoke Tests')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.slow
@pytest.mark.ui_smoke_suite
@pytest.mark.parametrize("campaign_params",
                         [
                             pytest.param({"audience": "Driver", "campaign_type": "oneshot"},
                                          marks=pytest.mark.ui_driver_oneshot, id="Driver_oneshot"),
                             pytest.param({"audience": "User", "campaign_type": "oneshot"},
                                          marks=pytest.mark.ui_user_oneshot, id="User_oneshot"),
                             pytest.param({"audience": "EatsUser", "campaign_type": "oneshot"},
                                          marks=pytest.mark.ui_eats_oneshot, id="EatsUser_oneshot"),
                             pytest.param({"audience": "LavkaUser", "campaign_type": "oneshot"},
                                          marks=pytest.mark.ui_lavka_oneshot, id="LavkaUser_oneshot"),
                             pytest.param({"audience": "GeoServices", "campaign_type": "oneshot"},
                                          marks=pytest.mark.ui_geo_oneshot, id="GeoServices_oneshot"),
                             pytest.param({"audience": "Driver", "campaign_type": "regular"},
                                          marks=pytest.mark.ui_driver_regular, id="Driver_regular"),
                             pytest.param({"audience": "User", "campaign_type": "regular"},
                                          marks=pytest.mark.ui_user_regular, id="User_regular"),
                             pytest.param({"audience": "EatsUser", "campaign_type": "regular"},
                                          marks=pytest.mark.ui_eats_regular, id="EatsUser_regular"),
                             pytest.param({"audience": "LavkaUser", "campaign_type": "regular"},
                                          marks=pytest.mark.ui_lavka_regular, id="LavkaUser_regular"),
                             pytest.param({"audience": "GeoServices", "campaign_type": "regular"},
                                          marks=pytest.mark.ui_geo_regular, id="GeoServices_regular"),
                         ]
                         )
def test_ui_smoke(web_driver, link, frontend_api, api_url, session, campaign_params, delete_old_campaigns):
    audience = campaign_params["audience"]
    campaign_type = campaign_params["campaign_type"]

    start = datetime.datetime.now()
    nice_start = start.strftime('%Y-%m-%d %H:%M:%S')
    start_s = start.strftime('%d.%m.%Y %H:%M')
    if campaign_type == 'regular':
        end = start + datetime.timedelta(hours=2)
    else:
        end = start + datetime.timedelta(days=7)
    end_s = end.strftime('%d.%m.%Y %H:%M')
    description = 'test description'

    if audience == "User":
        trend = 'Скидки/Снижение минималки/Активация'
    elif audience == "Driver":
        trend = 'Заработок и тарифы > Доступные тарифы в городе > Комфорт'
    elif audience == "EatsUser":
        trend = 'Продвижение Еды > Рестораны'
    elif audience == "GeoServices":
        trend = 'Продвижение гео сервисов'
    else:
        trend = 'Промоакция'

    campaign_name = f"UI: {campaign_type} for {audience}. {nice_start}"
    allure.dynamic.title(campaign_name)

    with allure.step("Открываем список кампаний."):
        campaigns_list = CampaignsScreen(web_driver, link)
        campaigns_list.open()

    with allure.step(f"Выбираем стенд бека ({frontend_api})."):
        if frontend_api == "api-t":
            campaigns_list.set_frontend_api_testing()
        elif frontend_api == "api-u":
            campaigns_list.set_frontend_api_unstable()
        campaigns_list.wait_for_create_button()

    with allure.step("Открываем форму создания кампании."):
        campaigns_list.open_campaign_form()

    with allure.step("Открываем форму создания кампании. Создаем кампанию."):
        campaign_form = CampaignFormScreen(web_driver, link)
        campaign_form.create_campaign(campaign_type, audience, campaign_name, description, trend, start_s, end_s)
        campaign_id = campaign_form.get_campaign_id()
        # Добавляем ссылку на кампанию в allure
        allure.dynamic.link(f"{link}/{campaign_id}/")
        campaign_card = CampaignCardScreen(web_driver, link, campaign_id)

    with allure.step("Переходим к настройкам креативов"):
        creative_screen = campaign_card.go_to_creative_settings()
        if audience == "User":
            creative_name = 'promo_notification'
            promo_notification_content = "0c7dffbf2e9147d79c686239fcb89772"
            creative_screen.set_promo_notification_settings(creative_name, promo_notification_content)
        elif audience == "Driver":
            creative_name = "feed"
            creative_screen.set_newsfeed_creative(creative_name, 5170)
        elif audience == "GeoServices":
            creative_name = "push"
            communication_content = "Hello from Selenium!"
            push_id = "111"
            creative_screen.set_geopush_creative(creative_name, communication_content, push_id)
        else:
            creative_name = "push"
            communication_content = "Hello from Selenium!"
            creative_screen.set_push_creative(creative_name, communication_content)

    with allure.step("Открываем карточку кампании"):
        creative_screen.open_campaign_card()
        campaign_card.wait_for_card_open()

    with allure.step("Переходим к настройкам сегмента."):
        segment_filter = campaign_card.go_to_segment_settings()

    with allure.step("Настраиваем сегмент."):
        if audience == "User":
            segment_filter.create_default_user_segment()
        elif audience == "Driver":
            segment_filter.create_default_driver_segment()
        elif audience == "EatsUser":
            segment_filter.create_default_eat_user_segment()
        elif audience == "GeoServices":
            segment_filter.create_default_geo_services_segment()
        else:
            segment_filter.create_default_lavka_user_segment()
        campaign_card.refresh()

    with allure.step("Кампания в состоянии 'Расчет сегмента'."):
        campaign_card.wait_for_status('Расчет сегмента')

    with allure.step("Ждем окончания расчета сегмента."):
        campaign_card.wait_for_status('Сегмент рассчитан')

    with allure.step("Одобряем идею кампании в тикете в стартреке."):
        star_track = campaign_card.click_link_for_idea_approval_ticket()
        star_track.approve_idea_and_go_back()
        campaign_card.refresh()
        campaign_card.wait_for_card_open()

    with allure.step("Переходим к настройкам разделения на группы. Настраиваем группы."):
        groups_settings_screen = campaign_card.go_to_groups_settings()
        group_name = "TEST_GROUP"
        groups_settings_screen.fill_in_group_settings(group_name, "", "", 1000, 0)
        groups_settings_screen.click_save_and_calculate_button()

    with allure.step("Ждем, что кампания в статусе 'Разделение на группы'."):
        campaign_card.wait_for_status('Разделение на группы')

    with allure.step("Ждем, когда все группы будут сформированы."):
        campaign_card.wait_for_status('Группы сформированы', timeout=2400)

    with allure.step("Переходим к настройкам отправки."):
        send_settings_screen = campaign_card.go_to_send_settings()

    with allure.step(f"Настраиваем отправку. Выбираем настроенный ранее креатив ({creative_name})"):
        send_settings_screen.set_creative(group_name, creative_name)

    if campaign_type == "regular":
        with allure.step("Настраиваем расписание отправок."):
            send_settings_screen.open_schedule_tab()
            scheduled_start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=25)
            scheduled_start = scheduled_start.strftime('%M %H * * *')
            send_settings_screen.input_cron_schedule(scheduled_start)
            send_settings_screen.click_save_schedule()
            send_settings_screen.open_test_user_tab()

    with allure.step("Тестируем отправку."):
        if audience == 'Driver':
            send_settings_screen.select_test_users("[TESTING] Daria")
        elif audience == 'GeoServices':
            send_settings_screen.select_test_users("545408343c638481b880d1199387e2ef")
        else:
            send_settings_screen.select_test_users("+79652734704")
        send_settings_screen.test_group_with_name(group_name)
        send_settings_screen.click_back_button()
        campaign_card.wait_for_status("Протестирована")

    with allure.step("Отправляем кампанию на финальное согласование."):
        campaign_card.send_for_final_approval()
        campaign_card.refresh()
        campaign_card.wait_for_status("Согласование отправки")
        star_track = campaign_card.click_link_for_idea_approval_ticket()

    with allure.step("Согласуем коммуникацию в стартреке."):
        star_track.approve_communication_and_go_back()
        campaign_card.refresh()
        campaign_card.wait_for_card_open()
        campaign_card.wait_for_status("Утверждена")

    if campaign_type == "oneshot":
        with allure.step("Отправляем группу."):
            send_settings_screen = campaign_card.go_to_send_settings()
            send_settings_screen.click_checkbox_for_group(group_name)
            send_settings_screen.click_send_or_schedule_button()
            send_settings_screen.click_yes_in_popover()
            send_settings_screen.check_for_popover_message()
            if audience == "User" and audience == "LavkaUser":
                send_settings_screen.click_back_button()
            time.sleep(5)
            campaign_card.refresh()
            campaign_card.wait_for_status("Отправка запланирована")
            campaign_card.wait_for_status("Отправка")

        with allure.step("Ждем окончания отправки."):
            campaign_card.wait_for_status("Завершена")
    else:
        with allure.step("Запускаем регулярную кампанию."):
            campaign_card.click_start_regular_campaign()
            campaign_card.refresh()

        with allure.step("Ожидаем начала применения черновика."):
            campaign_card.wait_for_status("Применение черновика")

        # with allure.step("Ожидаем окончания применения черновика."):
        #     campaign_card.wait_for_status("Отправка запланирована")

        with allure.step("Ждем начала расчета сегмента."):
            campaign_card.wait_for_status("Расчет сегмента", timeout=2400)

        with allure.step("Ждем окончания расчета сегмента."):
            campaign_card.wait_for_status("Сегмент рассчитан")

        with allure.step("Ждем начала разделения на группы."):
            campaign_card.wait_for_status("Разделение на группы")

        with allure.step("Ждем окончания разделения на группы."):
            campaign_card.wait_for_status("Группы сформированы", timeout=2100)

        with allure.step("Ждем, когда начнется отправка."):
            campaign_card.wait_for_status("Отправка")

        with allure.step("Ждем окончания отправки и перехода в статус 'Отправка запланирована'."):
            campaign_card.wait_for_status("Отправка запланирована")

        with allure.step("Ждем завершения кампании."):
            timeout = (end - datetime.datetime.now() +
                       datetime.timedelta(minutes=25)).total_seconds()
            campaign_card.wait_for_status("Кампания завершена", timeout=timeout)
    with allure.step("Удаляем кампанию."):
        session.delete(api_url + f'/v1/internal/campaign/clear?id={campaign_id}')
