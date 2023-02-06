package ru.yandex.autotests.mainmorda.data;


import org.hamcrest.Matcher;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.allOf;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.isEmptyString;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.AFISHA;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.MAPS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.NEWS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.SERVICES;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.STOCKS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TEASER;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TRAFFIC;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TV;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TV_AFISHA;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WEATHER;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;

/**
 * User: leonsabr
 * Date: 26.08.11
 */
public class CoordinatesData {
    ////////////////////////////////Паттерны
    public static final String YU = "&yu=";
    public static final String WIDGET = "&widget=";
    public static final String COORD = "&coord=";
    public static final String DIVISOR = "%3A";
    public static final String USER_CH = "&usrCh=";
    public static final String REMOVED = "&removed=";

    private static final String SYMBOLS = "[&%0-9a-zA-Z\\._\\-=,]+";

    private static final String WAUTH_PATTERN = "prototype=v12&wauth=[0-9a-zA-Z\\._\\-]+";
    private static final String SETTINGS_PATTERN =
            "(&psettings=%26pinned%3D1%26hidePromo%3D0%26columnsCount%3D5%26layoutType%3Drows|" +
                    "&psettings=%26pinned%3D1%26layoutType%3Drows%26columnsCount%3D5%26hidePromo%3D0)";
    private static final String YU_PATTERN = YU + "([0-9a-zA-Z]+)";
    private static final String WCOORD_PATTERN_PART =
            "&widget=([_A-Za-z0-9]+)-([0-9]+)&coord=[1-5]{1}%3A[\\d]+&usrCh=[0-3]{1}";

    private static final String WCOORD_PATTERN =
            "((" + WCOORD_PATTERN_PART + ")+)";
    private static final String REMOVED_PATTERN = "(" + REMOVED + "([_A-Za-z0-9]+-[0-9]+)?" +
            "(,[_A-Za-z0-9]+-[0-9]+){0,})";

    public static final String MAIN_FORMAT_PATTERN = WAUTH_PATTERN +
            WCOORD_PATTERN + REMOVED_PATTERN +
            SETTINGS_PATTERN + YU_PATTERN;

    public static final String ONLY_WIDGETS_PATTERN =
            WAUTH_PATTERN + WCOORD_PATTERN + "&" + SYMBOLS;

    public static final String ONLY_REMOVED_PATTERN =
            SYMBOLS + REMOVED_PATTERN + "&" + SYMBOLS;

    ///////////////////////////////////////////////////////////////////////
    private static final String FAKE_SETTINGS_PATTERN =
            "(&psettings=%26pinned%3D1%26hidePromo%3D0%26columnsCount%3D5%26fake%3D1%26layoutType%3Drows|" +
                    "&psettings=%26pinned%3D1%26hidePromo%3D0%26columnsCount%3D5%26layoutType%3Drows%26fake%3D1|" +
                    "&psettings=%26pinned%3D1%26layoutType%3Drows%26columnsCount%3D5%26fake%3D1%26hidePromo%3D0)";
    public static final String MAIN_FAKE_PATTERN = WAUTH_PATTERN +
            FAKE_SETTINGS_PATTERN + YU_PATTERN;
    public static final String FAKE_PARAM = "fake%3D1";
    public static final String SKIN_PARAM = "%26defskin%3D";
    /////////////////////////////////////Автообновление
    // Auto update parameters (rebind)
    public static final String STOCKS_AUTO_UPDATE_MIN_PARAM = "120";
    public static final String STOCKS_AUTO_UPDATE_MAX_PARAM = "800";

    public static final Matcher<String> NO_AUTO_UPDATE = isEmptyString();
    public static final Matcher<String> DEFAULT_AUTO_UPDATE_INTERVAL = equalTo("300");
    public static final Matcher<String> STOCKS_AUTO_UPDATE_INTERVAL = allOf(
            greaterThanOrEqualTo(STOCKS_AUTO_UPDATE_MIN_PARAM),
            lessThanOrEqualTo(STOCKS_AUTO_UPDATE_MAX_PARAM)
    );

    public static final Map<WidgetInfo, Matcher<String>> AUTO_UPDATE_WIDGETS_COMMON =
            new HashMap<WidgetInfo, Matcher<String>>() {{
                put(NEWS, DEFAULT_AUTO_UPDATE_INTERVAL);
                put(WEATHER, DEFAULT_AUTO_UPDATE_INTERVAL);
                put(TEASER, NO_AUTO_UPDATE);
                put(SERVICES, NO_AUTO_UPDATE);
                put(MAPS, NO_AUTO_UPDATE);
                put(STOCKS, STOCKS_AUTO_UPDATE_INTERVAL);
                // put("etrains", "");
                // put("stocks","600");
            }};

    private static final Map<WidgetInfo, Matcher<String>> AUTO_UPDATE_WIDGETS_TV_AND_AFISHA_AND_TRAFFIC =
            new HashMap<WidgetInfo, Matcher<String>>(AUTO_UPDATE_WIDGETS_COMMON) {{
                put(TV, DEFAULT_AUTO_UPDATE_INTERVAL);
                put(AFISHA, NO_AUTO_UPDATE);
                put(TRAFFIC, DEFAULT_AUTO_UPDATE_INTERVAL);
            }};

    private static final Map<WidgetInfo, Matcher<String>> AUTO_UPDATE_WIDGETS_TV_AND_AFISHA =
            new HashMap<WidgetInfo, Matcher<String>>(AUTO_UPDATE_WIDGETS_COMMON) {{
                put(TV, DEFAULT_AUTO_UPDATE_INTERVAL);
                put(AFISHA, NO_AUTO_UPDATE);
            }};

    public static final Map<Domain, Map<WidgetInfo, Matcher<String>>> AUTO_UPDATE_WIDGETS_FOR_DOMAINS
            = new HashMap<Domain, Map<WidgetInfo, Matcher<String>>>() {{
        put(Domain.RU, AUTO_UPDATE_WIDGETS_TV_AND_AFISHA_AND_TRAFFIC);
        put(Domain.UA, AUTO_UPDATE_WIDGETS_TV_AND_AFISHA_AND_TRAFFIC);
        put(Domain.KZ, AUTO_UPDATE_WIDGETS_TV_AND_AFISHA);
        put(Domain.BY, AUTO_UPDATE_WIDGETS_TV_AND_AFISHA_AND_TRAFFIC);
    }};

    public static final List<Domain> MDA_DOMAINS = Arrays.asList(Domain.UA, Domain.KZ, Domain.BY);

    public static final List<Domain> KUBR_DOMAINS = new ArrayList<Domain>(MDA_DOMAINS) {{
        add(Domain.RU);
    }};
}
