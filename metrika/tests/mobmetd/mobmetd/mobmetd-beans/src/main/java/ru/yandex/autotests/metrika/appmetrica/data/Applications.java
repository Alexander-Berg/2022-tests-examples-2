package ru.yandex.autotests.metrika.appmetrica.data;

import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.LAYER;

/**
 * Created by konkov on 04.05.2016.
 * <p>
 * Разбито по слоям mtmoblog, упорядочено по аудитории (приблизительно)
 */
public class Applications {

    public static final Application YANDEX_TAXI = new Application("Yandex.Taxi (Production)")
            .put(ID, 3L)
            .put(LAYER, 1);

    // External app
    public static final Application MTS_SERVICE = new Application("МТС Сервис")
            .put(ID, 97600L)
            .put(LAYER, 1);

    public static final Application YANDEX_MAPS = new Application("Yandex.Maps (Production)")
            .put(ID, 4L)
            .put(LAYER, 1);

    public static final Application AUTO_RU = new Application("Auto.ru")
            .put(ID, 28554L)
            .put(LAYER, 1);

    public static final Application YANDEX_METRO = new Application("Yandex.Metro (Production)")
            .put(ID, 2L)
            .put(LAYER, 1);

    public static final Application YANDEX_DISK = new Application("Yandex.Disk (Production)")
            .put(ID, 18895L)
            .put(LAYER, 1);

    public static final Application KINOPOISK = new Application("КиноПоиск (Production)")
            .put(ID, 10267L)
            .put(LAYER, 1);

    public static final Application EDADEAL = new Application("Едадил PROD")
            .put(ID, 41734L)
            .put(LAYER, 1);

    public static final Application SEARCH_PLUGIN = new Application("Yandex.Searchplugin (Production) Android")
            .put(ID, 10321L)
            .put(LAYER, 1);

    public static final Application YANDEX_MONEY = new Application("Яндекс.Деньги Android")
            .put(ID, 130830L)
            .put(LAYER, 1);

    public static final Application YANDEX_REALTY = new Application("Yandex.Realty")
            .put(ID, 62063L)
            .put(LAYER, 1);

    public static final Application YANDEX_MARKET = new Application("Yandex.Market Android (Production)")
            .put(ID, 23107L)
            .put(LAYER, 1);

    public static final Application YANDEX_TOLOKA = new Application("Яндекс.Толока")
            .put(ID, 139535L)
            .put(LAYER, 1);

    public static final Application ANDROID_APP = new Application("Android App")
            .put(ID, 85021L)
            .put(LAYER, 1);

    public static final Application YANDEX_KEYBOARD = new Application("Yandex Keyboard (iOS)")
            .put(ID, 38000L)
            .put(LAYER, 1);

    public static final Application YANDEX_MUSIC = new Application("Яндекс.Музыка")
            .put(ID, 25378L)
            .put(LAYER, 1);

    public static final Application YANDEX_TRANSLATE_FOR_ANDROID = new Application("Yandex.Translate for Android (Production)")
            .put(ID, 20740L)
            .put(LAYER, 1);

    public static final Application YANDEX_SEARCH_FOR_WP_TESTING = new Application("Yandex.Search for WP (Testing)")
            .put(ID, 5745L)
            .put(LAYER, 1);

    public static final Application ANDROID_BROWSER = new Application("Yandex.Browser Android (Production)")
            .put(ID, 106400L)
            .put(LAYER, 1);

    public static final Application METRICA_PUSH_LIBRARY = new Application("MetricaPushLibrary")
            .put(ID, 218300L)
            .put(LAYER, 2);

    public static final Application LITE_BROWSER = new Application("LiteBrowser")
            .put(ID, 619001L)
            .put(LAYER, 2);

    public static final Application ZEN_APP = new Application("Zen App")
            .put(ID, 728964L)
            .put(LAYER, 2);

    public static final Application DRIVE = new Application("Drive")
            .put(ID, 917433L)
            .put(LAYER, 2);

    public static final Application YANDEX_BROWSER_ZTE = new Application("Yandex Browser ZTE")
            .put(ID, 178830L)
            .put(LAYER, 2);

    public static final Application APPMETRICA_PROD = new Application("AppMetricaApp (Prod)")
            .put(ID, 806976L)
            .put(LAYER, 2);

    // Используется для выдачи грантов. Использование в тех же целях ещё где-то приведёт к гонкам
    public static final Application METRIKA_TEST = new Application("Метрика (Test)")
            .put(ID, 284530L)
            .put(LAYER, 2);

    public static final Application ZAPRAVKI = new Application("Яндекс.Заправки")
            .put(ID, 937662L)
            .put(LAYER, 2);

    public static final Application PUSH_SAMPLE = new Application("AppMetrica Push Sample")
            .put(ID, 185600L)
            .put(LAYER, 2);

    public static final Application YANDEX_YANG = new Application("Яндекс.Янг")
            .put(ID, 681895L)
            .put(LAYER, 2);

    public static final Application SAMPLE = new Application("Yandex Libraries Sample (Test)")
            .put(ID, 28620L)
            .put(LAYER, 3);

    public static final Application BERU = new Application("Беру / beru")
            .put(ID, 1389598L)
            .put(LAYER, 3);

    public static final Application ZEN_APP_IOS = new Application("Zen App iOS")
            .put(ID, 1357762L)
            .put(LAYER, 3);

    public static final Application YANDEX_DISK_DESKTOP = new Application("Яндекс.Диск Десктоп")
            .put(ID, 2151871L)
            .put(LAYER, 4);

    public static final Application YANDEX_DISK_BETA = new Application("Yandex.Disk (Beta)")
            .put(ID, 2173642L)
            .put(LAYER, 4);

    public static final Application UBER_RUSSIA = new Application("Uber Russia")
            .put(ID, 2171938L)
            .put(LAYER, 4);

    // External app
    public static final Application LIFEHACKER = new Application("Лайфхакер")
            .put(ID, 2246839L)
            .put(LAYER, 4);

    // External app
    public static final Application PRAVOSLAVNYY_MIR = new Application("Православный мир")
            .put(ID, 2517649L)
            .put(LAYER, 4);

    // External app
    public static final Application ONE_NEWS = new Application("1news")
            .put(ID, 2459208L)
            .put(LAYER, 4);

    // External app
    public static final Application APP_WITH_EXPIRED_IOS_CERT = new Application("APP_WITH_EXPIRED_IOS_CERT")
            .put(ID, 1949596L)
            .put(LAYER, 4);

    // External app
    public static final Application IGOOODS = new Application("igooods")
            .put(ID, 2342908L)
            .put(LAYER, 4);

    // External app
    public static final Application EAPTEKA = new Application("eApteka")
            .put(ID, 2550202L)
            .put(LAYER, 4);

    // External app
    public static final Application YANDEX_BROWSER_IOS = new Application("Мобильное приложение «Яндекс» (Production) iOS")
            .put(ID, 42989L)
            .put(LAYER, 1);

    // External test app for skad
    public static final Application SKAD_TEST_APP = new Application("Приложение для тестов SKAd доступов")
            .put(ID, 4012018L)
            .put(LAYER, 4);

    // External app
    public static final Application BURGER_KING = new Application("Burger King mobile application")
            .put(ID, 784890L)
            .put(LAYER, 1);

    // External app
    public static final Application MUNDUS = new Application("Mundus")
            .put(ID, 3776032L)
            .put(LAYER, 1);

    // External app for post-api
    public static final Application MOS_RU = new Application("Mos.ru")
            .put(ID, 994791L)
            .put(LAYER, 1);

    // External app for Cohort Analysis v2
    public static final Application PLANETAZDOROVO = new Application("planetazdorovo")
            .put(ID, 1714523L)
            .put(LAYER, 1);

    public static final Map<Long, Application> appById = new HashMap<>();

    static {
        for (Field f : Applications.class.getDeclaredFields()) {
            try {
                if (f.getType() == Application.class) {
                    Application app = (Application) f.get(null);
                    appById.put(app.get(ID), app);
                }
            } catch (IllegalAccessException ignored) {
            }
        }
    }

}
