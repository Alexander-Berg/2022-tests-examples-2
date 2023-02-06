package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ATBASAR;
import static ru.yandex.autotests.utils.morda.region.Region.BORISPOL;
import static ru.yandex.autotests.utils.morda.region.Region.ORSHA;
import static ru.yandex.autotests.utils.morda.region.Region.VYBORG;

/**
 * User: eoff
 * Date: 14.01.13
 */
public class EtrainsSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final List<String> NUMBER_TEXT = Arrays.asList("1", "2", "3", "4", "5", "6", "7", "8", "9", "10");
    public static final String FROM_TO_ARROW = " → ";
    public static final Matcher<String> OK_TEXT = equalTo(getTranslation("local", "etrains", "ok", CONFIG.getLang()));
    public static final Matcher<String> RESET_TEXT =
            equalTo(getTranslation("local", "etrains", "reset", CONFIG.getLang()));
    public static final Matcher<String> CLOSE_TEXT =
            equalTo(getTranslation("local", "etrains", "close", CONFIG.getLang()));

    public static class Route {
        public String from;
        public String to;
    }

    private static final Map<Domain, Region> REGIONS_MAP = new HashMap<Domain, Region>() {{
        put(Domain.RU, VYBORG);
        put(Domain.UA, BORISPOL);
        put(Domain.BY, ORSHA);
        put(Domain.KZ, ATBASAR);
    }};

    public static final Region REGION = REGIONS_MAP.get(CONFIG.getBaseDomain());
}
