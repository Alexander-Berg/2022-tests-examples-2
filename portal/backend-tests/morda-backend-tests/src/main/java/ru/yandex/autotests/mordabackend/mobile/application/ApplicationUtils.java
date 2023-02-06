package ru.yandex.autotests.mordabackend.mobile.application;

import ru.yandex.autotests.mordabackend.beans.browserdesc.BrowserDesc;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.language.LanguageManager;
import ru.yandex.autotests.utils.morda.region.Region;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ANKARA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.IZMIR;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.LYUDINOVO;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;

/**
 * User: ivannik
 * Date: 21.08.2014
 */
public class ApplicationUtils {

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);

    public static final Map<UserAgent, String> PLATFORM_TYPES = new HashMap<UserAgent, String>() {{
        put(TOUCH, "iphone");
        put(WP8, "wp8");
        put(ANDROID_HTC_SENS, "android4");
    }};

    public static final List<Region> APPLICATION_REGIONS_MAIN = Arrays.asList(MOSCOW, KIEV, SANKT_PETERBURG,
            SAMARA, MINSK, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNIY_NOVGOROD, VOLGOGRAD, LYUDINOVO);


    public static final List<Region> APPLICATION_REGIONS_TR = Arrays.asList(ISTANBUL, IZMIR, BURSA, ANKARA);

    public static final List<Region> APPLICATION_REGIONS_ALL = new ArrayList<>();

    static {
        APPLICATION_REGIONS_ALL.addAll(APPLICATION_REGIONS_MAIN);
    }

    public static String getTitle(Language language, BrowserDesc browserDesc) {
        if (browserDesc.getDeviceName() != null) {
            return String.format(LanguageManager.getTranslation("home", "apps", "apps_for_vendor_name", language),
                    browserDesc.getDeviceName());
        } else {
            if (browserDesc.getIsTablet() == 1) {
                return String.format(LanguageManager.getTranslation("home", "apps", "apps_for_vendor_tablet", language),
                        browserDesc.getDeviceVendor());
            } else {
                return String.format(LanguageManager.getTranslation("home", "apps", "apps_for_vendor_phone", language),
                        browserDesc.getDeviceVendor());
            }
        }
    }

}
