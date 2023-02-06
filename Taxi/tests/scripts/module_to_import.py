def divide_by_zero():
    return 1 / 0


def function_to_succeed(one, two):
    return {
        'one': one,
        'two': two
    }


async def async_function_to_succeed(one, two):
    return {
        'one': one,
        'two': two
    }


def function_not_serializable():
    return open


NOT_A_FUNCTION = 0
