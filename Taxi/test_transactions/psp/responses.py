import json
import os


def load_response(response_path):
    with open(
            os.path.dirname(__file__) + '/static/' + response_path,
    ) as resp_f:
        return json.load(resp_f)


INTENT_CREATED = load_response('intent_created_response.json')
INTENT_EVENTS = load_response('get_intent_events_response.json')
