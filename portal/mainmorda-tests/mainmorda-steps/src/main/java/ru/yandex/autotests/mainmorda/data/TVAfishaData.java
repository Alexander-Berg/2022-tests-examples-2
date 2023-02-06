package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.region.RegionManager;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.*;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.BELORUSSIA;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.UKRAINE;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;


/**
 * User: leonsabr
 * Date: 09.04.12
 */
public class TVAfishaData {
    private static final Properties CONFIG = new Properties();
    public static final String TV_LINK_PATTERN = CONFIG.getProtocol() + "://tv.yandex%s/";

    public static final String TV_EVENT_HREF_PATTERN = CONFIG.getProtocol() + "://tv\\.yandex\\%s/%s/program/[0-9]+\\?eventId=[0-9]+";
    public static final String TIME_PATTERN = "([0-1][0-9]|2[0-3]):[0-5][0-9]";

    public static final Map<Domain, Region> CAPITAL_TV_CODE = new HashMap<Domain, Region>() {{
        put(Domain.RU, MOSCOW);
        put(UA, UKRAINE);
        put(Domain.KZ, ASTANA);
        put(Domain.BY, BELORUSSIA);
    }};

    ////////Afisha
    public static final String AFISHA_EVENT_HREF_PATTERN =
            "https://afisha\\.yandex\\%s/events/[\\da-а]{24}\\?city=\\w+";

    public static final HashMap<Domain, String> AFISHA_HREFS = new HashMap<Domain, String>() {{
        put(Domain.RU, "https://afisha.yandex.ru/?city=moscow");
        put(UA, "https://afisha.yandex.ua/events/?city=kyiv");
        put(Domain.KZ, "https://afisha.yandex.kz/?city=astana");
        put(Domain.BY, "https://afisha.yandex.by/?city=minsk");
    }};

    public static final List<String> GENRES = new ArrayList<String>() {{
        add("детектив");
        add("боевик");
        add("приключения");
        add("комедия");
        add("драма");
        add("премьера");
        add("триллер");
        add("ужасы");
        add("экшн");
        add("экшен");
        add("кино");
        add("анимационная комедия");
        add("криминал");
        add("военный");
        add("спорт");
        add("фантастика");
        add("фэнтези");
        add("экшн-комедия");
        add("мультфильм");
        add("анимация");
        add("кинофестиваль");
        add("мюзикл");
        add("мелодрама");
        add("музыкальный");
        add("исторический");
        add("короткометражный фильм");
        add("комедийный боевик");
        add("анимационный");
        add("приключенческий боевик");
        add("биографический");
        add("семейный");
        add("мистика");
        if (CONFIG.domainIs(UA)) {
            add("трилер");
        }
    }};

    public static final Matcher<Integer> TV_ITEMS_NUMBER =
            equalTo(5);

    public static int getExpectedNumberOfAfishaEvents() {
        return isMiddleOfWeek(RegionManager.getDayOfWeek(MOSCOW)) ? 4 : 6;
    }

    private static boolean isMiddleOfWeek(int day) {
        return day >= Calendar.MONDAY && day <= Calendar.WEDNESDAY;
    }

    public static boolean isPremiereDay() {
        return isMiddleOfWeek(RegionManager.getDayOfWeek(MOSCOW));
    }

    public static int getNumberOfTvEvents(Region region) {
        int curHour = RegionManager.getHour(region);
        int dayOfWeek = RegionManager.getDayOfWeek(region);
        if (dayOfWeek == Calendar.SATURDAY || dayOfWeek == Calendar.SUNDAY) {
            if (curHour >= 10 || curHour < 3) {
                return 5;
            }
            return 3;
        } else if (dayOfWeek == Calendar.FRIDAY) {
            if (curHour >= 18 || curHour < 3) {
                return 5;
            }
            return 3;
        } else {
            if ( curHour >= 17 || curHour < 3) {
                return 5;
            }
            return 3;
        }
    }
}
