CURRENCY_DICT = {
    'AM': 'AMD',
    'RU': 'RUS',
    'BY': 'BYN',
    'RU_MSC': 'RUS',
    None: None
}

# 'технический код страны': ['двухсимвольный код страны', 'трёхсимвольный код страны'] 
COUNTRY_CODE_DICT = {
    'AM': ['AM', 'arm'],
    'RU': ['RU', 'rus'],
    'BY': ['BY', 'blr'],
    'RU_MSC': ['RU', 'rus'],
    None: [None, None]
}

COUNTRY_NAME_EN_DICT = {
    'Армения': 'Armenia',
    'Россия': 'Mother Russia',
    'Белоруссия': 'Belarus',
    'Москва': 'Moscow',
    None: None
}

AGGLOMERATION_NAME_DICT = {
    'br_erevan': ['Erevan', 'Ереван'],
    'br_hatanga': ['Very cold - do not come by', 'Хатанга'],
    'br_moscow': ['Moscow', 'Москва'],
    'br_orsha': ['Orsha', 'Орша'],
    'br_soligorsk': ['Soligorsk', 'Солигорск'],
    None: [None, None]
}

EXAMPLE_HIERARCHY = [
        {
            'node_id': 'op_root',
            'hierarchy_type': 'op',
            'node_type': 'root',
            'name_en': 'Operational Hierarchy',
            'country_short_code': None,
            'child_geo_nodes': ['op_russia', 'op_armenia', 'op_belarus'],
            'time_zone_code': None,
            'name_ru': 'Операционная иерархия'
        },
        {
            'node_id': 'op_russia',
            'hierarchy_type': 'op',
            'node_type': 'country',
            'name_en': 'Mother Russia',
            'country_short_code': 'RU',
            'child_geo_nodes': ['br_moscow', 'op_franchise', 'op_siberia'],
            'time_zone_code': None,
            'name_ru': 'Россия'
        },
        {
            'node_id': 'op_armenia',
            'hierarchy_type': 'op',
            'node_type': 'country',
            'name_en': 'Armenia',
            'country_short_code': 'AM',
            'child_geo_nodes': ['br_erevan'],
            'time_zone_code': None,
            'name_ru': 'Армения'
        },
        {
            'node_id': 'br_erevan',
            'hierarchy_type': 'agglomeration',
            'node_type': 'agglomeration',
            'name_en': 'Erevan',
            'country_short_code': None,
            'child_geo_nodes': [],
            'population': 1300000,
            'child_tariff_zones': ['erevan', 'erevan_region'],
            'time_zone_code': 'Asia/Yerevan',
            'name_ru': 'Ереван'
        },
        {
            'node_id': 'op_belarus',
            'hierarchy_type': 'op',
            'node_type': 'country',
            'name_en': 'Belarus',
            'country_short_code': 'BY',
            'child_geo_nodes': ['br_orsha', 'br_soligorsk'],
            'time_zone_code': None,
            'name_ru': 'Белоруссия'
        },
        {
            'node_id': 'br_orsha',
            'hierarchy_type': 'agglomeration',
            'node_type': 'agglomeration',
            'name_en': 'Orsha',
            'country_short_code': None,
            'child_geo_nodes': [],
            'population': 110000,
            'child_tariff_zones': ['orsha'],
            'time_zone_code': 'Europe/Minsk',
            'name_ru': 'Орша'
        },
        {
            'node_id': 'br_soligorsk',
            'hierarchy_type': 'agglomeration',
            'node_type': 'agglomeration',
            'name_en': 'Soligorsk',
            'country_short_code': None,
            'child_geo_nodes': [],
            'population': 110000,
            'child_tariff_zones': ['soligorsk'],
            'time_zone_code': 'Europe/Minsk',
            'name_ru': 'Солигорск'
        },
        {
            'node_id': 'op_franchise',
            'hierarchy_type': 'op',
            'node_type': 'node',
            'name_en': 'Franchise towns',
            'country_short_code': None,
            'child_geo_nodes': ['br_hatanga'],
            'parent_priority': 10,
            'time_zone_code': None,
            'name_ru': 'Франшиза'
        },
        {
            'node_id': 'op_siberia',
            'hierarchy_type': 'op',
            'node_type': 'node',
            'name_en': 'Siberia',
            'country_short_code': None,
            'child_geo_nodes': ['br_hatanga'],
            'time_zone_code': None,
            'name_ru': 'Сибирь'
        },
        {
            'node_id': 'br_moscow',
            'hierarchy_type': 'agglomeration',
            'node_type': 'agglomeration',
            'name_en': 'Moscow',
            'country_short_code': None,
            'child_geo_nodes': ['br_moscow_adm', 'br_mytischi'],
            'population': 12500000,
            'child_tariff_zones': ['dme', 'svo', 'vko'],
            'time_zone_code': None,
            'name_ru': 'Москва'
        },
        {
            'node_id': 'br_moscow_adm',
            'hierarchy_type': 'br',
            'node_type': 'node',
            'name_en': 'Moscow (Inner)',
            'country_short_code': None,
            'child_geo_nodes': [],
            'child_tariff_zones': ['moscow', 'khimki', 'zelenograd', 'butovo'],
            'time_zone_code': 'Europe/Moscow',
            'name_ru': 'Москва (адм)'
        },
        {
            'node_id': 'br_mytischi',
            'hierarchy_type': 'br',
            'node_type': 'node',
            'name_en': 'Mytischi',
            'country_short_code': None,
            'child_geo_nodes': [],
            'child_tariff_zones': ['mytischi', 'korolev'],
            'time_zone_code': 'Europe/Moscow',
            'name_ru': 'Мытищи'
        },
        {
            'node_id': 'br_hatanga',
            'hierarchy_type': 'agglomeration',
            'node_type': 'agglomeration',
            'name_en': 'Very cold - do not come by',
            'country_short_code': None,
            'child_geo_nodes': [],
            'population': 80000,
            'child_tariff_zones': ['hatanga', 'cold_desert'],
            'time_zone_code': 'Asia/Krasnoyarsk',
            'name_ru': 'Хатанга'
        },
        {
            'node_id': 'fi_root',
            'hierarchy_type': 'fi',
            'node_type': 'root',
            'name_en': 'Financial Hierarchy',
            'country_short_code': None,
            'child_geo_nodes': ['fi_cis'],
            'time_zone_code': None,
            'name_ru': 'Финансовая иерархия'
        },
        {
            'node_id': 'fi_cis',
            'hierarchy_type': 'fi',
            'node_type': 'node',
            'name_en': 'Commonwealth of Independent States',
            'country_short_code': None,
            'child_geo_nodes': ['fi_1m+', 'fi_100k+', 'fi_100k-'],
            'time_zone_code': None,
            'name_ru': 'СНГ'
        },
        {
            'node_id': 'fi_1m+',
            'hierarchy_type': 'fi',
            'node_type': 'node',
            'name_en': 'Millionaire cities',
            'country_short_code': None,
            'child_geo_nodes': ['br_erevan', 'br_moscow'],
            'time_zone_code': None,
            'name_ru': '1m+'
        },
        {
            'node_id': 'fi_100k+',
            'hierarchy_type': 'fi',
            'node_type': 'node',
            'name_en': '100k+ cities',
            'country_short_code': None,
            'child_geo_nodes': [],
            'time_zone_code': None,
            'name_ru': '100k+'
        },
        {
            'node_id': 'fi_100k-',
            'hierarchy_type': 'fi',
            'node_type': 'node',
            'name_en': 'Small towns',
            'country_short_code': None,
            'child_geo_nodes': ['br_hatanga'],
            'time_zone_code': None,
            'name_ru': '100k-'
        },
        {
            'node_id': 'br_root',
            'hierarchy_type': 'br',
            'node_type': 'root',
            'name_en': 'Basic Root',
            'country_short_code': None,
            'child_geo_nodes': ['br_russia'],
            'time_zone_code': None,
            'name_ru': 'Базовая иерархия'
        },
        {
            'node_id': 'br_russia',
            'hierarchy_type': 'br',
            'node_type': 'node',
            'name_en': 'The Basis of Mjther Russia',
            'country_short_code': None,
            'child_geo_nodes': ['br_moscow', 'br_hatanga'],
            'time_zone_code': None,
            'name_ru': 'Россия'
        },
    ]
