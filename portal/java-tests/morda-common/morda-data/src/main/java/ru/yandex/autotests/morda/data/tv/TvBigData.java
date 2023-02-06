package ru.yandex.autotests.morda.data.tv;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public interface TvBigData extends TvData {
    @Override
    default String getHost() {
        return getBigHost();
    }
}
