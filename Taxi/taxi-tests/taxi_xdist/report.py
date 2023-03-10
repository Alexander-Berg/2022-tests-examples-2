import difflib

import py


def report_collection_diff(from_collection, to_collection, from_id, to_id):
    """Report the collected test difference between two nodes.

    :returns: detailed message describing the difference between the given
    collections, or None if they are equal.
    """
    if from_collection == to_collection:
        return None

    diff = difflib.unified_diff(
        from_collection,
        to_collection,
        fromfile=from_id,
        tofile=to_id,
    )
    # pylint: disable=protected-access
    error_message = py.builtin._totext(
        'Different tests were collected between {from_id} and {to_id}. '
        'The difference is:\n'
        '{diff}',
    ).format(from_id=from_id, to_id=to_id, diff='\n'.join(diff))
    msg = '\n'.join([x.rstrip() for x in error_message.split('\n')])
    return msg
