import allure
import datetime
import os
import pytest
import time

from apis.api_helper import ApiHelper, create_file_to_upload
from apis import yql_api


# "extra_data": "csv", "YT", None


@allure.suite('API Smoke Tests')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.slow
@pytest.mark.api_smoke_suite
def test_api_smoke(session, api_url, startrack_session, startrack_url, campaign_params,
                   yql_url, yql_session, custom_param, delete_old_campaigns, test_suite):
    audience = campaign_params["audience"]
    campaign_type = campaign_params["campaign_type"]
    channel = campaign_params["channel"]
    global_control = campaign_params["global_control"]
    groups_count = campaign_params["groups_count"]  # число групп за исключением Основной
    group_limit = campaign_params["group_limit"]
    segment_version = campaign_params["segment_version"]
    segment_type = campaign_params["segment_type"]
    if campaign_type == "oneshot":
        com_politic = campaign_params["com_politic"]
        efficiency = campaign_params["efficiency"]
    else:
        com_politic = False
        efficiency = False
    if api_url == 'http://crm-admin.taxi.dev.yandex.net':
        api_type = "unstable"
    else:
        api_type = "testing"

    extra_data = campaign_params["extra_data"]

    api_helper = ApiHelper(api_url, session, startrack_url, startrack_session)

    # Открытие списка кампаний
    with allure.step("Открываем список кампаний."):
        api_helper.open_campaign_list()

    # Создание кампании
    start = datetime.datetime.now(datetime.timezone.utc)
    start_s = start.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')
    nice_start = start.strftime('%Y-%m-%d %H:%M:%S')
    if campaign_type == "oneshot":
        end = start + datetime.timedelta(days=7)
    else:
        end = start + datetime.timedelta(hours=2, minutes=30)
    end_s = end.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')

    campaign_name = f"API: {campaign_type} for {audience} ({channel}). Groups: {groups_count}. " \
                    f"Segment: {segment_type}. Start: {nice_start}"
    allure.dynamic.title(campaign_name)

    with allure.step("Получаем информацию о версиях сегментов и каналах для аудиторий."):
        api_helper.get_segment_versions_for_audience(audience)
        api_helper.get_channels_for_audience(audience)
    with allure.step(f"Создаем {campaign_type} кампанию для аудитории {audience}, канал: {channel}."):
        campaign = api_helper.create_campaign(audience, campaign_type, campaign_name, start_s, end_s, efficiency,
                                              com_politic, segment_version, global_control)
    campaign_id = campaign.json()["id"]

    # Добавляем ссылку на кампанию в allure
    allure.dynamic.link(f"https://campaign-management-unstable.taxi.tst.yandex-team.ru/campaigns/{campaign_id}/")

    ticket_id = api_helper.get_campaign_ticket_id(campaign_id)

    api_helper.verify_campaign_state(campaign_id, "NEW")

    # Настройка сегмента
    with allure.step("Получаем информацию о параметрах сегмента."):
        api_helper.get_segment_data(campaign_id)
    with allure.step("Настраиваем сегмент."):
        api_helper.set_segment(campaign_id, audience, segment_type)
    with allure.step("Начинаем расчет сегмента"):
        api_helper.start_segment_calculations(campaign_id)

    # Расчет сегмента
    with allure.step("Ждем окончания расчета сегмента."):
        api_helper.wait_while_state(campaign_id, "SEGMENT_CALCULATING", n=360)

    # Сегмент рассчитан
    with allure.step("Проверяем, что кампания в состоянии 'Сегмент рассчитан' (SEGMENT_FINISHED)."
                     " Получаем статистику сегмента."):
        api_helper.verify_campaign_state(campaign_id, "SEGMENT_FINISHED")
        api_helper.get_segment_stats(campaign_id)

    # Одобряем идею в тикете
    with allure.step("Согласуем идею в тикете в стартреке."):
        api_helper.approve_idea_in_ticket(ticket_id)

    # Проверяем статус кампании после утверждения идеи
    time.sleep(2)
    with allure.step("Проверяем, что кампания в состоянии 'Настройка групп' (GROUPS_READY)."):
        api_helper.verify_campaign_state(campaign_id, "GROUPS_READY")

    # Настройка групп
    # Здесь передавать список словарей с группами
    test_groups = []
    test_group_names = []
    for i in range(groups_count):
        test_group_name = f"test_group_{i}"
        test_group = {"name": test_group_name, "limit": group_limit}
        test_groups.append(test_group)
        test_group_names.append(test_group_name)
    with allure.step(f"Добавляем группы ({groups_count + 1} шт.). Начинаем расчет групп."):
        api_helper.set_groups(campaign_id, test_groups)
        api_helper.start_groups_calculating(campaign_id)

    # Расчет групп
    with allure.step("Ждем окончания разделения на группы."):
        api_helper.wait_while_state(campaign_id, "GROUPS_CALCULATING", n=360)

    # Проверяем статус кампании после расчета групп
    with allure.step("Проверяем, что кампания в состоянии 'Группы сформированы' (GROUPS_FINISHED)."):
        api_helper.verify_campaign_state(campaign_id, "GROUPS_FINISHED")

    # Персонализация
    # Список колонок сегмента
    columns = api_helper.get_columns(campaign_id)
    # Список доступных параметров персонализации
    api_helper.get_placeholders(campaign_id)

    comm_text = "Hello from test!"
    if extra_data is not None:
        new_column = custom_param
        if segment_version == "1":
            if audience == "Driver":
                test_column = "unique_driver_id"
            elif audience == "Geo":
                test_column = "device_id"
            else:
                test_column = "user_phone_id"
        else:
            test_column = columns[3]
        if extra_data == "csv":
            with allure.step(f"Проверяем персонализацию через csv. Дополнительный параметр: '{new_column}'."):
                # Скачиваем файл csv, создаем новый файл с параметром new и загружаем файл csv назад
                api_helper.download_file(campaign_id, test_column, f'file_in_{campaign_id}.csv', 'csv')
                create_file_to_upload(f'file_in_{campaign_id}.csv', f'file_out_{campaign_id}.csv', new_column)
                api_helper.send_file(campaign_id, f'file_out_{campaign_id}.csv')

                # Проверяем, что доп параметр успешно загрузился
                placeholders = api_helper.get_placeholders(campaign_id)
                assert new_column in placeholders
                os.remove(f'file_in_{campaign_id}.csv')
                os.remove(f'file_out_{campaign_id}.csv')
        else:
            # Персонализация через YT (без csv)
            with allure.step(f"Проверяем персонализацию через YT. Дополнительный параметр: '{new_column}'."):
                yql_api.yql_add_extra_data(yql_url, yql_session, api_type, campaign_id, test_column, new_column)
                api_helper.get_path_to_extradata(api_type, campaign_id, test_column)
                # Проверяем, что доп параметр успешно загрузился
                placeholders = api_helper.get_placeholders(campaign_id)
                assert new_column in placeholders
        # в текст добавила {new_column} - персонализация
        comm_text += "{" + f'{new_column}' + "}"

    # Создание креативов
    with allure.step("Создаем креативы."):
        creatives_list = api_helper.setup_creatives(campaign_id, channel, audience, groups_count, comm_text)

    # Настройка отправки
    with allure.step("Устанавливаем Настройки отправки."):
        for i in range(groups_count):
            creative_id = creatives_list[i]['id']
            creative_channel = creatives_list[i]['params']['channel_name']
            with allure.step(f"Группа: {i + 1} - Канал: {creative_channel}"):
                api_helper.set_group_send_settings(campaign_id, f"test_group_{i}", creative_id, efficiency)

        if campaign_type == "regular":
            scheduled_start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=20)
            schedule = scheduled_start.strftime('%M %H * * *')
            api_helper.save_schedule(campaign_id, start_s, end_s, schedule)

    # Тестирование отправки
    test_drivers = [
        "7ad36bc7560449998acbe2c57a75c293_7198b6f166870f53ce743f2ed20f3e28",
        "7ad36bc7560449998acbe2c57a75c293_5f7025a0afab7bc20af9398239dfce37"
    ]
    test_users = [
        "+79652734704"
    ]
    test_geo_users = [
        "545408343c638481b880d1199387e2ef"
    ]
    # TODO: тестировать все группы сразу, или поочереди, или рандомную группу
    with allure.step(f"Тестируем группы"):
        api_helper.verify_groups(campaign_id, ["test_group_0"], audience, test_users, test_drivers, test_geo_users)

    with allure.step("Ждем окончания тестирования."):
        api_helper.wait_while_state(campaign_id, "VERIFY_PROCESSING", n=360)

    # Проверяем статус после того, как тестовая отправка завершена
    with allure.step("Проверяем, что кампания в состоянии 'Протестирована' (VERIFY_FINISHED)."):
        api_helper.verify_campaign_state(campaign_id, "VERIFY_FINISHED")

    # Призыв согласующих в тикет
    with allure.step("Призываем согласующих в тикет."):
        api_helper.summon_approver(campaign_id)
        api_helper.verify_campaign_state(campaign_id, "PENDING")

    # Согласование отправки
    with allure.step("Финальное согласование отправки в тикете."):
        api_helper.approve_sending(ticket_id)

    # Проверяем статус после того, как отправка согласована в тикете
    with allure.step("Проверяем, что кампания в состоянии 'Утверждена' (CAMPAIGN_APPROVED)."):
        time.sleep(5)
        api_helper.verify_campaign_state(campaign_id, "CAMPAIGN_APPROVED")

    if campaign_type == "oneshot":
        # Отправка групп
        with allure.step(f"Отправляем группы. Основная группа не будет отправлена."):
            time.sleep(20)  # чтобы на девайсе после получения тестовой коммуникации успели очистить пуши в шторке
            # и открыть шторку снова
            api_helper.send_groups(campaign_id, test_group_names)
        if not efficiency:
            # Кампания готовится к отправке
            with allure.step("Проверяем, что кампания перешла в состояние 'Отправка запланированна' (SCHEDULED)."
                             "Ждем, пока кампания в этом состоянии."):
                api_helper.verify_campaign_state(campaign_id, "SCHEDULED")
                api_helper.wait_while_state(campaign_id, "SCHEDULED", n=360)
        else:
            with allure.step("Кампания в статусе 'Анализ эффективности' (EFFICIENCY_ANALYSIS)."):
                # # теперь у каждой группы свой канал, поэтому их нужно собрать
                # test_group_channels = []
                # groups = api_helper.get_groups(campaign_id).json()['groups']
                # for group in groups:
                #     if group['channel'] != "DEVNULL":
                #         test_group_channels.append(group['channel'])
                test_group_channels = api_helper.get_channels_for_audience(audience)

                # TODO: можно ли вынести всю эту логику в yql_api?
                yql_api.yql_campaign_log(yql_url, yql_session, api_type, campaign_id, test_group_names, test_group_channels,
                                         "true")
                api_helper.wait_for_state(campaign_id, "EFFICIENCY_ANALYSIS")

                # узнаем все id групп в кампании
                group_ids = api_helper.get_all_groups_id(campaign_id)
                # считаем кол-во коммуникаций в группе
                group_amount = api_helper.count_groups_amount(campaign_id, group_ids)
                # время, позже которого таблицы  сформирована таблица segments_to_send
                now_time = datetime.datetime.now(datetime.timezone.utc)

                # ждем 30 минут, чтобы таблица segments_to_send сгенерировалась
                time.sleep(1800)

                [table_segments_to_send, count_comms] = yql_api.segments_to_send_with_comms(yql_url, yql_session,
                                                                                            api_type, campaign_id, group_ids,
                                                                                            now_time)
                # проверяем кол-во коммуникация в таблице из интересующей кампании/группы
                assert group_amount == int(count_comms)

                # ищем таблицу filtered
                table_segments_to_send_filtered = table_segments_to_send.replace("send_first", "send_filtered_first")
                yql_api.wait_for_table(yql_url, yql_session, table_segments_to_send_filtered)
                count_comms_filtered = yql_api.count_comms_segments_to_send(yql_url, yql_session, campaign_id,
                                                                            group_ids,
                                                                            table_segments_to_send_filtered)
                # все коммуникации разрешены на отправку
                assert count_comms == count_comms_filtered

        # Проверяем статус, когда отправка всех групп завершена
        with allure.step("Ждем окончания отправки (перехода в состояние 'Завершена' (SENDING_FINISHED)."):
            time.sleep(1)
            api_helper.wait_for_state(campaign_id, "SENDING_FINISHED", n=360)

        # Получение результатов кампании
        with allure.step("Получаем результаты кампании."):
            campaign_stats = api_helper.get_campaign_stats(campaign_id)  # размер, глобальный контроль, контроль,
            api_helper.get_campaign_results(
                campaign_id)  # отправлено, зафейлено, пропущено, не отправлено, проанализровано, отклонено
            api_helper.get_groups(campaign_id)  # статистика по группам
            # TODO: здесь добавить проверку на политику контактов - проверить значения в полученной статистике
            #  в зависимости от того, была включена политика или нет,
            #  а также проверка статистики по группам/каналам и по глобальному контролю

            group_ids = api_helper.get_all_groups_id(campaign_id)
            creatives_ids = api_helper.get_all_creatives_id(campaign_id)
            api_helper.verify_com_policy(campaign_stats.json(), com_politic, campaign_id, group_ids, creatives_ids, audience, channel)

            api_helper.verify_general_segment_stat(campaign_stats.json(), audience, segment_version, global_control)
    else:  # если кампания - регулярная (пока сделано так, что будет только одна отправка в рамках регулярки)
        # Запустить регулярную кампанию
        with allure.step("Запускаем регулярную кампанию."):
            api_helper.start_regular_campaign(campaign_id)
            time.sleep(3)

        with allure.step("Проверяем, что кампания в состоянии 'Применение черновика'(APPLYING_DRAFT)."
                         "Ждем пока кампания в этом состоянии."):
            api_helper.verify_campaign_state(campaign_id, "APPLYING_DRAFT")
            api_helper.wait_while_state(campaign_id, "APPLYING_DRAFT", n=360)

        # Кампания запланирована
        with allure.step("Проверяем, что кампания в состоянии 'Отправка запланирована'(SCHEDULED)."
                         "Ждем пока кампания в этом состоянии."):
            if api_helper.check_status_skip(campaign_id, "SCHEDULED", "SEGMENT_CALCULATING"):
                api_helper.wait_while_state(campaign_id, "SCHEDULED", n=270)

        # Начинается пересчет сегмента
        with allure.step("Проверяем, что кампания в состоянии 'Расчет сегмента' (SEGMENT_CALCULATING)."
                         "Ждем пока кампания в этом состоянии."):
            api_helper.verify_campaign_state(campaign_id, "SEGMENT_CALCULATING")
            api_helper.wait_while_state(campaign_id, "SEGMENT_CALCULATING", n=360)

        # Сегмент рассчитан
        with allure.step("Проверяем, что кампания в состоянии 'Сегмент рассчитан'(SEGMENT_FINISHED). "
                         "Ждем пока кампания в этом состоянии."):
            if api_helper.check_status_skip(campaign_id, "SEGMENT_FINISHED", "GROUPS_CALCULATING"):
                api_helper.wait_while_state(campaign_id, "SEGMENT_FINISHED")

        # Расчет групп
        with allure.step("Проверяем, что кампания в состоянии 'Разделение на группы' (GROUPS_CALCULATING)."
                         "Ждем пока кампания в этом состоянии."):
            api_helper.verify_campaign_state(campaign_id, "GROUPS_CALCULATING")
            api_helper.wait_while_state(campaign_id, "GROUPS_CALCULATING", n=360)

        # Группы сформированы
        with allure.step("Проверяем, что кампания в состоянии 'Группы сформированы' (GROUPS_FINISHED)."
                         "Ждем пока кампания в этом состоянии."):
            if api_helper.check_status_skip(campaign_id, "GROUPS_FINISHED", "SENDING_PROCESSING"):
                api_helper.wait_while_state(campaign_id, "GROUPS_FINISHED")

        # Отправка
        with allure.step("Проверяем, что кампания в состоянии SENDING_PROCESSING. "
                         "Ждем пока кампания в состоянии SENDING_PROCESSING"):
            api_helper.verify_campaign_state(campaign_id, "SENDING_PROCESSING")
            api_helper.wait_while_state(campaign_id, "SENDING_PROCESSING", n=360)

        # Кампания запланирована
        with allure.step("Проверяем, что кампания в состоянии 'Запланирована' (SCHEDULED)."
                         "Ждем пока кампания в этом состоянии до окончания срока окончания кампании"):
            api_helper.verify_campaign_state(campaign_id, "SCHEDULED")
            time_left = (
                end - datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)).total_seconds()
            timeout = 10
            n = time_left / timeout + 1
            api_helper.wait_while_state(campaign_id, "SCHEDULED", n=n,
                                        timeout=timeout)  # здесь пытаемся ждать столько, сколько осталось до окончания кампании
        with allure.step("Проверяем, что кампания в состоянии 'Кампания завершена' (COMPLETED)."):
            api_helper.verify_campaign_state(campaign_id, "COMPLETED")

        with allure.step("Получаем статистику кампании."):
            # Получение результатов кампании
            # TODO: проверять статистику, полиси, глобальный контроль и прочее
            api_helper.get_campaign_results(campaign_id)
            api_helper.get_regular_campaign_stats(campaign_id)
            api_helper.get_groups(campaign_id)
            api_helper.get_campaign_stats(campaign_id)

    # Проверка логов в YT
    with allure.step("Проверяем логи в yt в таблицах experiments."):
        # TODO: можно ли вынести всю эту логику в yql_api?
        logs = yql_api.path_to_logs(api_type)
        week_ago_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
        table_name = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
        list_found_table_name = yql_api.find_table(yql_url, yql_session, week_ago_time, logs[audience], table_name)
        table = list_found_table_name[-1][0]
        groups_id = api_helper.get_all_groups_id(campaign_id)
        # Проверяем для каждой группы отдельно
        for i, group_id in enumerate(groups_id, 1):
            comms = yql_api.comms_in_logs_experiments(yql_url, yql_session, ticket_id, table, audience, i)
            api_helper.check_logs_experiments(comms, campaign_id, group_id)
    # Удаление кампании
    with allure.step("Удаляем кампанию"):
        api_helper.delete_campaign(campaign_id)
