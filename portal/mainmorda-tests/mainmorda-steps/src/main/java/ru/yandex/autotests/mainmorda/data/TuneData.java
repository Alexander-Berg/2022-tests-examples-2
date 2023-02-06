package ru.yandex.autotests.mainmorda.data;

import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * User: eoff
 * Date: 01.02.13
 */
public class TuneData {
    private static final Properties CONFIG = new Properties();
    private static final String YANDEX_URL_PATTERN_NO_DOMAIN =
            CONFIG.getBaseURL().substring(0, CONFIG.getBaseURL().length() - 3);

    public static final String YANDEX_URL_PATTERN = YANDEX_URL_PATTERN_NO_DOMAIN
            + "%s/";

    public static final String TUNE_URL_PATTERN =
            CONFIG.getProtocol() + "://tune.yandex.ru/region/?retpath="
                    + UrlManager.encodeRetpath(YANDEX_URL_PATTERN_NO_DOMAIN) + "%s" +
                    "%2F%3Fdomredir%3D1";
    public static final String TUNE_BANNER_URL = CONFIG.getProtocol() + "://tune.yandex.ru/banner/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1";
    public static final List<Domain> DOMAINS =
            new ArrayList<Domain>(Arrays.asList(Domain.RU, Domain.UA, Domain.KZ, Domain.BY));

    static {
        DOMAINS.remove(CONFIG.getBaseDomain());
    }

    public static final String YANDEX_RU = String.format(YANDEX_URL_PATTERN, Domain.RU);
}
