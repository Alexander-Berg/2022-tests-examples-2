package ru.yandex.autotests.mordalinks.modificators;

import org.apache.http.client.CookieStore;

import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getYandexUid;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.06.14
 */
public class YandexUidModificator extends MordaLinkModificator {
    @Override
    public String onAdd(String href) {
        return href.replaceAll("yu=[^&]+", "yu=yandex_uid");
    }

    @Override
    public String onCompare(String href) {
        return href.replaceAll("yu=[^&]+", "yu=yandex_uid");
    }

    @Override
    public String onCheck(String href, CookieStore cookieStore) {
        return href.replaceAll("yu=[^&]+", "yu=" + getYandexUid(cookieStore));
    }
}
