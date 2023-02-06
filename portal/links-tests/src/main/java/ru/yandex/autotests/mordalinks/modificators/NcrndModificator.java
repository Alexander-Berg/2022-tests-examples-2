package ru.yandex.autotests.mordalinks.modificators;

import org.apache.http.client.CookieStore;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.06.14
 */
public class NcrndModificator extends MordaLinkModificator {
    @Override
    public String onAdd(String href) {
        return onCompare(href);
    }

    @Override
    public String onCompare(String href) {
        return href.replaceAll("\\?ncrnd=[^&]+$", "")
                .replaceAll("\\?ncrnd%3D[^&]+$", "")
                .replaceAll("ncrnd=[^&]+&", "")
                .replaceAll("ncrnd%3D[^&]+&", "");
    }

    @Override
    public String onCheck(String href, CookieStore cookieStore) {
        return href;
    }
}
