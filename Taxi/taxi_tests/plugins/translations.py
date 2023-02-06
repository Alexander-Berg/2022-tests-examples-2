import pytest


@pytest.fixture(autouse=True)
def translations(request, mongodb):
    marker = request.node.get_marker('translations')
    if not marker:
        return

    set_last_updated = {}
    for keyset, values in marker.kwargs.items():
        collection = getattr(mongodb, 'localization_' + keyset, None)
        if not collection:
            continue
        bulk = collection.initialize_unordered_bulk_op()
        for key, translation in values.items():
            values = []
            for locale, text in translation.items():
                if isinstance(text, list):
                    forms_and_texts = list(enumerate(text))
                else:
                    forms_and_texts = [(None, text)]
                for form, txt in forms_and_texts:
                    conditions = {}
                    if form is not None:
                        conditions['form'] = form
                    if locale != 'ru':
                        conditions['locale'] = {
                            'language': locale,
                        }
                    values.append({
                        'value': txt,
                        'conditions': conditions,
                    })
            bulk.find({'_id': key}).upsert().update({
                '$set': {
                    'values': values,
                },
            })
        bulk.execute()
        set_last_updated['value.%s' % keyset] = True

    if hasattr(mongodb, 'localizations_meta') and set_last_updated:
        mongodb.localizations_meta.update(
            {'_id': 'LAST_UPDATED_META_ID'},
            {'$currentDate': set_last_updated},
            upsert=True,
        )
