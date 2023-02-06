package ru.yandex.autotests.mordabackend.mobile.poi;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.poi_groups.PoiGroups;
import ru.yandex.autotests.mordabackend.beans.poi_groups.PoiGroupsItem;
import ru.yandex.autotests.mordabackend.beans.poi_groups.PoiGroupsItemDetail;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.PoiGroupsEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static ch.lambdaj.Lambda.selectDistinct;
import static ch.lambdaj.Lambda.sort;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEOID;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ISHOLIDAY;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LOCAL;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.POI_GROUPS;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.GeosMatcher.geos;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Poi Groups Block")
@Features("Mobile")
@Stories("Poi Groups Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class PoiGroupsTouchBlockTest {

    private static final int WEIGHT_0 = 20;

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, NIZHNIY_NOVGOROD, EKATERINBURG)
                    .withUserAgents(TOUCH, WP8, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(CleanvarsBlock.POI_GROUPS, GEOID, LOCAL, ISHOLIDAY, HIDDENTIME);

    private final Cleanvars cleanvars;

    private List<PoiGroupsEntry> poiGroupsEntries;

    public PoiGroupsTouchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                   UserAgent userAgent) {
        this.cleanvars = cleanvars;
    }

    @Before
    public void init() {
        boolean isHoliday = cleanvars.getIsHoliday() != null && !cleanvars.getIsHoliday().equals("0");
        String weekDayNumber = cleanvars.getLocal().getWday() == 0 ? "7" :
                String.valueOf(cleanvars.getLocal().getWday());

        List<PoiGroupsEntry> poiGroupsEntries = new ArrayList<>();
        List<PoiGroupsEntry> entries = exports(POI_GROUPS, geos(cleanvars.getGeoID()),
                anyOf(
                        having(on(PoiGroupsEntry.class).getWeekDay(),
                                isHoliday ? equalTo("holiday") : equalTo("workday")),
                        having(on(PoiGroupsEntry.class).getWeekDay(), containsString(weekDayNumber)),
                        having(on(PoiGroupsEntry.class).getWeekDay(), isEmptyOrNullString())
                ),
                anyOf(
                        allOf(
                                having(on(PoiGroupsEntry.class).getFrom(),
                                        before("yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
                                having(on(PoiGroupsEntry.class).getTill(),
                                        after("yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime()))
                        ),
                        allOf(
                                having(on(PoiGroupsEntry.class).getFrom(), isEmptyOrNullString()),
                                having(on(PoiGroupsEntry.class).getTill(), isEmptyOrNullString())
                        )
                )
        );

        for (int order : selectDistinct(extract(entries, on(PoiGroupsEntry.class).getOrder()))) {
            List<PoiGroupsEntry> items = select(entries, having(on(PoiGroupsEntry.class).getOrder(), equalTo(order)));
            Collections.sort(items, new Comparator<PoiGroupsEntry>() {
                @Override
                public int compare(PoiGroupsEntry o1, PoiGroupsEntry o2) {
                    return Integer.compare(calcWeight2Day(o2, cleanvars), calcWeight2Day(o1, cleanvars));
                }
            });
            poiGroupsEntries.add(items.get(0));
        }
        this.poiGroupsEntries = sort(poiGroupsEntries, on(PoiGroupsEntry.class).getOrder());
    }

    @Test
    public void poiGroups() {
        shouldMatchTo(cleanvars.getPoiGroups(), allOfDetailed(
                hasPropertyWithValue(on(PoiGroups.class).getBrowserOk(), equalTo(1)),
                hasPropertyWithValue(on(PoiGroups.class).getShow(), equalTo(1))
        ));
    }

    @Test
    public void poiGroupsItems() {
        List<PoiGroupsItem> items = cleanvars.getPoiGroups().getList();
        shouldMatchTo(items, hasSize(poiGroupsEntries.size()));
        for (int i = 0; i < items.size(); i++) {
            PoiGroupsItem item = items.get(i);
            PoiGroupsEntry export = poiGroupsEntries.get(i);
            shouldMatchTo(item, allOfDetailed(
                    hasPropertyWithValue(on(PoiGroupsItem.class).getGroup(), equalTo(export.getId())),
                    hasPropertyWithValue(on(PoiGroupsItem.class).getHideCategory(), equalTo(export.getHideCategory())),
                    hasPropertyWithValue(on(PoiGroupsItem.class).getSubgroups(),
                            hasSameItemsAsList(Arrays.asList(export.getSubgroupsList().split(", "))))
            ));

            shouldMatchTo(item.getDetail(), allOfDetailed(
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getGeos(), equalTo(export.getGeos())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getId(), equalTo(export.getId())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getHideCategory(),
                            equalTo(export.getHideCategory())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getOrder(), equalTo(export.getOrder())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getSubgroupsList(),
                            equalTo(export.getSubgroupsList())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getWeekDay(),
                            equalTo(export.getWeekDay())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getMorning(),
                            equalTo(export.getMorning())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getDay(),
                            equalTo(export.getDay())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getEvening(),
                            equalTo(export.getEvening())),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getNight(),
                            equalTo(export.getNight())),

                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getWeight(),
                            equalTo(calcWeight2Day(export, cleanvars))),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getWeight0(),
                            equalTo(WEIGHT_0)),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getWeight1Week(),
                            equalTo(calcWeight1Week(export, cleanvars))),
                    hasPropertyWithValue(on(PoiGroupsItemDetail.class).getWeight2Day(),
                            equalTo(calcWeight2Day(export, cleanvars)))
            ));
        }
    }

    private int calcWeight1Week(PoiGroupsEntry entry, Cleanvars cleanvars) {
        boolean isHoliday = cleanvars.getIsHoliday() != null && !cleanvars.getIsHoliday().equals("0");
        String weekDayNumber = cleanvars.getLocal().getWday() == 0 ? "7" :
                String.valueOf(cleanvars.getLocal().getWday());

        if (entry.getWeekDay() != null && (
                !isHoliday && "workday".equals(entry.getWeekDay()) ||
                        isHoliday && "holiday".equals(entry.getWeekDay()) ||
                        entry.getWeekDay().contains(weekDayNumber))) {
            return WEIGHT_0 * 2;
        } else {
            return WEIGHT_0;
        }
    }

    private int calcWeight2Day(PoiGroupsEntry entry, Cleanvars cleanvars) {
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
        } else if (hour >= 12 && hour < 17) {
            return "day";
        } else if ((hour >= 17 && hour < 23) || (hour == 23 && mins < 30)) {
            return "evening";
        } else {
            return "night";
        }
    }
}
