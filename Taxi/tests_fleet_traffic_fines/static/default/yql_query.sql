USE hahn;
PRAGMA yt.TmpFolder = "//home/taxi/testing/features/fleet-traffic-fines/tmp";

$script = @@
replace_rules = (
    {'en': 'A', 'ru': u'А'},
    {'en': 'B', 'ru': u'В'},
    {'en': 'E', 'ru': u'Е'},
    {'en': 'K', 'ru': u'К'},
    {'en': 'M', 'ru': u'М'},
    {'en': 'H', 'ru': u'Н'},
    {'en': 'O', 'ru': u'О'},
    {'en': 'P', 'ru': u'Р'},
    {'en': 'C', 'ru': u'С'},
    {'en': 'T', 'ru': u'Т'},
    {'en': 'Y', 'ru': u'У'},
    {'en': 'X', 'ru': u'Х'})

def transliterate_by_view(s, from_lang, to_lang):
    if not s:
        return None
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    for rule in replace_rules:
        s = s.replace(rule[from_lang], rule[to_lang])
    return s
@@;
$render_car = Python2::transliterate_by_view(Callable<(String?, String, String)->String?>, $script);

$last_rides = (
    SELECT number_normalized
    FROM `//home/taxi/testing/replica/postgres/taximeter_orders_private/taximeter_orders`
    WHERE date_end IS NOT NULL AND date_end >= 1633251600
    GROUP BY $render_car(String::ToUpper(car_number),'ru','en') as number_normalized
);

INSERT INTO `//home/taxi/testing/features/fleet-traffic-fines/cars` WITH TRUNCATE
SELECT
    cars.park_id AS park_id,
    cars.car_id AS car_id,
    cars.number_normalized AS number_normalized,
    cars.registration_cert AS registration_cert
FROM `//home/taxi/testing/replica/mongo/struct/pda_private/pda_cars` AS cars
JOIN `//home/taxi/testing/replica/mongo/struct/pda_private/pda_parks` AS parks ON
  cars.park_id = parks.id
JOIN `//home/taxi/testing/replica/mongo/struct/pda_private/pda_cities` AS cities ON
  parks.city = cities.name
LEFT JOIN $last_rides AS last_rides ON
  cars.number_normalized == last_rides.number_normalized
WHERE
    cities.country_id = 'rus' AND
    COALESCE(cars.registration_cert, '') <> '' AND
    COALESCE(cars.rental, false) AND
    cars.status = 'working' AND
    (
      last_rides.number_normalized IS NOT NULL
      OR
      park_id IN ('PARK_01','PARK_02')
    );
