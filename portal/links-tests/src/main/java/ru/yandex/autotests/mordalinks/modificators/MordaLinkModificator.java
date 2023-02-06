package ru.yandex.autotests.mordalinks.modificators;

import org.apache.http.client.CookieStore;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.06.14
 */
public abstract class MordaLinkModificator {
    public abstract String onAdd(String href);
    public abstract String onCompare(String href);
    public abstract String onCheck(String href, CookieStore cookieStore);
}
