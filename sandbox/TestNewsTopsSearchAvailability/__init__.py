import logging
import pprint
import requests

from sandbox import sdk2
import sandbox.sdk2.parameters as sp

req = requests.Session()
req.hooks = {
    'response': lambda r, *args, **kwargs: r.raise_for_status()
}


def send_event(host, service, tags, status, descr):
    res = req.post('http://juggler-push.search.yandex.net/events', json={
        'source': 'news-search-monitoring',
        'events': [
            {
                'host': host,
                'service': service,
                'instance': '',
                'tags': tags,
                'status': status,
                'description': descr
                }
            ]
        },
        timeout=1).json()
    if (not res['success']):
        raise RuntimeError("Error sending events to juggler: {}".format(res))


def is_available(text, need_story=True, sort_date=False):
    params = dict(text='"{}"'.format(text), as_json=1)
    if sort_date:
        params['sortby'] = 'date'
    response = req.get('https://newssearch.yandex.ru/news/search', params=params)
    logging.info("Request url: %s", response.url)
    response_json = response.json()
    logging.info("Response: \n%s", pprint.pformat(response_json))
    r = response_json['data']
    if need_story:
        return any(x['type'] == 'story' for x in r)
    else:
        return len(r) > 0


class TestNewsTopsSearchAvailability(sdk2.Task):
    """Checks that all top5 titles can be found through news search"""

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 1024
        disk_space = 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        juggler_host = sp.String('Juggler host')
        juggler_service = sp.String('Juggler service')
        juggler_tags = sp.List('Juggler tags', value_type=sp.String)

        warn_threshold = sp.Integer('Warn threshold', default=1)
        crit_threshold = sp.Integer('Crit threshold', default=2)
        attempts = sp.Integer('Attempts count', default=1)
        delay = sp.Integer('Delay between attempts (sec)', default=60)
        need_story = sp.Bool('Require story', default=False)
        sort_by_date = sp.Bool('Sort by date', default=True)

    def on_execute(self):
        ctx = self.Context
        p = self.Parameters

        with self.memoize_stage.init:
            tops = req.get('http://data.news.yandex.ru/api/v2/tops_export?new_format=1').json()
            ctx.tocheck = [{k: x[k] for k in ('title', 'url')} for x in tops['data'][0]['stories']]
            ctx.attempt = 0
            ctx.nbad = 10000  # 'max'
            ctx.message = ''

        tocheck = ctx.tocheck
        total = len(tocheck)

        logging.info('tocheck: {}'.format(tocheck))

        bad = [t for t in tocheck if not is_available(t['title'], need_story=p.need_story, sort_date=p.sort_by_date)]
        nbad = len(bad)
        good = total - nbad

        logging.info('good: {}'.format(good))
        ctx.attempt += 1

        if nbad < ctx.nbad:
            ctx.nbad = nbad
            msg = "Didn't find titles: {}".format('\n'.join('{} -> {}'.format(x['title'], x['url']) for x in bad)) if nbad > 0 else 'All ok'
            logging.warn(msg)
            ctx.message = msg

        if ctx.nbad == 0 or ctx.attempt >= p.attempts:
            status = ('OK' if ctx.nbad < p.warn_threshold else
                      'WARN' if ctx.nbad < p.crit_threshold else 'CRIT')

            send_event(p.juggler_host, p.juggler_service, p.juggler_tags, status, ctx.message)
        else:
            raise sdk2.WaitTime(p.delay)
