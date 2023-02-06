package ru.yandex.autotests.morda.pages;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public interface AbstractPdaMorda<T> extends Morda<T> {

    @Override
    default String getDefaultUserAgent() {
        return CONFIG.getPdaUserAgent();
    }
}
