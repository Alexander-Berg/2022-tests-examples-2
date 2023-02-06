package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.AfishaTvBlock;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.region.RegionManager;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.Calendar;
import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_CHANNELS_TEXT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_LESS10;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_LESS3;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_LESS5;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_LESS7;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_NOANNOUNCES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TV_QUANTITY;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: eoff
 * Date: 14.12.12
 */
public class TvSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> ADD_ALL_TEXT = equalTo("»»");
    public static final Matcher<String> ADD_TEXT = equalTo("»");
    public static final Matcher<String> REMOVE_ALL_TEXT = equalTo("««");
    public static final Matcher<String> REMOVE_TEXT = equalTo("«");

    public static final int DEFAULT_TV_ITEMS_NUMBER = 5;

    public static final Matcher<String> TV_TITLE_TEXT = equalTo(getTranslation(TV_CHANNELS_TEXT, CONFIG.getLang()));
    public static final Matcher<String> TV_COUNT_TEXT = equalTo(getTranslation(TV_QUANTITY, CONFIG.getLang()));
    public static final Matcher<String> TV_NO_ANNOUNCE_TEXT = equalTo(getTranslation(TV_NOANNOUNCES, CONFIG.getLang()));

    public static final Map<Domain, Integer> DEFAULT_CHANNELS_CHOSEN_MAP = new HashMap<Domain, Integer>() {{
        put(RU, 5);
        put(Domain.UA, 8);
        put(Domain.BY, 8);
        put(Domain.KZ, 8);
    }};

    public static final int DEFAULT_CHANNELS_CHOSEN_SIZE = DEFAULT_CHANNELS_CHOSEN_MAP.get(CONFIG.getBaseDomain());

    public static final String DEFAULT_CHANNELS_COUNT = "5";

    public static final Map<String, String> DEFAULT_CHANNELS_TEXT = new HashMap<String, String>() {{
        put("3", getTranslation(TV_LESS3, CONFIG.getLang()));
        put("5", getTranslation(TV_LESS5, CONFIG.getLang()));
        put("7", getTranslation(TV_LESS7, CONFIG.getLang()));
        put("10", getTranslation(TV_LESS10, CONFIG.getLang()));
    }};

    public static AfishaTvBlock getTvBlock(BasePage basePage) {
        if (CONFIG.domainIs(RU) || CONFIG.domainIs(UA)) {
            return basePage.tvBlock;
        } else {
            return basePage.tvBlock;
        }
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
