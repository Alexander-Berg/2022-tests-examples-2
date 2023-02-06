package ru.yandex.autotests.mordabackend.mobile.poi;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.poi_favourite.PoiFavourite;
import ru.yandex.autotests.mordabackend.beans.poi_favourite.PoiFavouriteItem;
import ru.yandex.autotests.mordabackend.beans.poi_favourite.PoiFavouriteItemDetail;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordaexportsclient.beans.PoiFavouriteEntry;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.*;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.POI_FAVOURITE;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.GeosMatcher.geos;
import static ru.yandex.autotests.utils.morda.region.Region.*;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 *
 */
//@Aqua.Test(title = "Poi Favorite Block")
//@Features("Mobile")
//@Stories("Poi Favorite Block")
//@RunWith(CleanvarsParametrizedRunner.class)
public class PoiFavoriteTouchBlockTest {

//    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, ASTANA, NIZHNIY_NOVGOROD, EKATERINBURG, LYUDINOVO)
                    .withUserAgents(TOUCH, WP8, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(CleanvarsBlock.POI_FAVOURITE, GEOID, LOCAL, ISHOLIDAY);

    private final Cleanvars cleanvars;

    private List<PoiFavouriteEntry> poiFavouriteEntries;

    public PoiFavoriteTouchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                     UserAgent userAgent) {
        this.cleanvars = cleanvars;
    }

//    @Before
    public void init() {
        boolean isHoliday = cleanvars.getIsHoliday() != null && !cleanvars.getIsHoliday().equals("0");
        String weekDayNumber = cleanvars.getLocal().getWday() == 0 ? "7" :
                String.valueOf(cleanvars.getLocal().getWday());

        List<PoiFavouriteEntry> poiFavouriteEntriesAll =
                exports(POI_FAVOURITE, geos(cleanvars.getGeoID()),
                        anyOf(
                                having(on(PoiFavouriteEntry.class).getWeekDay(),
                                        isHoliday ? equalTo("holiday") : equalTo("work")),
                                having(on(PoiFavouriteEntry.class).getWeekDay(), containsString(weekDayNumber)),
                                having(on(PoiFavouriteEntry.class).getWeekDay(), isEmptyOrNullString())
                        ));
        Collections.sort(poiFavouriteEntriesAll, new Comparator<PoiFavouriteEntry>() {
            @Override
            public int compare(PoiFavouriteEntry o1, PoiFavouriteEntry o2) {
                return Integer.compare(calcWeight2Day(o2, cleanvars), calcWeight2Day(o1, cleanvars));
            }
        });
        Map<String, Integer> groupLimits = new HashMap<>();
        Map<String, Integer> subgroupLimits = new HashMap<>();
        List<PoiFavouriteEntry> poiFavouriteEntries = new ArrayList<>();
        for (PoiFavouriteEntry e : poiFavouriteEntriesAll) {
            int groupPos = groupLimits.containsKey(e.getId()) ? groupLimits.get(e.getId()) + 1 : 1;
            groupLimits.put(e.getId(), groupPos);

            int subgroupPos = subgroupLimits.containsKey(e.getSubgroup()) ? subgroupLimits.get(e.getSubgroup()) + 1 : 1;
            subgroupLimits.put(e.getSubgroup(), subgroupPos);

            if (groupPos <= 4 && subgroupPos <= 2) {
                poiFavouriteEntries.add(e);
            }
        }

        this.poiFavouriteEntries = poiFavouriteEntries;
    }

//    @Test
    public void poiFavourite() {
        shouldMatchTo(cleanvars.getPoiFavourite(), allOfDetailed(
                hasPropertyWithValue(on(PoiFavourite.class).getShow(), equalTo(1))
        ));
    }

//    @Test
    public void poiFavouriteItems() {
        List<PoiFavouriteItem> items = cleanvars.getPoiFavourite().getList();
        shouldMatchTo(items, hasSize(poiFavouriteEntries.size()));
        for (int i = 0; i < items.size(); i++) {
            PoiFavouriteItem item = items.get(i);
            PoiFavouriteEntry export = poiFavouriteEntries.get(i);
            shouldMatchTo(item, allOfDetailed(
                    hasPropertyWithValue(on(PoiFavouriteItem.class).getGroup(), equalTo(export.getId())),
                    hasPropertyWithValue(on(PoiFavouriteItem.class).getSubgroup(), equalTo(export.getSubgroup())),
                    hasPropertyWithValue(on(PoiFavouriteItem.class).getWeight(),
                            equalTo(calcWeight2Day(export, cleanvars)))
            ));

            shouldMatchTo(item.getDetail(), allOfDetailed(
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getGeos(), equalTo(export.getGeos())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getId(), equalTo(export.getId())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getSubgroup(), equalTo(export.getSubgroup())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getWeekDay(), equalTo(export.getWeekDay())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getMorning(), equalTo(export.getMorning())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getDay(), equalTo(export.getDay())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getEvening(), equalTo(export.getEvening())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getNight(), equalTo(export.getNight())),

                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getWeight(),
                            equalTo(calcWeight2Day(export, cleanvars))),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getWeight0(),
                            equalTo(export.getWeightDef())),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getWeight1Week(),
                            equalTo(calcWeight1Week(export, cleanvars))),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getWeight2Day(),
                            equalTo(calcWeight2Day(export, cleanvars))),
                    hasPropertyWithValue(on(PoiFavouriteItemDetail.class).getWeightDef(),
                            equalTo(export.getWeightDef()))
            ));
        }
    }

    private int calcWeight1Week(PoiFavouriteEntry entry, Cleanvars cleanvars) {
        String weekDayNumber = cleanvars.getLocal().getWday() == 0 ? "7" :
                String.valueOf(cleanvars.getLocal().getWday());
        if (entry.getWeekDay() == null) {
            return entry.getWeightDef();
        } else if (cleanvars.getIsHoliday() == null && "workday".equals(entry.getWeekDay()) ||
                "1".equals(cleanvars.getIsHoliday()) && "holiday".equals(entry.getWeekDay()) ||
                entry.getWeekDay().contains(weekDayNumber))
        {
            return entry.getWeightDef() * 2;
        } else {
            return entry.getWeightDef();
        }
    }

    private int calcWeight2Day(PoiFavouriteEntry entry, Cleanvars cleanvars) {
        switch (getDayTime(cleanvars)) {
            case "morning":
                return calcWeight1Week(entry, cleanvars) + (entry.getMorning() * 10);
            case "day":
                return calcWeight1Week(entry, cleanvars) + (entry.getDay() * 10);
            case "evening":
                return calcWeight1Week(entry, cleanvars) + (entry.getEvening() * 10);
            case "night":
                return calcWeight1Week(entry, cleanvars) + (entry.getNight() * 10);
            default:
                return calcWeight1Week(entry, cleanvars);
        }
    }

    private String getDayTime(Cleanvars cleanvars) {
        int hour = cleanvars.getLocal().getHour();
        int mins = cleanvars.getLocal().getMin();
        if (hour >= 7 && hour < 12) {
            return "morning";
        } else if (hour >= 12 && hour < 18) {
            return "day";
        } else if ((hour >= 18 && hour < 23) || (hour == 23 && mins < 30)) {
            return "evening";
        } else {
            return "night";
        }
    }
}
