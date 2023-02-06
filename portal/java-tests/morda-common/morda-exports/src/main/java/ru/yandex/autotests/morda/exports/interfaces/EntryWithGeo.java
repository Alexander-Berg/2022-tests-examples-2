package ru.yandex.autotests.morda.exports.interfaces;

import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.04.14
 */
public interface EntryWithGeo extends Entry {
    MordaGeoFilter getGeo();
}
