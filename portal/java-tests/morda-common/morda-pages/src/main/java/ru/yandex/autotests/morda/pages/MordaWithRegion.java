package ru.yandex.autotests.morda.pages;

import ru.yandex.geobase.regions.GeobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/05/16
 */
public interface MordaWithRegion<T> extends Morda<T> {
    GeobaseRegion getRegion();

    T region(GeobaseRegion region);
}
