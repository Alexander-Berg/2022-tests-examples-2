async def handle(raise_error: bool = False, **_):
    if raise_error:
        raise Exception('__exc__')
