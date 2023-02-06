# pylint: disable=unused-argument
async def handle(key, arg, stash, **kwargs):
    if key in set(('wrong_key',)):
        return None

    return key
