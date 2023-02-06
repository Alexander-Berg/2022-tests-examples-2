select url, path, result, expected, String::JoinFromList(result, ';') = String::JoinFromList(expected, ';') as ok from (
    select url, path, $normalize_domain_with_path(url, path) as result, expected from (
        select 'сайт.рф' as url, '/' as path, AsList('сайт.рф') as expected
        union all
        select 'xn--80aswg.xn--p1ai' as url, '/' as path, AsList('сайт.рф') as expected
        union all
        select 'xn--trash' as url, '/' as path, ListCreate(ParseType("String")) as expected
        union all
        select '.' as url, '/' as path, ListCreate(ParseType("String")) as expected
        union all
        select '' as url, '/' as path, ListCreate(ParseType("String")) as expected
        union all
        select 'habr.ru' as url, '/' as path, AsList('habr.ru') as expected
        union all
        select 'habr.ru' as url, '/some' as path, AsList('habr.ru') as expected
        union all

        select 'afisha.yandex.ru' as url, '/' as path, AsList('afisha.yandex.ru', 'yandex.ru') as expected
        union all
        select 'alice.yandex.ru' as url, '/' as path, AsList('alice.yandex.ru') as expected
        union all
        select 'auto.ru' as url, '/' as path, AsList('auto.ru', 'yandex.ru') as expected
        union all
        select 'avia.yandex.ru' as url, '/' as path, AsList('avia.yandex.ru') as expected
        union all
        select 'browser.yandex.ru' as url, '/' as path, AsList('browser.yandex.ru') as expected
        union all
        select 'calendar.yandex.ru' as url, '/' as path, AsList('calendar.yandex.ru') as expected
        union all
        select 'dialogs.yandex.ru' as url, '/' as path, AsList('dialogs.yandex.ru') as expected
        union all
        select 'disk.yandex.ru' as url, '/' as path, AsList('disk.yandex.ru') as expected
        union all
        select 'edadeal.ru' as url, '/' as path, AsList('edadeal.ru', 'yandex.ru') as expected
        union all
        select 'education.yandex.ru' as url, '/' as path, AsList('education.yandex.ru') as expected
        union all
        select 'fotki.yandex.ru' as url, '/' as path, AsList('fotki.yandex.ru') as expected
        union all
        select 'kinopoisk.ru' as url, '/' as path, AsList('kinopoisk.ru', 'yandex.ru') as expected
        union all
        select 'mail.yandex.ru' as url, '/' as path, AsList('mail.yandex.ru', 'yandex.ru') as expected
        union all
        select 'market.yandex.ru' as url, '/' as path, AsList('market.yandex.ru') as expected
        union all
        select 'metrika.yandex.ru' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all
        select 'music.yandex.ru' as url, '/' as path, AsList('music.yandex.ru', 'yandex.ru') as expected
        union all
        select 'pdd.yandex.ru' as url, '/' as path, AsList('pdd.yandex.ru') as expected
        union all
        select 'plus.yandex.ru' as url, '/' as path, AsList('plus.yandex.ru') as expected
        union all
        select 'rabota.yandex.ru' as url, '/' as path, AsList('rabota.yandex.ru', 'yandex.ru') as expected
        union all
        select 'radio.yandex.ru' as url, '/' as path, AsList('music.yandex.ru', 'yandex.ru') as expected
        union all
        select 'rasp.yandex.ru' as url, '/' as path, AsList('rasp.yandex.ru', 'yandex.ru') as expected
        union all
        select 'realty.yandex.ru' as url, '/' as path, AsList('realty.yandex.ru', 'yandex.ru') as expected
        union all
        select 'station.yandex.ru' as url, '/' as path, AsList('station.yandex.ru') as expected
        union all
        select 'toloka.yandex.ru' as url, '/' as path, AsList('toloka.yandex.ru') as expected
        union all
        select 'translate.yandex.ru' as url, '/' as path, AsList('translate.yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/bus' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'travel.yandex.ru' as url, '/' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'tv.yandex.ru' as url, '/' as path, AsList('tv.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yadi.sk' as url, '/' as path, AsList('disk.yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/collections' as path, AsList('yandex.ru/collections', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/efir' as path, AsList('yandex.ru/efir', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/portal/video' as path, AsList('yandex.ru/efir', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/games' as path, AsList('yandex.ru/games', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/local' as path, AsList('yandex.ru/local', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/maps' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/news' as path, AsList('yandex.ru/news', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/pogoda' as path, AsList('yandex.ru/pogoda', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/q' as path, AsList('yandex.ru/q', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/search' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/images' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/sport' as path, AsList('yandex.ru/sport', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/time' as path, AsList('yandex.ru/time') as expected
        union all
        select 'yandex.ru' as url, '/tutor' as path, AsList('yandex.ru/tutor') as expected
        union all
        select 'yandex.ru' as url, '/uslugi' as path, AsList('yandex.ru/uslugi', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/znatoki' as path, AsList('yandex.ru/znatoki', 'yandex.ru') as expected
        union all
        select 'zen.yandex.ru' as url, '/' as path, AsList('zen.yandex.ru', 'yandex.ru') as expected
        union all
        select 'video.yandex.ru' as url, '/' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'ya.ru' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/touchsearch' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/padsearch' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/msearch' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/metro' as path, AsList('yandex.ru/metro', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/health' as path, AsList('yandex.ru/health', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/video' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/chat' as path, AsList('yandex.ru/chat') as expected
        union all
        select 'money.yandex.ru' as url, '/' as path, AsList('money.yandex.ru') as expected
        union all

        select 'yandex.ru' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'yandex.com' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'yandex.com.tr' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'yandex.kz' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'ya.ru' as url, '/' as path, AsList('yandex.ru/portal', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/search' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.com' as url, '/search' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.com.tr' as url, '/search' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'yandex.kz' as url, '/search' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all
        select 'ya.ru' as url, '/search' as path, AsList('yandex.ru/search', 'yandex.ru') as expected
        union all

        select 'yandex.ru' as url, '/sometrash' as path, ListCreate(ParseType("String?")) as expected
        union all

        select 'yandex.ru' as url, '/maps' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'yandex.com' as url, '/maps' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'yandex.com.tr' as url, '/maps' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'yandex.kz' as url, '/maps' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'maps.yandex.ru' as url, '/' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'maps.yandex.com' as url, '/' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'maps.yandex.com.tr' as url, '/' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all
        select 'maps.yandex.kz' as url, '/' as path, AsList('yandex.ru/maps', 'yandex.ru') as expected
        union all

        select 'taxi.yandex.ru' as url, '/' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.com' as url, '/' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.com.tr' as url, '/' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.kz' as url, '/' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.ru' as url, '/some' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.com' as url, '/some' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.com.tr' as url, '/some' as path, AsList('taxi.yandex.ru') as expected
        union all
        select 'taxi.yandex.kz' as url, '/some' as path, AsList('taxi.yandex.ru') as expected
        union all

        select 'yandex.ru' as url, '/bus' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.com' as url, '/bus' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.com.tr' as url, '/bus' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.kz' as url, '/bus' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.ru' as url, '/bus/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.com' as url, '/bus/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.com.tr' as url, '/bus/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'yandex.kz' as url, '/bus/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.ru' as url, '/' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.com' as url, '/' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.com.tr' as url, '/' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.kz' as url, '/' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.ru' as url, '/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.com' as url, '/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.com.tr' as url, '/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all
        select 'bus.yandex.kz' as url, '/smth' as path, AsList('travel.yandex.ru', 'yandex.ru') as expected
        union all

        select 'yandex.ru' as url, '/pogoda' as path, AsList('yandex.ru/pogoda', 'yandex.ru') as expected
        union all
        select 'pogoda.yandex.ru' as url, '/' as path, AsList('yandex.ru/pogoda', 'yandex.ru') as expected
        union all
        select 'p.ya.ru' as url, '/' as path, AsList('yandex.ru/pogoda', 'yandex.ru') as expected
        union all

        select 'metrika.yandex.ru' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all
        select 'metrika.yandex.com' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all
        select 'metrika.yandex.com.tr' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all
        select 'metrika.yandex.kz' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all
        select 'metrica.yandex.com' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all
        select 'metrica.yandex.com.tr' as url, '/' as path, AsList('metrika.yandex.ru') as expected
        union all

        select 'google.com' as url, '/maps' as path, AsList('google.ru/maps', 'google.ru') as expected
        union all
        select 'google.co.uk' as url, '/maps' as path, AsList('google.ru/maps', 'google.ru') as expected
        union all
        select 'google.ru' as url, '/maps' as path, AsList('google.ru/maps', 'google.ru') as expected
        union all
        select 'docs.google.com' as url, '/' as path, AsList('docs.google.com', 'google.ru') as expected
        union all
        select 'google.co.uk' as url, '/' as path, AsList('google.ru') as expected
        union all
        select 'google.com' as url, '/earth' as path, AsList('earth.google.com', 'google.ru') as expected
        union all
        select 'google.ru' as url, '/earth' as path, AsList('earth.google.com', 'google.ru') as expected
        union all
        select 'earth.google.com' as url, '/' as path, AsList('earth.google.com', 'google.ru') as expected
        union all
        select 'earth.google.ru' as url, '/' as path, AsList('earth.google.com', 'google.ru') as expected
        union all
        select 'drive.google.ru' as url, '/' as path, AsList('drive.google.com', 'google.ru') as expected
        union all
        select 'drive.google.com' as url, '/' as path, AsList('drive.google.com', 'google.ru') as expected
        union all
        select 'docs.google.ru' as url, '/' as path, AsList('docs.google.com', 'google.ru') as expected
    )
) order by ok;
