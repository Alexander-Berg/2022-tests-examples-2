def make_error_response(text, code=None):
    result = {'error': {'text': text}}
    if code is not None:
        result['error']['code'] = code

    return result
