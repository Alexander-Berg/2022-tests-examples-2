package ru.yandex.autotests.mainmorda.data;

import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.utils.PatternInfo;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.AFISHA;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.LENTARU;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.MAPS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.METRO;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.NEWS_RU;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.SERVICES;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TEASER;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TRAFFIC;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TV;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_ANTIMATTER;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_BELT;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_IPV6;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_MOSCOW;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_NIGHT;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_WEATHER;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_WT_YA13;

/**
 * User: alex89
 * Date: 28.01.13
 */
public class PatternsData {
    private static final Properties CONFIG = new Properties();


    public static final List<PatternInfo> OLD_PATTERNS_LIST =
            new ArrayList<PatternInfo>() {{
                add(new PatternInfo(NEW_WT_YA13, "ya13",
                        new ArrayList<WidgetInfo>(Arrays.asList(TEASER, MAPS, NEWS_RU, WidgetsData.WEATHER, TRAFFIC))));
                add(new PatternInfo(NEW_WT_WEATHER, "weather",
                        new ArrayList<WidgetInfo>(Arrays.asList(TEASER, MAPS, NEWS_RU, WidgetsData.WEATHER, TRAFFIC))));
                add(new PatternInfo(NEW_WT_ANTIMATTER, "antimatter",
                        new ArrayList<WidgetInfo>(Arrays.asList(NEWS_RU, TEASER, MAPS, TRAFFIC,
                                WidgetsData.WEATHER, WidgetsData.WEATHER, WidgetsData.WEATHER))));
                add(new PatternInfo(NEW_WT_BELT, "belt",
                        new ArrayList<WidgetInfo>()));
                add(new PatternInfo(NEW_WT_NIGHT, "night",
                        new ArrayList<WidgetInfo>(Arrays.asList(NEWS_RU, TEASER, MAPS, WidgetsData.WEATHER, TRAFFIC, SERVICES,
                                TV, AFISHA, METRO, LENTARU))));
                add(new PatternInfo(NEW_WT_IPV6, "ipv6",
                        new ArrayList<WidgetInfo>(Arrays.asList(NEWS_RU, TEASER, MAPS, WidgetsData.WEATHER, TRAFFIC, SERVICES,
                                TV, AFISHA, LENTARU))));
                add(new PatternInfo(NEW_WT_MOSCOW, "moscow",
                        new ArrayList<WidgetInfo>(Arrays.asList(NEWS_RU, MAPS, WidgetsData.WEATHER, TRAFFIC, SERVICES,
                                TV, AFISHA))));
            }};

    public static final String RU_URL =
            CONFIG.getBaseURL().replace(CONFIG.getBaseDomain().toString(), Domain.RU.toString());

}