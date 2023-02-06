package ru.yandex.autotests.widgets.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher;
import ru.yandex.autotests.widgets.Properties;

/**
 * User: ivannik
 * Date: 01.08.13
 * Time: 20:50
 */
public class SidData {
    private static final Properties CONFIG = new Properties();

    public static final String CLCK_HOST = "clck.yandex.ru";
    public static final String MAIN_URL = CONFIG.getBaseURL().replaceFirst("widgets", "www");
    public static final Matcher<String> SID_MATCHER = new RegexMatcher(CONFIG.getProtocol() + "://" + CLCK_HOST +
            "/\\w+/[\\s\\S]+sid=[0-9]+[\\s\\S]+");
}
