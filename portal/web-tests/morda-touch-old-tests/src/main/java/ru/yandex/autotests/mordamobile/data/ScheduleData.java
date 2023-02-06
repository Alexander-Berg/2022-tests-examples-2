package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.equalToIgnoringCase;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.SCHEDULE_BUS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.SCHEDULE_ETRAIN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.SCHEDULE_PLANE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.SCHEDULE_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.SCHEDULE_TRAIN;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class ScheduleData {
    private static final Properties CONFIG = new Properties();

    private static final String RASP_HREF = "https://t.rasp.yandex.ru/";
    private static final String RASP_URL = "https://t.rasp.yandex.ru/";

    public static final LinkInfo TITLE_LINK = new LinkInfo(
            equalTo(getTranslation(SCHEDULE_TITLE, CONFIG.getLang())),
            equalTo(RASP_URL)
    );

    private static final ScheduleInfo PLAIN = new ScheduleInfo(
            SCHEDULE_PLANE,
            equalTo(RASP_HREF + "stations/plane/"),
            equalTo(RASP_URL + "stations/plane/"),
            "b-rasp__icon_category_aero"
    );
    private static final ScheduleInfo TRAIN = new ScheduleInfo(
            SCHEDULE_TRAIN,
            equalTo(RASP_HREF + "stations/train/"),
            equalTo(RASP_URL + "stations/train/"),
            "b-rasp__icon_category_train"
    );
    private static final ScheduleInfo BUS = new ScheduleInfo(
            SCHEDULE_BUS,
            equalTo(RASP_HREF + "stations/bus/"),
            equalTo(RASP_URL + "stations/bus/"),
            "b-rasp__icon_category_bus"
    );
    private static final ScheduleInfo ETRAIN = new ScheduleInfo(
            SCHEDULE_ETRAIN,
            equalTo(RASP_HREF + "suburban-directions/"),
            equalTo(RASP_URL + "suburban-directions/"),
            "b-rasp__icon_category_el"
    );

    public static final List<ScheduleInfo> SCHEDULE_ICONS = Arrays.asList(
            PLAIN, TRAIN, BUS, ETRAIN
    );

    public static class ScheduleInfo {
        private TextID text;
        private Matcher<String> href;
        private Matcher<String> url;
        private String icon;

        public ScheduleInfo(TextID text, Matcher<String> href, String icon) {
            this(text, href, href, icon);
        }

        public ScheduleInfo(TextID text, Matcher<String> href, Matcher<String> url, String icon) {
            this.text = text;
            this.href = href;
            this.url = url;
            this.icon = icon;
        }

        public Matcher<String> getText(Language lang) {
            return equalToIgnoringCase(getTranslation(text, lang));
        }

        public LinkInfo getLing(Language lang) {
            return new LinkInfo(
                    equalToIgnoringCase(getTranslation(text, lang)),
                    url,
                    hasAttribute(HREF, href)
            );
        }

        public Matcher<HtmlElement> getIconMatcher() {
            return hasAttribute(CLASS, containsString(icon));
        }

        @Override
        public String toString() {
            return getTranslation(text, RU);
        }
    }
}
