from tests_corp_billing import util


class EventsService:
    def __init__(self):
        self.topics = {}

    def push(self, events):
        for event in events:
            self._push_event(event)

    def compacted(self, changed_topics):
        topics = []
        for changed in changed_topics:
            key = self._topic_key(changed)
            if key in self.topics:
                known = set()
                events = []
                revision = 0
                for event in reversed(self.topics[key]['events']):
                    revision += 1
                    evkey = self._event_key(event)
                    if evkey in known:
                        continue
                    known.add(evkey)
                    events.append(event)
                twe = changed.copy()
                twe['topic']['revision'] = revision
                twe['events'] = list(reversed(events))
                topics.append(twe)
        return {'topics': topics}

    def _push_event(self, event):
        key = self._topic_key(event)
        if key not in self.topics:
            self.topics[key] = {'known_events': set(), 'events': []}

        event = event.copy()
        del event['namespace']
        del event['topic']
        evkey = self._event_key(event)
        if evkey not in self.topics[key]['known_events']:
            self.topics[key]['known_events'].add(evkey)
            self.topics[key]['events'].append(event)

    @staticmethod
    def _topic_key(obj):
        topic = obj['topic']
        return obj['namespace'], topic['type'], topic['external_ref']

    @staticmethod
    def _event_key(obj):
        occured_at = util.to_timestring(obj['occured_at'])
        return obj['type'], obj.get('external_ref'), occured_at
