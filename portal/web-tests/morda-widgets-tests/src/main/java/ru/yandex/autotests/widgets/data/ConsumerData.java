package ru.yandex.autotests.widgets.data;

import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.widgets.Properties;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.07.13
 */
public class ConsumerData {
    private static final Properties CONFIG = new Properties();

    private static final String CONSUMER = "qwerty";

    public static final String CONSUMER_URL = CONFIG.getBaseURL() + "/?consumer=" + CONSUMER;

    public static final LinkInfo CONSUMER_LINK = new LinkInfo(
            not(""),
            containsString("consumer=" + CONSUMER)
    );
}
