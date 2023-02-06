package ru.yandex.autotests.widgets.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.utils.morda.region.Region;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.utils.morda.region.Region.AHTYRKA;
import static ru.yandex.autotests.utils.morda.region.Region.AKTOBE;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.BORISOV;
import static ru.yandex.autotests.utils.morda.region.Region.BREST;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.FEODOSIYA;
import static ru.yandex.autotests.utils.morda.region.Region.GOMELSKAYA_OBLAST;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.ISHIM;
import static ru.yandex.autotests.utils.morda.region.Region.KARAGANDA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEVSKAYA_OBLAST;
import static ru.yandex.autotests.utils.morda.region.Region.KOSTANAY;
import static ru.yandex.autotests.utils.morda.region.Region.KRIVOY_ROG;
import static ru.yandex.autotests.utils.morda.region.Region.LONDON;
import static ru.yandex.autotests.utils.morda.region.Region.LVOV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOGILYOV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.MYUNHEN;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.NYU_YORK;
import static ru.yandex.autotests.utils.morda.region.Region.OMSK;
import static ru.yandex.autotests.utils.morda.region.Region.PAVLODAR;
import static ru.yandex.autotests.utils.morda.region.Region.SPB;
import static ru.yandex.autotests.utils.morda.region.Region.SSHA;
import static ru.yandex.autotests.utils.morda.region.Region.TOKIO;
import static ru.yandex.autotests.utils.morda.region.Region.VITEBSK;
import static ru.yandex.autotests.utils.morda.region.Region.VYBORG;
import static ru.yandex.autotests.utils.morda.region.Region.YUZHNO_KAZAHSTANSKAYA_OBLAST;

/**
 * User: leonsabr
 * Date: 08.11.11
 */
public class RegionsData {
    private static final RegionCategories MOSCOW_CATEGORIES = new RegionCategories(MOSCOW, new ArrayList<String>());
    private static final RegionCategories SPB_CATEGORIES = new RegionCategories(SPB, "2", "225");
    private static final RegionCategories VYBORG_CATEGORIES = new RegionCategories(VYBORG, "969", "10174", "225");
    private static final RegionCategories ISHIM_CATEGORIES = new RegionCategories(ISHIM, "11173", "11176", "225");
    private static final RegionCategories FEODOSIYA_CATEGORIES = new RegionCategories(FEODOSIYA, "11469", "977", "225");
    private static final RegionCategories KIEV_CATEGORIES = new RegionCategories(KIEV, "143", "187");
    private static final RegionCategories KRIVOI_ROG_CATEGORIES =
            new RegionCategories(KRIVOY_ROG, "10347", "20537", "187");
    private static final RegionCategories AHTYRKA_CATEGORIES = new RegionCategories(AHTYRKA, "20552", "187");
    private static final RegionCategories MINSK_CATEGORIES = new RegionCategories(MINSK, "149");
    private static final RegionCategories MOGILYOV_CATEGORIES = new RegionCategories(MOGILYOV, "158", "149");
    private static final RegionCategories VITEBSK_CATEGORIES = new RegionCategories(VITEBSK, "154", "149");
    private static final RegionCategories BORISOV_CATEGORIES = new RegionCategories(BORISOV, "21193", "29630", "149");
    private static final RegionCategories ALMATY_CATEGORIES = new RegionCategories(ALMATY, "162", "159", "29406");
    private static final RegionCategories AKTOBE_CATEGORIES = new RegionCategories(AKTOBE, "159", "20273");
    private static final RegionCategories KARAGANDA_CATEGORIES = new RegionCategories(KARAGANDA, "159", "164");
    private static final RegionCategories KOSTANAY_CATEGORIES = new RegionCategories(KOSTANAY, "10295", "159");

    public static final List<RegionCategories> REGION_CATEGORIES = Arrays.asList(
            MOSCOW_CATEGORIES, SPB_CATEGORIES, VYBORG_CATEGORIES, ISHIM_CATEGORIES, FEODOSIYA_CATEGORIES,
            KIEV_CATEGORIES, KRIVOI_ROG_CATEGORIES, AHTYRKA_CATEGORIES, MINSK_CATEGORIES, MOGILYOV_CATEGORIES,
            VITEBSK_CATEGORIES, BORISOV_CATEGORIES, ALMATY_CATEGORIES, AKTOBE_CATEGORIES
    );

    private static final WidgetRegions DUBNA_REGIONS = new WidgetRegions(DUBNA, new ArrayList<String>());
    private static final WidgetRegions SPB_REGIONS = new WidgetRegions(SPB, "10174");
    private static final WidgetRegions NOVOSIBIRSK_REGIONS = new WidgetRegions(NOVOSIBIRSK, "11316");
    private static final WidgetRegions EKB_REGIONS = new WidgetRegions(EKATERINBURG, "11162");
    private static final WidgetRegions OMSK_REGIONS = new WidgetRegions(OMSK, "11318");
    private static final WidgetRegions VIBORG_REGIONS = new WidgetRegions(VYBORG, new ArrayList<String>());

    private static final WidgetRegions KIEV_REGIONS = new WidgetRegions(KIEV, "20544");
    private static final WidgetRegions KIEVSKAYA_OBLAST_REGIONS = new WidgetRegions(KIEVSKAYA_OBLAST, "20544");
    private static final WidgetRegions DONECK_REGIONS = new WidgetRegions(KIEVSKAYA_OBLAST, "20536");
    private static final WidgetRegions HARKOV_REGIONS = new WidgetRegions(HARKOV, "20538");
    private static final WidgetRegions LVOV_REGIONS = new WidgetRegions(LVOV, "20529");
    private static final WidgetRegions FEODOSIYA_REGIONS = new WidgetRegions(FEODOSIYA, new ArrayList<String>());

    private static final WidgetRegions MINSK_REGIONS = new WidgetRegions(MINSK, "29630");
    private static final WidgetRegions VITEBSK_REGIONS = new WidgetRegions(VITEBSK, "29633");
    private static final WidgetRegions MOGILEV_REGIONS = new WidgetRegions(MOGILYOV, "29629");
    private static final WidgetRegions GOMELSKAYA_OBLAST_REGIONS =
            new WidgetRegions(GOMELSKAYA_OBLAST, new ArrayList<String>());
    private static final WidgetRegions BREST_REGIONS = new WidgetRegions(BREST, "29632");
    private static final WidgetRegions BORISOV_REGIONS = new WidgetRegions(BORISOV, new ArrayList<String>());

    private static final WidgetRegions ASTANA_REGIONS = new WidgetRegions(ASTANA, "29403");
    private static final WidgetRegions ALMATY_REGIONS = new WidgetRegions(ALMATY, "29406");
    private static final WidgetRegions AKTOBE_REGIONS = new WidgetRegions(AKTOBE, "29404");
    private static final WidgetRegions KARAGANDA_REGIONS = new WidgetRegions(KARAGANDA, "29411", "159");
    private static final WidgetRegions PAVLODAR_REGIONS = new WidgetRegions(PAVLODAR, "190", "159", "29415");
    private static final WidgetRegions YUZHNO_KAZ_OBLAST_REGIONS =
            new WidgetRegions(YUZHNO_KAZAHSTANSKAYA_OBLAST, new ArrayList<String>());

    private static final WidgetRegions MUNICH_REGIONS = new WidgetRegions(MYUNHEN, "103750");
    private static final WidgetRegions TOKIO_REGIONS = new WidgetRegions(TOKIO, new ArrayList<String>());
    private static final WidgetRegions NEW_YORK_REGIONS = new WidgetRegions(NYU_YORK, SSHA.getRegionId(), "29349");
    private static final WidgetRegions LONDON_REGIONS = new WidgetRegions(LONDON, new ArrayList<String>());

    public static final List<WidgetRegions> WIDGET_REGIONS_LIST = Arrays.asList(
            DUBNA_REGIONS, SPB_REGIONS, NOVOSIBIRSK_REGIONS, EKB_REGIONS, OMSK_REGIONS, VIBORG_REGIONS,
            KIEV_REGIONS, KIEVSKAYA_OBLAST_REGIONS, DONECK_REGIONS, HARKOV_REGIONS, LVOV_REGIONS, FEODOSIYA_REGIONS,
            MINSK_REGIONS, VITEBSK_REGIONS, MOGILEV_REGIONS, GOMELSKAYA_OBLAST_REGIONS, BREST_REGIONS, BORISOV_REGIONS,
            ASTANA_REGIONS, ALMATY_REGIONS, AKTOBE_REGIONS, KARAGANDA_REGIONS, PAVLODAR_REGIONS,
            YUZHNO_KAZ_OBLAST_REGIONS, MUNICH_REGIONS, LONDON_REGIONS
    );

    private static class RegionInfo {
        protected Region region;
        protected List<String> regions;

        public RegionInfo(Region region, String... regions) {
            this.region = region;
            this.regions = new ArrayList<String>();
            this.regions.addAll(Arrays.asList(regions));
        }

        public RegionInfo(Region region, List<String> regions) {
            this.region = region;
            this.regions = regions;
        }

        public Region getRegion() {
            return region;
        }

        public List<String> getRegions() {
            return regions;
        }

        @Override
        public String toString() {
            return region.toString();
        }
    }

    public static class RegionCategories extends RegionInfo {
        public RegionCategories(Region region, String... regions) {
            super(region, regions);
        }

        public RegionCategories(Region region, List<String> regions) {
            super(region, regions);
        }
    }

    public static class WidgetRegions extends RegionCategories {
        public WidgetRegions(Region region, String... regions) {
            super(region, regions);
            this.regions.add(region.getRegionId());
        }

        public WidgetRegions(Region region, List<String> regions) {
            super(region, regions);
            this.regions.add(region.getRegionId());
        }

        public Matcher<String> getRegionMatcher() {
            ArrayList<Matcher<String>> matchers = new ArrayList<Matcher<String>>();
            for (String str : regions) {
                matchers.add(containsString("?region=" + str));
            }
            return anyOf(matchers.toArray(new Matcher[matchers.size()]));
        }
    }


}
