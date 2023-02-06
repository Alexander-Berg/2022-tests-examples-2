import hashlib


def get_feedback_id(order_id, driver_id, feed_type):
    hash_key = (order_id + driver_id + str(feed_type)).encode('utf-8')
    return hashlib.blake2b(hash_key, digest_size=16).hexdigest()


def get_feed_type_code(feed_type):
    types = {
        'passenger': 1,
        'sender': 2,
        'recipient': 3,
        'eater': 4,
        'restaurant': 5,
        'grocery': 6,
        'misc': 7,
    }
    return types.get(feed_type, 0)
