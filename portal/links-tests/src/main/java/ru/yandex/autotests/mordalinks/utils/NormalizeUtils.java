package ru.yandex.autotests.mordalinks.utils;

import org.apache.http.client.CookieStore;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordalinks.modificators.MordaLinkModificator;
import ru.yandex.autotests.mordalinks.modificators.RedircntModificator;
import ru.yandex.autotests.mordalinks.modificators.SecretKeyModificator;
import ru.yandex.autotests.mordalinks.modificators.YandexUidModificator;

import java.util.Arrays;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.14
 */
public class NormalizeUtils {

    private static final Logger LOG = Logger.getLogger(NormalizeUtils.class);
    public static final List<MordaLinkModificator> MODIFICATORS = Arrays.asList(
            new SecretKeyModificator(),
            new YandexUidModificator(),
            new ru.yandex.autotests.mordalinks.modificators.NcrndModificator(),
            new ru.yandex.autotests.mordalinks.modificators.SessionInfoModificator(),
            new RedircntModificator(),
            new ru.yandex.autotests.mordalinks.modificators.IdKeyModificator()
    );

    public static String normalizeOnCompare(String href) {
        if (href == null) {
            return null;
        }
        for (MordaLinkModificator modificator : MODIFICATORS) {
            href = modificator.onCompare(href);
        }
        return href;
    }

    public static String normalizeOnAdd(String href) {
        if (href == null) {
            return null;
        }
        for (MordaLinkModificator modificator : MODIFICATORS) {
            href = modificator.onAdd(href);
        }
        return href;
    }

    public static String normalizeOnCheck(String href, CookieStore cookieStore) {
        if (href == null) {
            return null;
        }
        for (MordaLinkModificator modificator : MODIFICATORS) {
            href = modificator.onCheck(href, cookieStore);
        }
        return href;
    }


}
