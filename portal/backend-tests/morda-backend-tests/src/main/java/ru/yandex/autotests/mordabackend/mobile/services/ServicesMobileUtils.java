package ru.yandex.autotests.mordabackend.mobile.services;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
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
 * Date: 22.08.2014
 */
public class ServicesMobileUtils {

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);

    public static final List<UserAgent> USER_AGENTS = Arrays.asList(TOUCH, WP8, ANDROID_HTC_SENS);

    public static final List<Region> SERVICES_MOBILE_REGIONS_MAIN = Arrays.asList(MOSCOW, KIEV, SANKT_PETERBURG,
            SAMARA, MINSK, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNIY_NOVGOROD, VOLGOGRAD, LYUDINOVO);


    public static final List<Region> SERVICES_MOBILE_REGIONS_TR = Arrays.asList(ISTANBUL, IZMIR, BURSA, ANKARA);

    public static final List<Region> SERVICES_MOBILE_REGIONS_ALL = new ArrayList<>();
    static {
        SERVICES_MOBILE_REGIONS_ALL.addAll(SERVICES_MOBILE_REGIONS_MAIN);
        SERVICES_MOBILE_REGIONS_ALL.addAll(SERVICES_MOBILE_REGIONS_TR);
    }

    public static Matcher<String> getHrefMatcher(ServicesV122Entry entry) {
        return anyOf(
                containsString(entry.getHref().replace("clid=506", "clid=505").replace("clid=691", "clid=505")),
                equalTo(entry.getTouch())
        );
    }

    public static Matcher<String> getUrlMatcher(ServicesV122Entry entry) {
        if (entry.getTouch() != null && !entry.getTouch().equals("")) {
            return equalTo(entry.getTouch());
        } else if (entry.getPda() != null && !entry.getPda().equals("")) {
            return equalTo(entry.getPda());
        } else {
            return equalTo(entry.getHref().replace("clid=506", "clid=505").replace("clid=691", "clid=505"));
        }
    }

    public static Matcher<String> getSearchUrlMatcher(ServicesV122Entry servicesV12Entry) {
        if (servicesV12Entry.getSearchMobile() != null && !servicesV12Entry.getSearchMobile().equals("")) {
            return equalTo(servicesV12Entry.getSearchMobile());
        } else {
            return equalTo(servicesV12Entry.getSearch());
        }
    }
}
