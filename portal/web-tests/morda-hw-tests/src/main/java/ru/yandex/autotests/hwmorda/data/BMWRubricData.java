package ru.yandex.autotests.hwmorda.data;

import ru.yandex.autotests.hwmorda.Properties;

/**
 * Created with IntelliJ IDEA.
 * User: lipka
 * Date: 29.03.13
 * Time: 15:58
 * To change this template use File | Settings | File Templates.
 */
public class BMWRubricData {
    private static final Properties CONFIG = new Properties();

    public static final String WEATHER_URL = CONFIG.getBMWBaseUrl() + "/weather";
    public static final String TOPNEWS_URL = CONFIG.getBMWBaseUrl() + "/topnews";
    public static final String TUNE_URL = CONFIG.getBMWBaseUrl() + "/tune";
}
