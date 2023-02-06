package ru.yandex.autotests.morda.data.tv;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11/08/16
 */
public interface TvTouchData extends TvData {
    @Override
    default String getHost() {
        return getTouchHost();
    }
}
