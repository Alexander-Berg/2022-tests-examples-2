package ru.yandex.autotests.morda.data;

import ru.yandex.geobase.regions.GeobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public interface DataWithRegion {
    GeobaseRegion getRegion();
}
