package ru.yandex.autotests.mordalinks.modificators;

import org.apache.http.client.CookieStore;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.06.14
 */
public class RedircntModificator extends MordaLinkModificator {
    @Override
    public String onAdd(String href) {
        return href;
    }

    @Override
    public String onCompare(String href) {
        return href.replaceAll("redircnt=[^&]+", "redircnt=0");
    }

    @Override
    public String onCheck(String href, CookieStore cookieStore) {
        return href;
    }
}
