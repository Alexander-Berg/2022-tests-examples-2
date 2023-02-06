def make_price(price):
    return {
        'boarding': price,
        'distance': price,
        'time': price,
        'waiting': price,
        'requirements': price,
        'transit_waiting': price,
        'destination_waiting': price,
    }


def split_price(price):
    return make_price(price / 7)


def fill_price(
        boarding=0,
        distance=0,
        time=0,
        waiting=0,
        requirements=0,
        transit_waiting=0,
        destination_waiting=0,
):
    return {
        'boarding': boarding,
        'distance': distance,
        'time': time,
        'waiting': waiting,
        'requirements': requirements,
        'transit_waiting': transit_waiting,
        'destination_waiting': destination_waiting,
    }
