def get_country(country_iso3):
    if country_iso3 == 'RUS':
        return 'Russia'
    if country_iso3 == 'ISR':
        return 'Israel'
    if country_iso3 == 'FRA':
        return 'France'
    return None


def get_city_by_region_id(region_id):
    if region_id == 213:
        return 'Moscow'
    if region_id == 2:
        return 'Saint Petersburg'
    if region_id == 47:
        return 'Nizhny Novgorod'
    if region_id == 43:
        return 'Kazan'
    if region_id == 10502:
        return 'Paris'
    if region_id == 131:
        return 'Tel Aviv'

    return None
