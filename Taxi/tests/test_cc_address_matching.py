from taxi_pyml.cc_address_matching import preprocess as pp


def test_address_matching_preprocess(load_json):
    inputs = load_json('sample-input.json')
    record = inputs[0]

    phrase_payload = pp.payload_preprocess(
        pp.honest_v1, title=record['text_out'], key='text',
    )
    in_phrase = 'были скорпиона нет нет улица молодежная улица'
    phrase = phrase_payload['text']

    assert in_phrase in phrase

    proposals = [
        pp.payload_preprocess(
            pp.honest_v1, title=p['title'], subtitle=p['subtitle'], key='text',
        )['text']
        for p in record['results']
    ]

    in_prop = 'сто двадцать три дробь два'
    assert in_prop in proposals[0]
