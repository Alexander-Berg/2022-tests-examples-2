package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.loader.DataLoader;
import ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isIn;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_DOWN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_FORECAST;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_POINTS_MANY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_POINTS_ONE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_POINTS_SOME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_PROBKI;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_UP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_0;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_1;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_10;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_2;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_3;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_4;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_5;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_6;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_7;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_8;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_9;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_FORECAST_HOUR;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: leonsabr
 * Date: 23.03.12
 */
public class TrafficData {
    private static final Properties CONFIG = new Properties();

    static {
        DataLoader.populate(TrafficData.class, CONFIG.getBaseDomain());
    }

    public static final Matcher<HtmlElement> ARROW_MATCHER = allOf(anyOf(
            not(exists()),
            allOf(hasAttribute(HtmlAttribute.TITLE, equalTo(getTranslation(TRAFFIC_UP, CONFIG.getLang()))),
                    hasText("↑")
            ),
            allOf(hasAttribute(HtmlAttribute.TITLE, equalTo(getTranslation(TRAFFIC_DOWN, CONFIG.getLang()))),
                    hasText("↓")
            )
    ));

    private static final Map<Domain, String> TRAFFIC_HREF_MAP = new HashMap<Domain, String>() {{
        put(Domain.RU, "moscow_traffic");
        put(Domain.UA, "kiev_traffic");
        put(Domain.KZ, "astana_traffic");
        put(Domain.BY, "minsk_traffic");
    }};

    private static final Map<Domain, String> TRAFFIC_SMALL_REGION_MAP = new HashMap<Domain, String>() {{
        put(Domain.RU, "Волгоград");
        put(Domain.UA, "Львов");
        put(Domain.KZ, "Астана");
        put(Domain.BY, "Минск");
    }};

    private static final Map<Domain, String> TRAFFIC_HREF_SMALL_MAP = new HashMap<Domain, String>() {{
        put(Domain.RU, "traffic");
        put(Domain.UA, "traffic");
        put(Domain.KZ, "astana_traffic");
        put(Domain.BY, "minsk_traffic");
    }};

    public static final String SMALL_REGION = TRAFFIC_SMALL_REGION_MAP.get(CONFIG.getBaseDomain());

    private static final String TRAFFIC_LAYERS_PARAMETERS = "l=map%2Ctrf";

    private static String TRAFFIC_LINK_URL;
    static {
        if (CONFIG.getBaseDomain().equals(Domain.UA)) {
            TRAFFIC_LINK_URL = CONFIG.getProtocol() + "://maps.yandex.ua/";
        } else {
            TRAFFIC_LINK_URL = CONFIG.getProtocol() + "://maps.yandex.ru/";
        }
    }

    private static final Matcher<String> TRAFFIC_HREF = equalTo(TRAFFIC_LINK_URL +
            TRAFFIC_HREF_MAP.get(CONFIG.getBaseDomain()));
    private static final Matcher<String> TRAFFIC_URL = allOf(startsWith(TRAFFIC_LINK_URL),
            containsString(TRAFFIC_LAYERS_PARAMETERS));
    private static final Matcher<String> TRAFFIC_SMALL_HREF = equalTo(TRAFFIC_LINK_URL +
            TRAFFIC_HREF_SMALL_MAP.get(CONFIG.getBaseDomain()));

    public static final Matcher<String> POINTS_MATCHER = RegexMatcher.matches("([1-9]|10) .+");

    public static Matcher<String> getPointsMatcher(int points) {
        TextID pointsTextID = PointsText.getPointsText(points).getTextID();
        return equalTo(points + " " + getTranslation(pointsTextID, CONFIG.getLang()));
    }

    public static final Map<Integer, String> DESCRIPTIONS = new HashMap<Integer, String>() {{
        put(0, getTranslation(TRAFFIC_0, CONFIG.getLang()));
        put(1, getTranslation(TRAFFIC_1, CONFIG.getLang()));
        put(2, getTranslation(TRAFFIC_2, CONFIG.getLang()));
        put(3, getTranslation(TRAFFIC_3, CONFIG.getLang()));
        put(4, getTranslation(TRAFFIC_4, CONFIG.getLang()));
        put(5, getTranslation(TRAFFIC_5, CONFIG.getLang()));
        put(6, getTranslation(TRAFFIC_6, CONFIG.getLang()));
        put(7, getTranslation(TRAFFIC_7, CONFIG.getLang()));
        put(8, getTranslation(TRAFFIC_8, CONFIG.getLang()));
        put(9, getTranslation(TRAFFIC_9, CONFIG.getLang()));
        put(10, getTranslation(TRAFFIC_10, CONFIG.getLang()));
    }};

    public static final LinkInfo DESCRIPTION_LINK = new LinkInfo(
            isIn(DESCRIPTIONS.values()),
            TRAFFIC_URL,
            hasAttribute(HtmlAttribute.HREF, TRAFFIC_HREF)
    );

    public static final LinkInfo LIGHTS_LINK = new LinkInfo(
            equalTo(""),
            TRAFFIC_URL,
            hasAttribute(HtmlAttribute.HREF, TRAFFIC_HREF)
    );

    public static final LinkInfo TRAFFIC_LINK = new LinkInfo(
            equalTo(getTranslation(TRAFFIC_PROBKI, CONFIG.getLang())),
            TRAFFIC_URL,
            hasAttribute(HtmlAttribute.HREF, TRAFFIC_HREF)
    );

    public static final LinkInfo TRAFFIC_SMALL_LINK = new LinkInfo(
            equalTo(getTranslation(TRAFFIC_PROBKI, CONFIG.getLang())),
            TRAFFIC_URL,
            hasAttribute(HtmlAttribute.HREF, TRAFFIC_SMALL_HREF)
    );

    public static final LinkInfo LIGHTS_SMALL_LINK = new LinkInfo(
            equalTo(""),
            TRAFFIC_URL,
            hasAttribute(HtmlAttribute.HREF, TRAFFIC_SMALL_HREF)
    );

    public static final Matcher<String> FORECAST_TEXT =
            equalTo(getTranslation(TRAFFIC_FORECAST, CONFIG.getLang()));

    public static final Matcher<String> FORECAST_HOUR_TEXT =
            endsWith(getTranslation(TRAFFIC_FORECAST_HOUR, CONFIG.getLang()) + " ");

    protected static enum PointsText {
        ONE(0, 1, TRAFFIC_POINTS_ONE),
        SOME(2, 4, TRAFFIC_POINTS_SOME),
        MANY(5, 10, TRAFFIC_POINTS_MANY);

        private int from;
        private int to;
        private TextID text;

        private PointsText(int from, int to, TextID text) {
            this.from = from;
            this.to = to;
            this.text = text;
        }

        private boolean contains(int points) {
            return points >= from && points <= to;
        }

        public static PointsText getPointsText(int points) {
            for (PointsText pt : values()) {
                if (pt.contains(points)) {
                    return pt;
                }
            }
            return null;
        }

        public TextID getTextID() {
            return this.text;
        }
    }
}
