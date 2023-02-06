class CashbackSettings:
    cashback = None
    active_from = None
    active_till = None

    def __init__(self, cashback, active_from, active_till):
        self.cashback = cashback
        self.active_from = active_from
        self.active_till = active_till


def get_cashback_settings(place_id, cursor):
    cursor.execute(
        'SELECT cashback, active_from, active_till, type '
        'FROM eats_plus.cashback_settings '
        f'WHERE place_id={place_id}'
        ' ORDER BY active_from;',
    )
    settings = cursor.fetchall()
    if not settings:
        return {}

    result = {}
    for setting in settings:
        if setting[3] == 'eda':
            result.setdefault('eda', []).append(
                CashbackSettings(
                    cashback=setting[0],
                    active_from=setting[1],
                    active_till=setting[2],
                ),
            )
        if setting[3] == 'place':
            result.setdefault('place', []).append(
                CashbackSettings(
                    cashback=setting[0],
                    active_from=setting[1],
                    active_till=setting[2],
                ),
            )
    return result


class PlusSettings:
    place_id = None
    active = None
    eda_cashback = None
    place_cashback = None

    def __init__(self, place_id, active):
        self.place_id = place_id
        self.active = active


def get_plus_settings(place_id, cursor):
    cursor.execute(
        'SELECT active '
        'FROM eats_plus.place_plus_settings '
        f'WHERE place_id={place_id};',
    )
    settings = cursor.fetchone()
    if settings is None:
        return None
    plus_settings = PlusSettings(place_id=place_id, active=settings[0])
    cashback_settings = get_cashback_settings(place_id, cursor)
    plus_settings.eda_cashback = cashback_settings.get('eda', [])
    plus_settings.place_cashback = cashback_settings.get('place', [])
    return plus_settings
