package ru.yandex.autotests.mordamobile.data;

import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.APPS_ALL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.APPS_VENDOR_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class AppsData {
    private static final Properties CONFIG = new Properties();

    private static final String TITLE = getTranslation(APPS_VENDOR_TITLE, CONFIG.getLang()).replace("%s", "смартфона на Android");


    public static final LinkInfo TITLE_LINK = new LinkInfo(
            equalTo(TITLE),
            startsWith("https://mobile.yandex.ru/apps/android"),
            hasAttribute(HREF, startsWith("https://mobile.yandex.ru/"))
    );

    public static final LinkInfo ALL_APPS_LINK = new LinkInfo(
            equalTo(getTranslation(APPS_ALL, CONFIG.getLang())),
            startsWith("https://mobile.yandex.ru/apps/android"),
            hasAttribute(HREF, startsWith("https://mobile.yandex.ru/"))
    );
}
