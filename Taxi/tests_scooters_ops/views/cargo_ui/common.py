def stabilize_response(body):
    for action in body.get('state', {}).get('point', {}).get('actions', []):
        action.get('problems', []).sort(key=lambda problem: problem['value'])
    return body
