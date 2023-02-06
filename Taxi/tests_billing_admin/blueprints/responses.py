import bson


def cursor():
    return {'pg': '2019-11-08T14:53:42.066000+00:00/1003985940140'}


def str_cursor():
    return 'billing_reports_cursor'


def wrapped_str_cursor():
    return {'reports_cursor': str_cursor()}


def archive_api(order_proc=None):
    if order_proc is None:
        order_proc = assigned_order_proc()
    return bytes(bson.BSON.encode({'doc': order_proc}))


def billing_reports_docs(docs, cursor_type='object'):
    if cursor_type == 'object':
        cursor_value = cursor()
    else:
        assert cursor_type == 'str'
        cursor_value = str_cursor()
    return {'docs': docs, 'cursor': cursor_value}


def assigned_order_proc():
    return {
        'performer': {'candidate_index': 0},
        'candidates': [{'alias_id': 'some_alias_id'}],
    }


def unassigned_order_proc():
    return {'performer': {'candidate_index': None}, 'candidates': []}
