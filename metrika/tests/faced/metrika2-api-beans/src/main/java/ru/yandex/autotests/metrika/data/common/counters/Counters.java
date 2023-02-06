package ru.yandex.autotests.metrika.data.common.counters;

import java.util.Collections;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.*;

/**
 * Created by vananos on 15.08.16.
 */
public final class Counters {
    public static final Counter YANDEX_METRIKA = new Counter("Yandex.Metrika")
            .put(ID, 101500L)
            .put(GOAL_ID, 608122L);
    public static final Counter YANDEX_METRIKA_2_0 = new Counter("Yandex.Metrika 2.0")
            .put(ID, 24226447L)
            .put(GOAL_ID, 13592250L);
    public static final Counter YANDEX_METRIKA_FOR_APPS = new Counter("Yandex.Metrika For Apps")
            .put(ID, 22430419L);
    public static final Counter YANDEX_MAIN_PAGE = new Counter("Yandex Main Page")
            .put(ID, 722545L);
    public static final Counter YANDEX_SEARCH_BIG = new Counter("Yandex.Search (Big)")
            .put(ID, 731962L)
            .put(GOAL_ID, 2392195L);
    public static final Counter YANDEX_TURKEY = new Counter("Yandex.Turkey")
            .put(ID, 9927757L);//layer_id: 6
    public static final Counter YANDEX_DIRECT = new Counter("Yandex.Direct")
            .put(ID, 34L)
            .put(GOAL_ID, 22L);
    public static final Counter MVIDEO = new Counter("Сайт ATG")
            .put(ID, 25907066L);
    public static final Counter YANDEX_WEATHER = new Counter("Yandex.Weather")
            .put(ID, 345696L)
            .put(GOAL_ID, 26350194L);
    public static final Counter YANDEX_PHOTOS = new Counter("Yandex.Photos")
            .put(ID, 149814L)
            .put(GOAL_ID, 46382L);
    public static final Counter YANDEX_IMAGES = new Counter("images.yandex.ru")
            .put(ID, 722889L)
            .put(GOAL_ID, 1545418L);//layer_id: 30
    public static final Counter HUBHOST = new Counter("hubhost.ru")
            .put(ID, 21315463L);
    public static final Counter PARTNER_TEST_1 = new Counter("Partner test counter #1")
            .put(ID, 48088418L);
    public static final Counter PARTNER_TEST_2 = new Counter("Partner test counter #2")
            .put(ID, 49249054L);
    public static final Counter PARTNER_TEST_3 =  new Counter("Partner test counter #3")
            .put(ID, 52591000L);
    public static final Counter HOLODILNIKRU =  new Counter("holodilnik.ru")
            .put(ID, 42L)
            .put(CLIENT_IDS, of(15155L, 8431167L, 8794297L));
    public static final Counter MOS_RU = new Counter("mos.ru")
            .put(ID, 32628510L);
    public static final Counter STAT_MTRS = new Counter("stat.mtrs.yandex-team.ru")
            .put(ID, 36141705L);
    /**
     * Яндекс.Маркет - тяжелый счетчик. Не рекомендуется к используванию в тестах, где нет проверок возвращаемых данных.
     */
    public static final Counter YANDEX_MARKET = new Counter("Yandex.Market")
            .put(ID, 160656L)
            .put(GOAL_ID, 53225L)
            .put(U_LOGIN, "yndx-market-direct")
            .put(CLIENT_IDS, of(3126011L));//layer_id: 3
    public static final Counter YANDEX_NEWS = new Counter("news.yandex.ru")
            .put(ID, 722818L);//layer_id: 6
    public static final Counter LENTA_RU = new Counter("Lenta.Ru")
            .put(ID, 4308403L)
            .put(GOAL_ID, 1963180L)
            .put(U_LOGIN, "alextocquevile");//layer_id: 8
    public static final Counter DARIA_MAIL_YANDEX_RU = new Counter("daria.mail.yandex.ru")
            .put(ID, 1143050L)
            .put(GOAL_ID, 353023L)
            .put(CLIENT_IDS, of(1487230L, 1353047L, 1909536L, 2135991L, 7635832L))
            .put(U_LOGIN, "yuraklinok");//layer_id: 12
    public static final Counter SENDFLOWERS_RU = new Counter("sendflowers.ru")
            .put(ID, 101024L)
            .put(GOAL_ID, 3176503L)
            .put(CLIENT_IDS, of(3292374L, 8044831L, 3027651L))
            .put(U_LOGIN, "imedia-sendflowers");//layer_id: 1
    public static final Counter SHATURA_COM = new Counter("shatura.com")
            .put(ID, 501087L)
            .put(GOAL_ID, 388375L)
            .put(CLIENT_IDS, of(1486392L))
            .put(U_LOGIN, "webit-shatura");//layer_id: 5
    public static final Counter GENVIC_RU = new Counter("genvik.ru")
            .put(ID, 21714361L)
            .put(GOAL_ID, 2530441L)
            .put(CLIENT_IDS, of(561364L))
            .put(U_LOGIN, "galant-mitsubishi");//layer_id: 24
    public static final Counter WIKIMART_RU = new Counter("wikimart.ru")
            .put(ID, 1310521L)
            .put(GOAL_ID, 804865L)
            .put(U_LOGIN, "wikimartmain");//layer_id: 5
    public static final Counter YANDEX_BY_TESTER = new Counter("Yandex")
            .put(ID, 27179342L);
    public static final Counter DEMOCRAT_SPB = new Counter("democrat-spb")
            .put(ID, 176877L)
            .put(GOAL_ID, 225878L);
    public static final Counter METRIKA_DEMO = new Counter("yandex.ru")
            .put(ID, 29761725L);
    public static final Counter KVAZI_KAZINO = new Counter("www.kvazi-kazino.ru")
            .put(ID, 145336L)
            .put(GOAL_ID, 64011L)
            .put(EXPERIMENT_ID, 6L);
    public static final Counter DOCTORHEAD = new Counter("doctorhead.ru")
            .put(ID, 38019L);
    public static final Counter BIG_COUNTER = new Counter("AVITO.ru_Direct")
            .put(ID, 2237260L)
            .put(GOAL_ID, 1095613L)
            .put(U_LOGIN, "sm-avito");//// layer_id: 7
    public static final Counter ECOMMERCE_TEST = new Counter("ecommerce test data")
            .put(ID, 29096460L)
            .put(GOAL_ID, 11599636L);//layer_id: 34
    public static final Counter LAMODA_BY = new Counter("lamoda.by")
            .put(ID, 27405971L)
            .put(GOAL_ID, 6872423L)
            .put(U_LOGIN, "lamoda-by");//layer_id: 34
    public static final Counter LAMODA_RU = new Counter("lamoda.ru")
            .put(ID, 5503465L);
    public static final Counter GERASANT = new Counter("Gerasant")
            .put(ID, 1838839L)
            .put(GOAL_ID, 7976621L);
    public static final Counter DIRECT = new Counter("direct.yandex.ru")
            .put(ID, 34L)
            .put(GOAL_ID, 2918974L)
            .put(EXPERIMENT_ID, 5017L)
            .put(REFERENCE_ROW_ID, Collections.singletonList("10954"));
    public static final Counter NOTIK = new Counter("notik.ru")
            .put(ID, 37138L)
            .put(GOAL_ID, 2823892L);
    public static final Counter THERESPO_COM = new Counter("therespo.com")
            .put(ID, 31256393L);//layer_id: 33
    public static final Counter MIR_NEDVIZHIMOSTY = new Counter("mirndv.ru")
            .put(ID, 5214970L)
            .put(GOAL_ID, 5247422L);//layer_id: 11
    public static final Counter IKEA_VSEM = new Counter("ikea-vsem.ru")
            .put(ID, 11010319L)
            .put(GOAL_ID, 8686320L)
            .put(U_LOGIN, "ss333002");//layer_id: 10
    public static final Counter YANDEX_MAPS = new Counter("Yandex.Maps")
            .put(ID, 22227335L);//layer_id: 23
    public static final Counter JEELEX_MOSCOW = new Counter("jeelex.moscow")
            .put(ID, 28452966L)
            .put(GOAL_ID, 10748609L);//layer_id: 38
    public static final Counter PRISNILOS = new Counter("www.prisnilos.su")
            .put(ID, 11600101L);
    public static final Counter FEELEK = new Counter("feelek.livejournal.com")
            .put(ID, 907917L);
    public static final Counter PRODUCT = new Counter("www.productcenter.ru")
            .put(ID, 156713L);
    public static final Counter STRANALED = new Counter("stranaled.ru")
            .put(ID, 29974959L);
    public static final Counter FORBES = new Counter("forbes.com")
            .put(ID, 433635L);
    public static final Counter OPENTECH = new Counter ("www.opentech.ru")
            .put(ID,1104419L)
            .put(GOAL_ID, 31102120L);
    public static final Counter RBC_NEWS = new Counter("www.rbc.ru")
            .put(ID, 16443139L);
    public static final Counter DRESSTOP = new Counter("dress-top.ru")
            .put(ID, 4745287L)
            .put(U_LOGIN, "vladimir-sarckisow")
            .put(GOAL_ID, 17584775L)
            .put(EXPERIMENT_ID, 6L);

    public static final Counter EUROPA_PLUS = new Counter("europaplus.ru")
            .put(ID, 153605L);

    public static final Counter YANDEX_EATS_ON_MAPS = new Counter("yandex.ru/maps")
            .put(ID, 57358270L)
            .put(GOAL_ID, 66696235L);


    /**
     * Общий тестовый счетчик
     * Используется в фичернице как счетчик без данных по директу
     */
    public static final Counter TEST_COUNTER = new Counter("test counter")
            .put(ID, 42450794L);

    /**
     * счетчик без кампаний
     */
    public static final Counter TEST_NO_CAMPAIGN_COUNTER = new Counter("sctgukefgj.ru")
            .put(ID, 37774985L);

    /**
     * Тестовый счетчик с нестандартными лимитами: 210 целей, 40 фильтров, 40 операций
     * 29544240
     */
    public static final Counter TEST_COUNTER_LIMITS = new Counter("at-metrika-test-counter-1")
            .put(ID, 29544240L)
            .put(GOAL_ID, null);//layer_id: 36
    /**
     * Тестовый счетчик с нестандартным лимитом в 100 условий
     * 29544440
     */
    public static final Counter TEST_CONDITIONS_LIMIT = new Counter("at-metrika-test-counter-2")
            .put(ID, 29544440L);//layer_id: 34

    /**
     * Тестовый счетчик, представителем которого является пользователь PERMISSION_TEST_USER.
     * Используется в тестах на права доступа к отчетам.
     */
    public static final Counter TEST_DELEGATE_COUNTER = new Counter("test delegate counter")
            .put(ID, 36541300L); //no data
    /**
     * Тестовый счетчик, для которого выдан доступ на просмотр пользователю PERMISSION_TEST_USER.
     */
    public static final Counter TEST_VIEW_PERMISSION_COUNTER = new Counter("test view permission")
            .put(ID, 33686024L); //no data
    /**
     * Тестовый счетчик, для которого выдан доступ на редактирование пользователю PERMISSION_TEST_USER.
     */
    public static final Counter TEST_EDIT_PERMISSION_COUNTER = new Counter("test edit permission")
            .put(ID, 33537243L); //no data
    /**
     * Тестовый счетчик с данными по ecommerce.
     */
    public static final Counter TEST_ECOMMERCE = new Counter("Тест ecommerce")
            .put(ID, 29096460L);

    /**
     * Тестовый счетчик с данными по ecommerce в валюте для тестирования сортировки.
     */
    public static final Counter ECOMMERCE_AUTO = new Counter("Ecommerce test currency")
            .put(ID, 44648470L)
            .put(GOAL_ID, 31388959L);

    /**
     * Счетчик с представителем агенства в директе
     */
    public static final Counter ALI_EXPRESS = new Counter("aliexpress-ru2015")
            .put(ID, 29739640L)
            .put(CLIENT_IDS, of(8987970L, 2774582L, 9050511L, 10110175L));

    /**
     * Счетчик с новой версией вебвизора
     */
    public static final Counter AT_NEW_WEBVISOR = new Counter("at.yandex-team.ru")
            .put(ID, 41246029L);

    /**
     * Тестовый счетчик для офлайн загрузок.
     */
    public static final Counter TEST_UPLOADINGS = new Counter("Тестовый счетчик для офлайн загрузкок")
            .put(ID, 37690805L);

    /**
     * Тестовый счетчик для ym:s:sumParams
     */
    public static final Counter TEST_SUM_PARAMS = new Counter("Тестовый счётчик для периода выборки")
            .put(ID, 156713L)
            .put(GOAL_ID, 1627945L);

    public static final Counter B2B_SUM_PARAMS = new Counter("b2b sum Params")
            .put(ID, 292097L)
            .put(GOAL_ID, 704866L);

    /**
     * Тестовый счетчик для заказанных отчетов.
     */
    public static final Counter TEST_REPORT_ORDER = new Counter("Тестовый счетчик для заказанных отчетов")
            .put(ID, 46671738L);


    /**
     * Счетчик Жени Куршева. Используется для грида посетителей.
     */
    public static final Counter MELDA_RU = new Counter("melda.ru")
            .put(ID, 40181820L);

    /**
     * Тестовый счётчик для проверки фичи рекомендаций
     */
    public static final Counter RECOMMENDATION_AUTO = new Counter("Recommendation feature test")
            .put(ID, 50870540L);

    public static final Counter INOPTIKA_RU = new Counter("inoptika.ru")
            .put(ID, 142763L)
            .put(GOAL_ID, 42630L);
    public static final Counter VASHUROK_RU = new Counter("vashurok.ru")
            .put(ID, 38398360L)
            .put(GOAL_ID, 24702875L);

    /**
     * Счетчик с нулевой квотой. Используется для проверки корректности обработкки ошибки квоты
     */
    public static final Counter TEST_COUNTER_NO_QUOTA = new Counter("test counter no quota")
            .put(ID, 60802972L);

    /**
     * Тестовый счетчик для рекламных расходов.
     */
    public static final Counter TEST_EXPENSES = new Counter("metrika.yandex.ru")
            .put(ID, 59207371L)
            .put(U_LOGIN, "at-metrika")
            .put(GOAL_ID, 89084383L);
    /**
     * Тестовый счетчик wv2, который приспособили для тестирования CDP
     */
    public static final Counter TEST_CDP = new Counter("wv2_test")
            .put(ID, 42080444L)
            .put(GOAL_ID, 39226294L)
            .put(EXPERIMENT_ID, 136L)
            .put(REFERENCE_ROW_ID,  Collections.singletonList("325"));

    public static final Counter ROCKET_SALES = new Counter("RocketSales")
            .put(ID, 45403656L)
            .put(GOAL_ID, 167876494L);
}
