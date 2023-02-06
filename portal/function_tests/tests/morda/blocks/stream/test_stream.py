# -*- coding: utf-8 -*-
import logging
from datetime import timedelta, datetime
from pprint import pformat
from time import mktime

import allure
import pytest
from jinja2 import Template

from common import env
from common.client import MordaClient, StreamClient
from common.geobase import Regions, get_time
from common.mail import send_email
from common.morda import DesktopMain

logger = logging.getLogger(__name__)

BLOCK = 'Stream'
_FROM = 'eoff@yandex-team.ru'
_RECIPIENTS = ['eoff@yandex-team.ru', 'al-fedorov@yandex-team.ru', 'w495@yandex-team.ru', 'esysoeva@yandex-team.ru',
               'nizhi@yandex-team.ru', 'mashko@yandex-team.ru']


def get_channels(client):
    response = client.cleanvars([BLOCK], headers={'X-Forwarded-For': '93.158.178.98'}).send()
    assert response.is_ok(), 'Failed to get cleanvars'
    stream = response.json()['Stream']

    assert stream, 'Failed to get channels'

    return [{'id': channel.get('content_id'), 'title': channel.get('title')}
            for channel in stream['channels']]


def get_timestamps(now):
    time = now.replace(minute=0, second=0, microsecond=0)

    if time.hour >= 5:
        t1 = time
        t2 = time + timedelta(days=1)
    else:
        t1 = time - timedelta(days=1)
        t2 = time

    t1 = t1.replace(hour=5)
    t2 = t2.replace(hour=5)

    return t1, {
        'end_date_from': int(mktime(t1.timetuple())),
        'start_date_to': int(mktime(t2.timetuple()))
    }


def get_episodes(channel, timestamps):
    stream_client = StreamClient()
    response = stream_client.episodes(channel_id=channel['id'], **timestamps).send()

    if response.is_error():
        logger.error(response.format_error())
        return None, response

    return response.json().get('set'), response


def notify_schedule(date, failed):
    if not env.is_monitoring():
        return
    template = u'''<!DOCTYPE html>
    <html lang="en">
    <body>
        <div>Расписание на {{date}} пустое:</div>
        <ul>
            {% for channel in channels -%}
                <li>
                    <a href="{{channel.url}}"> {{channel.title}}</a> (id: {{channel.id}})
                </li>
            {%- endfor %}
        </ul>
        <div>Кажется, что-то не так с данными</div>
    </body>
    </html>
    '''

    number = u'канала' if len(failed) == 1 else u'каналов'

    subject = u'[{}] У {} {} сегодня пустое расписание'.format(
        str(date),
        number,
        ', '.join([e['title'] for e in failed])
    )

    template = Template(template)
    html = template.render(date=str(date), channels=failed).encode('utf-8')

    send_email(_FROM, _RECIPIENTS, subject, html)


def notify_blacked(date, failed):
    if not env.is_monitoring():
        return
    template = u'''<!DOCTYPE html>
    <html lang="en">
    <body>
        <div>Расписание на {{date}}:</div>
        <ul>
            {% for channel in channels -%}
                <li>
                    <a href="{{channel.url}}"> {{channel.title}}</a> (id: {{channel.id}}): {{channel.blacked}}
                    из {{channel.total}} blacked
                </li>
            {%- endfor %}
        </ul>
        <div>Кажется, что-то не так с данными</div>
    </body>
    </html>
    '''

    number = u'канала' if len(failed) == 1 else u'каналов'

    subject = u'[{}] У {} {} сегодня в расписании >50% черных окон'.format(
        date,
        number,
        ', '.join([e['title'] for e in failed])
    )

    template = Template(template)
    html = template.render(date=str(date), channels=failed).encode('utf-8')

    logger.error(html)

    send_email(_FROM, _RECIPIENTS, subject, html)


def notify_holes(date, failed):
    if not env.is_monitoring():
        return
    recipients = ['eoff@yandex-team.ru', 'al-fedorov@yandex-team.ru', 'nizhi@yandex-team.ru', 'mashko@yandex-team.ru',
                  'w495@yandex-team.ru']

    template = u'''<!DOCTYPE html>
    <html lang="en">
    <body>
        <div>Дырки в расписании на {{date}}:</div>
        <ul>
            {% for channel in channels -%}
                <li>
                    <a href="{{channel.url}}"> {{channel.title}}</a> (id: {{channel.id}})
                    <ul>
                        {% for hole in channel.holes -%}
                        <li>
                            {{hole.gap}}
                        </li>
                        {%- endfor %}
                    </ul>
                </li>
            {%- endfor %}
        </ul>
        <div>Кажется, что-то не так с данными</div>
    </body>
    </html>
    '''

    number = u'канала' if len(failed) == 1 else u'каналов'

    subject = u'[{}] У {} {} сегодня дырки в расписании'.format(
        date,
        number,
        ', '.join([e['title'] for e in failed])
    )

    template = Template(template)
    html = template.render(date=str(date), channels=failed).encode('utf-8')

    logger.error(len(html))
    logger.error(html)

    send_email(_FROM, recipients, subject, html)


@allure.feature('stream')
class TestStream(object):
    def setup_method(self, method):
        self.now = get_time(Regions.MOSCOW)
        client = MordaClient(morda=DesktopMain(region=Regions.MOSCOW))

        self.date, self.timestamps = get_timestamps(self.now)
        self.channels = get_channels(client)
        self.failed = []
        self.schedule_date = str(self.date.date())

    @allure.story('stream_schedule')
    @pytest.mark.yasm
    def test_stream_schedule_today(self):
        is_error = False
        for channel in self.channels:
            episodes, response = get_episodes(channel, self.timestamps)
            channel['url'] = response.request.prepared_request.url

            if episodes is None:
                logger.error('Failed to get episodes from bk')
                is_error = True
            else:
                logger.debug(
                    'Found ' + str(len(episodes)) + ' episodes for channel ' + channel['title'].encode('utf-8'))
                if len(episodes) == 0:
                    self.failed.append(channel)

        if len(self.failed) > 0:
            logger.error(pformat(self.failed))
            notify_schedule(self.schedule_date, self.failed)
            pytest.fail('Found channels without schedule')

        assert not is_error, 'Some errors during episodes obtain'

    @allure.story('stream_blacked')
    @pytest.mark.yasm
    def test_stream_blacked(self):
        is_error = False
        for channel in self.channels:
            episodes, response = get_episodes(channel, self.timestamps)
            channel['url'] = response.request.prepared_request.url

            if episodes is None or len(episodes) == 0:
                logger.error('Failed to get episodes from bk')
                is_error = True
            else:
                blacked = len([e for e in episodes if e.get('blacked') == 1])
                logger.debug('Found {} blacked episodes'.format(blacked))
                if float(blacked) / len(episodes) >= 0.5:
                    channel['blacked'] = blacked
                    channel['total'] = len(episodes)
                    self.failed.append(channel)

        if len(self.failed) > 0:
            logger.error(pformat(self.failed))
            notify_blacked(self.schedule_date, self.failed)
            pytest.fail('Found channels with too many blacked episodes')

        assert not is_error, 'Some errors during episodes obtain'

    @allure.story('stream_holes')
    @pytest.mark.yasm
    def test_stream_holes(self):
        def need_notify(st, et):
            if self.now.hour == 12:
                return True
            et_time = datetime.fromtimestamp(et)

            if 6 <= et_time.hour <= 23:
                return True

            return st - et > 3600

        is_error = False
        for channel in self.channels:
            episodes, response = get_episodes(channel, self.timestamps)
            channel['url'] = response.request.prepared_request.url

            if episodes is None or len(episodes) == 0:
                logger.error('Failed to get episodes from bk')
                is_error = True
            else:
                holes = []
                for i in xrange(1, len(episodes)):
                    st = episodes[i]['start_time']
                    et = episodes[i - 1]['end_time']
                    if st != et and need_notify(st, et):
                        st_str = datetime.fromtimestamp(st).strftime('%H:%M')
                        et_str = datetime.fromtimestamp(et).strftime('%H:%M')
                        gap_str = u'Пустое расписание с {} до {}'.format(et_str, st_str)
                        holes.append({
                            'st': st_str,
                            'et': et_str,
                            'gap': gap_str,
                            'title_st': episodes[i]['title'],
                            'title_et': episodes[i - 1]['title']
                        })
                        is_error = True
                if len(holes) > 0:
                    channel['holes'] = holes
                    self.failed.append(channel)

        if len(self.failed) > 0:
            logger.error(pformat(self.failed))
            notify_holes(self.schedule_date, self.failed)
            pytest.fail('Found channels with holes')

        assert not is_error, 'Some errors during episodes obtain'
