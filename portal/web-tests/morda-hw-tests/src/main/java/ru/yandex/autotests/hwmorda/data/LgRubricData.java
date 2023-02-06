package ru.yandex.autotests.hwmorda.data;

import ru.yandex.autotests.hwmorda.Properties;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


/**
 * Created with IntelliJ IDEA.
 * User: lipka
 * Date: 28.03.13
 * Time: 9:53
 * To change this template use File | Settings | File Templates.
 */
public class LgRubricData {
    private static final Properties CONFIG = new Properties();

    public static final String WEATHER_URL = CONFIG.getLgBaseUrl() + "/weather";
    public static final String TOPNEWS_URL = CONFIG.getLgBaseUrl() + "/topnews";
    public static final String STOCKS_URL = CONFIG.getLgBaseUrl() + "/stocks";
    public static final String TV_URL = CONFIG.getLgBaseUrl() + "/tv";
    public static final String FOTKI_URL = CONFIG.getLgBaseUrl() + "/fotki";
    public static final String TRAFFIC_URL = CONFIG.getLgBaseUrl() + "/traffic";

    public static final List<String> ALL_RUBRICS = new ArrayList<String>(Arrays.asList(WEATHER_URL, TOPNEWS_URL,
            STOCKS_URL, TV_URL, FOTKI_URL, TRAFFIC_URL));

    public static final String WEATHER_TITLE = "Погода\n";
    public static final String STOCKS_TITLE = "Котировки\n";
    public static final String NEWS_TITLE = "Новости\n";
    public static final String TRAFFIC_TITLE = "Пробки\n ";
}
