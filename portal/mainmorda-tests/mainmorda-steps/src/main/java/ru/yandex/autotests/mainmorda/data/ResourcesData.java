package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11.04.13
 */
public class ResourcesData {
    private static final Properties CONFIG = new Properties();

    public static final String MACHINE_NAME = ".yandex.net-->";
    public static final Matcher<String> MACHINE_NAME_MATCHER;

    static {
        if (CONFIG.getMordaEnv().isDev()) {
            MACHINE_NAME_MATCHER = matches("<!--(w-dev[\\d]*|v\\d+\\.wdevx)\\.yandex\\.net-->");
        } else if (CONFIG.getMordaEnv().isProd()) {
            MACHINE_NAME_MATCHER = matches("<!--(m|u|n|e|i|s|a|v)[\\d]+\\.wfront\\.yandex\\.net-->");
        } else {
            MACHINE_NAME_MATCHER = matches("<!--wrc-(m|u|n|e|i|s|a|v)[\\d]+\\.yandex\\.net-->");
        }
    }

    public static final Matcher<String> DEV_RESOURCES_MATCHER = not(anyOf(containsString("cloudkill"),
            containsString("graymantle"), containsString("wdevx")));

}
