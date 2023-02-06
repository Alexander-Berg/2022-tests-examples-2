package ru.yandex.autotests.morda.pages;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public interface AbstractDesktopMorda<T> extends Morda<T> {

    @Override
    default String getDefaultUserAgent() {
        return CONFIG.getDesktopUserAgent();
    }
}
