package ru.yandex.autotests.morda.exports.interfaces;

import ru.yandex.autotests.morda.exports.filters.MordaGeosFilter;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.04.14
 */
public interface EntryWithGeos extends Entry {
    MordaGeosFilter getGeos();
}
