package ru.yandex.autotests.morda.tests.searchapi;

import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/05/16
 */
@Resource.Classpath("morda-searchapi-tests.properties")
public class MordaSearchapiTestsProperties {
    public static final List<GeobaseRegion> WEATHER_REGIONS = asList(
            Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, ASTANA
    );

    public static final List<GeobaseRegion> NOW_REGIONS = asList(
            Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, ASTANA
    );


    public static final List<GeobaseRegion> TOPNEWS_REGIONS = asList(
            Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, ASTANA
    );

    public static final List<GeobaseRegion> TRANSPORT_REGIONS = asList(
            Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, ASTANA
    );

    public static final List<GeobaseRegion> POI_REGIONS = asList(
            Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.YEKATERINBURG,
            Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV
    );

    public static final List<GeobaseRegion> STOCKS_REGIONS = asList(
            Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, ASTANA
    );

    public static final List<GeobaseRegion> TV_REGIONS = asList(
            Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, ASTANA
    );

    public static final List<GeobaseRegion> APPLICATION_REGIONS = asList(
            Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, Russia.NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, Kazakhstan.ASTANA
    );

    public static final List<GeobaseRegion> INFORMER_REGIONS = asList(
            Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
            Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, Russia.NIZHNY_NOVGOROD, Russia.SAMARA,
            Belarus.MINSK, Belarus.GOMEL,
            Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
            Kazakhstan.ALMATY, Kazakhstan.ASTANA
    );

    public static final List<GeobaseRegion> BRIDGES_REGIONS = asList(
            Russia.SAINT_PETERSBURG
    );


    private MordaPagesProperties mordaPagesProperties = new MordaPagesProperties();

    public MordaSearchapiTestsProperties() {
        PropertyLoader.populate(this);
    }

    public MordaPagesProperties pages() {
        return mordaPagesProperties;
    }

}
