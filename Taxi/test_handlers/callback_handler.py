import typing


async def handle(
        callback: typing.Callable[[dict], None],
        **kwargs
) -> None:
    callback(kwargs)
