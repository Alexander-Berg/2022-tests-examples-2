package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.REGION_NEAR;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.REGION_YA;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class GeoData {
    private static final Properties CONFIG = new Properties();

    public static final LinkInfo POI_LINK = new LinkInfo(
            equalTo(getTranslation(REGION_NEAR, CONFIG.getLang())),
            startsWith(CONFIG.getBaseURL())
    );

    public static final Matcher<String> LOCATION_TEXT_MATCHER = startsWith(getTranslation(REGION_YA, CONFIG.getLang()));


}
