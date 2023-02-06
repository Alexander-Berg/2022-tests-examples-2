import datetime
import json


def test_delete_campaign(session, api_url):
    campaign_id = 2805
    session.delete(api_url + f"/v1/internal/campaign/clear?id={campaign_id}")


def test_delete_several_campaigns(session, api_url):
    campaign_ids = [2794, 2798, 2799, 2800, 2803, 2804, 2806, 2809, 2810, 2812, 2811]  # здесь можно указать несколько ids
    for campaign_id in campaign_ids:
        session.delete(api_url + f"/v1/internal/campaign/clear?id={campaign_id}")


def test_import_campaign(session, api_url, link):
    session.headers.update({"Content-Type": "application/json"})
    filename = 'oneshot_driver_campaign.json'  # разовая кампания для водителей
    # filename = 'oneshot_user_campaign.json'  # разовая кампания для пользователей
    # filename = 'oneshot_eats_user_campaign.json'  # разовая кампания для пользователей еды
    # filename = 'regular_user_campaign.json'  # регулярная кампания для пользователей
    # filename = 'regular_eats_user_campaign.json'  # регулярная кампания для пользователей еды
    # filename = 'regular_driver_campaign.json'  # регулярная кампания для водителей
    start = datetime.datetime.now(datetime.timezone.utc)
    start_s = start.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')
    end = start + datetime.timedelta(days=7)
    end_s = end.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')
    with open(filename, 'r') as f:
        j = json.load(f)
        if filename.startswith('oneshot'):
            j["campaign"]["efficiency_start_time"] = start_s
            j["campaign"]["efficiency_stop_time"] = end_s
        elif filename.startswith('regular'):
            j["campaign"]["regular_start_time"] = start_s
            j["campaign"]["regular_stop_time"] = end_s
        r = session.post(api_url + "/v1/internal/campaign/import", json=j)
    print(link + f"/{r.json()}")  # будет выведена ссылка на созданную кампанию


def test_export_campaign(session, api_url):
    campaign_id = 2784
    r = session.get(api_url + f"/v1/internal/campaign/export?id={campaign_id}")
    with open("exported_campaign.json", 'w') as f:
        content = json.dumps(r.json())
        f.write(content)


def test_export_and_import(session, api_url, link):
    campaign_id = 2785
    r = session.get(api_url + f"/v1/internal/campaign/export?id={campaign_id}")
    filename = 'exported_campaign.json'
    with open(filename, 'w') as f:
        content = json.dumps(r.json())
        f.write(content)

    session.headers.update({"Content-Type": "application/json"})
    with open(filename, 'r') as f:
        j = json.load(f)
        r = session.post(api_url + "/v1/internal/campaign/import", json=j)

    print(link + f"/{r.json()}")  # будет выведена ссылка на созданную кампанию
