from __future__ import print_function

import sys
import time

from readers.rcapi import RecentChangesApiReader
from readers.stream import StreamReader

from utils.config import read_feeds_config


def tsrange(events):
    min_ts = None
    max_ts = None

    for event in events:
        min_ts = event.timestamp if min_ts is None or event.timestamp < min_ts else min_ts
        max_ts = event.timestamp if max_ts is None or event.timestamp > max_ts else max_ts

    return min_ts, max_ts


def test_mode(options):
    feeds = read_feeds_config(options)

    print('Collecting events from stream...', file=sys.stderr)
    start_time = time.time()

    stored_events = []

    for event in StreamReader(options.stream_url, timeout=options.timeout_seconds, namespaces=options.namespaces).read():
        stored_events.append(event)

        end_time = time.time()
        if end_time - start_time > options.test_duration_seconds:
            break

    print('{} events collected in {} seconds'.format(len(stored_events), end_time - start_time), file=sys.stderr)

    for feed in feeds.Feeds:
        print('{}:'.format(feed.Name), file=sys.stderr)

        print('  Getting API events', file=sys.stderr)

        feed_api_events = []

        for namespace in options.namespaces:
            feed_api_events.extend(
                RecentChangesApiReader('https://{}/w/api.php'.format(feed.Server)).read(
                    int(start_time) - options.api_overlap_seconds,
                    int(end_time) + options.api_overlap_seconds,
                    namespace
                )
            )
        feed_stream_events = [event for event in stored_events if event.server == feed.Server]

        feed_api_titles = set([event.title for event in feed_api_events])
        feed_stream_titles = set([event.title for event in feed_stream_events])

        print('  Stream: {} events, {} titles, ts range {}-{}'.format(len(feed_stream_events), len(feed_stream_titles), *tsrange(feed_stream_events)), file=sys.stderr)
        print('  API: {} events, {} titles, ts range {}-{}'.format(len(feed_api_events), len(feed_api_titles), *tsrange(feed_api_events)), file=sys.stderr)
        print('  API/Stream coverage: {:.2f}%'.format(100.0 * len(feed_api_titles) / len((feed_api_titles | feed_stream_titles) or 1)), file=sys.stderr)

        print('  Only in Stream, missing from API:', file=sys.stderr)
        for event in feed_stream_events:
            if event.title not in feed_api_titles:
                print('    {} {}'.format(event.timestamp, event.title.encode('utf-8')), file=sys.stderr)

    return 0
