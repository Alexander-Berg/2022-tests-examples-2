package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TRAFFIC_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_FORECAST;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_FORECAST_HOUR;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class TrafficData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> TITLE = equalTo(getTranslation(TRAFFIC_TITLE, CONFIG.getLang()));

    public static final Matcher<String> FORECAST_TITLE = equalTo(getTranslation(TRAFFIC_FORECAST, CONFIG.getLang()));

    public static final LinkInfo TRAFFIC_LINK = new LinkInfo(
            not(""),
            startsWith("intent://maps.yandex.ru/"),
            hasAttribute(HREF, startsWith(CONFIG.getProtocol() + "://maps.yandex.ru/moscow_traffic"))
    );
    public static final Matcher<String> POINTS_MATCHER = matches("([1-9]|10)");

    public static Matcher<HtmlElement> getBallMatcher(HtmlElement ball) {
        return hasAttribute(CLASS, containsString("b-traffic-forecast__value_ball_" + ball.getText()));
    }

    public static final Matcher<String> FORECAST_HOUR_TEXT =
            endsWith(getTranslation(TRAFFIC_FORECAST_HOUR, CONFIG.getLang()) + " ");
}
