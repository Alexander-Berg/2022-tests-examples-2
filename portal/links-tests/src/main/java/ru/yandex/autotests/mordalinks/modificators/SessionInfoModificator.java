package ru.yandex.autotests.mordalinks.modificators;

import org.apache.http.client.CookieStore;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.06.14
 */
public class SessionInfoModificator extends MordaLinkModificator {
    @Override
    public String onAdd(String href) {
        return href.replaceAll("session_info=[^&]+", "session_info=0");
    }

    @Override
    public String onCompare(String href) {
        return href.replaceAll("session_info=[^&]+", "session_info=0");
    }

    @Override
    public String onCheck(String href, CookieStore cookieStore) {
        return href;
    }
}
