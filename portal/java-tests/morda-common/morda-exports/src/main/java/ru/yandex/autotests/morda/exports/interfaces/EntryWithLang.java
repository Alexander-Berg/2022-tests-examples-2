package ru.yandex.autotests.morda.exports.interfaces;

import ru.yandex.autotests.morda.exports.filters.MordaLanguageFilter;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.04.14
 */
public interface EntryWithLang extends Entry {
    MordaLanguageFilter getLang();
}
