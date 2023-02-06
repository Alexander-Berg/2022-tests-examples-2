package ru.yandex.autotests.morda.monitorings;

import ru.yandex.geobase.regions.*;

import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Belarus.VITEBSK;
import static ru.yandex.geobase.regions.Germany.BERLIN;
import static ru.yandex.geobase.regions.Kazakhstan.ALMATY;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.*;
import static ru.yandex.geobase.regions.Russia.PETROPAVLOVSK;
import static ru.yandex.geobase.regions.Russia.SARATOV;
import static ru.yandex.geobase.regions.Turkey.ANKARA_11503;
import static ru.yandex.geobase.regions.Turkey.ISTANBUL_11508;
import static ru.yandex.geobase.regions.Ukraine.KYIV;
import static ru.yandex.geobase.regions.Ukraine.LVIV;
import static ru.yandex.geobase.regions.UnitedKingdom.LONDON;
import static ru.yandex.geobase.regions.UnitedStates.NEW_YORK;
import static ru.yandex.geobase.regions.UnitedStates.WASHINGTON_87;

/**
 * Created by eoff on 14/02/2017.
 */
public class MonitoringsData {

    public static final List<GeobaseRegion> AFISHA_REGIONS = asList(MOSCOW, SAINT_PETERSBURG, YEKATERINBURG, VORONEZH,
            NIZHNY_NOVGOROD, ROSTOV_NA_DONU, KRASNODAR, CHELYABINSK,SAMARA, NOVOSIBIRSK, VOLGOGRAD, UFA, PERM,
            SARATOV, PETROPAVLOVSK,
            MINSK,
            KYIV, LVIV,
            ASTANA, ALMATY
    );

    public static final List<GeobaseRegion> NEWS_REGIONS = asList(MOSCOW, SAINT_PETERSBURG, YEKATERINBURG, VORONEZH,
            NIZHNY_NOVGOROD, ROSTOV_NA_DONU, KRASNODAR, CHELYABINSK,SAMARA, NOVOSIBIRSK, VOLGOGRAD, UFA, PERM,
            SARATOV, PETROPAVLOVSK,
            MINSK, VITEBSK,
            KYIV, LVIV,
            ASTANA, ALMATY,
            LONDON, NEW_YORK, BERLIN
    );

    public static final List<GeobaseRegion> WEATHER_REGIONS = asList(MOSCOW, SAINT_PETERSBURG, YEKATERINBURG, VORONEZH,
            NIZHNY_NOVGOROD, ROSTOV_NA_DONU, KRASNODAR, CHELYABINSK,SAMARA, NOVOSIBIRSK, VOLGOGRAD, UFA, PERM,
            SARATOV, PETROPAVLOVSK,
            MINSK, VITEBSK,
            KYIV, LVIV,
            ASTANA, ALMATY,
            ISTANBUL_11508, ANKARA_11503,
            LONDON, NEW_YORK, BERLIN
    );

    public static final List<GeobaseRegion> TV_REGIONS = asList(MOSCOW, SAINT_PETERSBURG, YEKATERINBURG, VORONEZH,
            NIZHNY_NOVGOROD, ROSTOV_NA_DONU, KRASNODAR, CHELYABINSK, SAMARA,
            NOVOSIBIRSK, VOLGOGRAD, UFA, PERM, SARATOV, PETROPAVLOVSK,
            KYIV, VITEBSK,
            ASTANA, ALMATY,
            WASHINGTON_87
    );

    public static final List<GeobaseRegion> TRAFFIC_REGIONS = asList(MOSCOW, KYIV, SAINT_PETERSBURG, YEKATERINBURG,
            PERM, SAMARA, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNY_NOVGOROD, VOLGOGRAD, ROSTOV_NA_DONU
    );

    public static final List<GeobaseRegion> SERVICES_REGIONS = asList(MOSCOW, SAINT_PETERSBURG,
            KYIV,
            MINSK,
            ASTANA, ALMATY,
            WASHINGTON_87
    );

    public static final List<GeobaseRegion> RASP_REGIONS = asList(MOSCOW, SAINT_PETERSBURG, YEKATERINBURG, VORONEZH,
            NIZHNY_NOVGOROD, ROSTOV_NA_DONU, KRASNODAR, CHELYABINSK, SAMARA,
            NOVOSIBIRSK, VOLGOGRAD, UFA, PERM, SARATOV, PETROPAVLOVSK,
            KYIV, VITEBSK,
            ASTANA, ALMATY,
            WASHINGTON_87
    );

    public static final List<GeobaseRegion> STOCKS_REGIONS = asList(
            MOSCOW, SAINT_PETERSBURG,
            KYIV, LVIV,
            MINSK, VITEBSK,
            ASTANA, ALMATY,
            WASHINGTON_87
    );

    public static final List<GeobaseRegion> COLLECTIONS_REGIONS = asList(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK);

    public static final List<GeobaseRegion> EDADEAL_REGIONS = asList(MOSCOW, SAINT_PETERSBURG);

}
