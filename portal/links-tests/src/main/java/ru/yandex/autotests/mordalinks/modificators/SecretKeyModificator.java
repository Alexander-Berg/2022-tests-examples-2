package ru.yandex.autotests.mordalinks.modificators;

import org.apache.http.client.CookieStore;

import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getSecretKey;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.06.14
 */
public class SecretKeyModificator extends MordaLinkModificator {
    @Override
    public String onAdd(String href) {
        return href.replaceAll("sk=[^&]+", "sk=secret_key");
    }

    @Override
    public String onCompare(String href) {
        return href.replaceAll("sk=[^&]+", "sk=secret_key");
    }

    @Override
    public String onCheck(String href, CookieStore cookieStore) {
        return href.replaceAll("sk=[^&]+", "sk=" + getSecretKey(cookieStore));
    }
}
