package ru.yandex.autotests.mainmorda.data;

import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter;
import ru.yandex.autotests.mainmorda.utils.WidgetProperties;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.COLUMNSCOUNT;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.FAKE;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.HIDEPROMO;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.LAYOUTTYPE;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.PINNED;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.PROTOTYPE;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.PSETTINGS;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.WAUTH;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.YU;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.BELAYA_CERKOV;
import static ru.yandex.autotests.utils.morda.region.Region.BORISOV;
import static ru.yandex.autotests.utils.morda.region.Region.DNO;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.HABAROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.KARAGANDA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MAGADAN;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.PARIZH;
import static ru.yandex.autotests.utils.morda.region.Region.ROVNO;
import static ru.yandex.autotests.utils.morda.region.Region.VITEBSK;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;

/**
 * User: alex89
 * Date: 13.12.12
 */
public class WidgetsData {
    private static final Properties CONFIG = new Properties();

    /**
     * Виджеты
     */
    public static final WidgetInfo NEWS_RU = new WidgetInfo("Новости", "_topnews", true);
    public static final WidgetInfo NEWS = new WidgetInfo("Новости", "_topnews", true);

    public static final WidgetInfo TEASER = new WidgetInfo("Тизер", "_teaser", true);
    public static final WidgetInfo SERVICES = new WidgetInfo("Сервисы", "_services", true);
    public static final WidgetInfo WEATHER = new WidgetInfo("Погода", "_weather", true);
    public static final WidgetInfo TRAFFIC = new WidgetInfo("Пробки", "_traffic", true);
    public static final WidgetInfo STOCKS = new WidgetInfo("Котировки", "_stocks", true);
    public static final WidgetInfo TV = new WidgetInfo("Телепрограмма", "_tv", true);
    public static final WidgetInfo TV_AFISHA = new WidgetInfo("ТВ-Афиша", "_tvafisha", true);
    public static final WidgetInfo AFISHA = new WidgetInfo("Афиша", "_afisha", true);
    public static final WidgetInfo MAPS = new WidgetInfo("Карты", "_geo", true);
    public static final WidgetInfo ETRAINS = new WidgetInfo("Электрички", "_etrains");

    public static final WidgetInfo PHOTO = new WidgetInfo("Яндекс.Фотки", "498");
    public static final WidgetInfo METRO = new WidgetInfo("Яндекс.Метро", "10718");
    public static final WidgetInfo LENTARU = new WidgetInfo("Lenta.ru", "28");
    public static final WidgetInfo WAR_NEWS = new WidgetInfo("Военное обозрение", "60766");
    public static final WidgetInfo TIME = new WidgetInfo("Яндекс.Время", "66463");

    public static final WidgetInfo WEATHER_CUSTOM = new WidgetInfo("Погода", "_weather");

    /**
     * Набор дефолтных виджетов на новой морде.
     */
    private static final List<WidgetInfo> COMMON_DEFAULT_WIDGETS = Arrays.asList(
            NEWS, TEASER, SERVICES, WEATHER, MAPS, TIME);

    private static final List<WidgetInfo> DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC =
            new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                addAll(Arrays.asList(TV, AFISHA, TRAFFIC));
            }};

    private static final List<WidgetInfo> DEFAULT_WIDGETS_WITH_TV_AND_AFISHA =
            new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                addAll(Arrays.asList(TV, AFISHA));
            }};
    private static final List<WidgetInfo> DEFAULT_WIDGETS_WITH_TV =
            new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                addAll(Arrays.asList(TV));
            }};

    public static final Map<Domain, List<WidgetInfo>> DEFAULT_WIDGETS_FOR_DOMAINS
            = new HashMap<Domain, List<WidgetInfo>>() {{
        put(RU, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
        put(Domain.UA, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
        put(Domain.KZ, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA);
        put(Domain.BY, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
    }};

    public static final List<WidgetInfo> SHUFFLED_DEFAULT_WIDGETS;

    static {
        SHUFFLED_DEFAULT_WIDGETS = DEFAULT_WIDGETS_FOR_DOMAINS.get(CONFIG.getBaseDomain());
        Collections.shuffle(SHUFFLED_DEFAULT_WIDGETS);
    }

    /**
     * Набор настраиваемых дефолтных виджетов на новой морде.
     */
    public static final List<WidgetInfo> COMMON_EDITABLE_WIDGETS = new ArrayList<WidgetInfo>() {{
        addAll(Arrays.asList(NEWS, WEATHER, TV));
    }};

    public static final WidgetInfo RANDOM_EDITABLE_WIDGET;

    static {
        Collections.shuffle(COMMON_EDITABLE_WIDGETS);
        RANDOM_EDITABLE_WIDGET = COMMON_EDITABLE_WIDGETS.get(0);
    }

    /**
     * Определяет рубрику виджета по его имени.
     *
     * @param widget -- WidgetInfo виджет
     * @return рубрика виджета в каталоге
     */
    public static String getWidgetRubric(WidgetInfo widget) {
        return WIDGET_RUBRICS.get(widget);
    }

    private static final Map<WidgetInfo, String> WIDGET_RUBRICS = new HashMap<WidgetInfo, String>() {{
        put(WEATHER, "?company=yandex");
        put(WEATHER_CUSTOM, "?company=yandex");
        put(LENTARU, "rubric/news");
        put(PHOTO, "?company=yandex");
        put(MAPS, "?company=yandex");
        put(METRO, "?company=yandex");
        put(WAR_NEWS, "rubric/news");
    }};

    public static final List<WidgetInfo> WIDGETS_FOR_ADDITIONS_FROM_CATALOG = new ArrayList<WidgetInfo>() {{
        add(WEATHER_CUSTOM);
//        add(LENTARU);
    }};

    public static final List<WidgetInfo> WIDGETS_FOR_DELETE = new ArrayList<WidgetInfo>() {{
        add(LENTARU);
    }};

    public static final List<WidgetInfo> CUSTOM_WIDGETS = new ArrayList<WidgetInfo>() {{
        add(WAR_NEWS);
        add(LENTARU);
        add(METRO);
        add(PHOTO);
    }};

    public static final WidgetInfo RANDOM_CUSTOM_WIDGET;
    public static final WidgetInfo RANDOM_CUSTOM_WIDGET_2;

    static {
        Collections.shuffle(CUSTOM_WIDGETS);
        RANDOM_CUSTOM_WIDGET = CUSTOM_WIDGETS.get(0);
        RANDOM_CUSTOM_WIDGET_2 = CUSTOM_WIDGETS.get(1);
    }

    public static final Map<Region, List<WidgetInfo>> WIDGETS_SETS_FOR_REGIONS =
            new HashMap<Region, List<WidgetInfo>>() {{
                put(MOSCOW, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
                put(KIEV, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
                put(ASTANA, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA);
                put(MINSK, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
                put(DUBNA, new ArrayList<WidgetInfo>(DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC) {{
                    add(ETRAINS);
                }});

                put(HABAROVSK, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA_AND_TRAFFIC);
                put(VITEBSK, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA);
                put(ROVNO, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA);
                put(KARAGANDA, DEFAULT_WIDGETS_WITH_TV_AND_AFISHA);

                put(BORISOV, new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                    addAll(Arrays.asList(TV, AFISHA, ETRAINS));
                }});
                put(BELAYA_CERKOV, new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                    addAll(Arrays.asList(TV, AFISHA, ETRAINS));
                }});

                put(DNO, new ArrayList<WidgetInfo>(DEFAULT_WIDGETS_WITH_TV) {{
                    addAll(Arrays.asList(ETRAINS));
                }});
                put(MAGADAN, new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                    addAll(Arrays.asList(TV));
                }});
                put(PARIZH, COMMON_DEFAULT_WIDGETS);
                put(ISTANBUL, new ArrayList<WidgetInfo>(COMMON_DEFAULT_WIDGETS) {{
                    add(TRAFFIC);
                }});
            }};

    public static final int DEFAULT_NUMBER_OF_WIDGETS = WIDGETS_SETS_FOR_REGIONS
            .get(CONFIG.getBaseDomain().getCapital())
            .size();

    public static final Map<Domain, List<Region>> REGIONS_FOR_DDEFAULT_WIDGET_TESTING =
            new HashMap<Domain, List<Region>>() {{
                put(RU, new ArrayList<Region>() {{
                    add(DUBNA);
                    add(DNO);
                    add(MAGADAN);
                    add(PARIZH);
                    add(ISTANBUL);
                }});
                put(Domain.UA, new ArrayList<Region>() {{
                    add(KIEV);
                    add(BELAYA_CERKOV);
                    add(ROVNO);
                }});
                put(Domain.BY, new ArrayList<Region>() {{
                    add(MINSK);
                    add(VITEBSK);
                    add(BORISOV);
                }});
                put(Domain.KZ, new ArrayList<Region>() {{
                    add(ASTANA);
                    add(KARAGANDA);
                }});
            }};

    public static final List<WidgetInfo> SHUFFLED_REGION_WIDGETS = new ArrayList<WidgetInfo>(
            WIDGETS_SETS_FOR_REGIONS.get(CONFIG.getBaseDomain().getCapital()));
    public static final WidgetInfo RANDOM_REGION_WIDGET;

    static {
        Collections.shuffle(SHUFFLED_REGION_WIDGETS);
        RANDOM_REGION_WIDGET = SHUFFLED_REGION_WIDGETS.get(0);
    }

    public static class WidgetInfo {
        private String title;
        private String name;
        private boolean isDefault = false;

        //usrCh, idNum - нужны для координатных тестов;
        private int userCh = 0;
        private int idNum = 1;

        public WidgetInfo(String title, String name, boolean isDefault) {
            this.title = title;
            this.name = name;
            this.isDefault = isDefault;
            if (!isDefault) {
                idNum = 2;
            }
        }

        public WidgetInfo(String title, String name) {
            this(title, name, false);
        }

        public WidgetInfo(String name) {
            this("Виджет '" + name + "'", name, false);
        }


        public String getTitle() {
            return title;
        }

        public String getName() {
            return name;
        }

        public boolean isDefault() {
            return isDefault;
        }

        public int getUserCh() {
            return userCh;
        }

        public int getIdNum() {
            return idNum;
        }

        public void setIdNum(int idNum) {
            this.idNum = idNum;
        }

        public String getWidgetId() {
            return name + "-" + idNum;
        }

        @Override
        public String toString() {
            return title;
        }
    }

    public static Map<WidgetPatternParameter, String> FAKE_PARAMETERS = new HashMap<WidgetPatternParameter, String>() {{
        put(PROTOTYPE, "v12");
        put(WAUTH, "[0-9a-zA-Z\\._\\-]+");
        put(PSETTINGS, "");
        put(PINNED, "1");
        put(HIDEPROMO, "");
        put(COLUMNSCOUNT, "5");
        put(FAKE, "1");
        put(LAYOUTTYPE, "rows");
        put(YU, "[0-9a-zA-Z]+:[0-9]+");
    }};


    public static WidgetPattern FAKE_PATTERN = WidgetPattern.createPatternFromMap(
            FAKE_PARAMETERS,
            new HashMap<String, WidgetProperties>());
}