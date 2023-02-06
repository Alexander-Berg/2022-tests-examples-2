package ru.yandex.autotests.morda.tests.poi.cleanvars;

import org.apache.commons.collections.CollectionUtils;
import org.apache.log4j.Logger;
import org.joda.time.LocalDateTime;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.poi_groups.PoiGroupsItem;
import ru.yandex.autotests.morda.beans.exports.poi_groups.PoiGroupsEntry;
import ru.yandex.autotests.morda.beans.exports.poi_groups.PoiGroupsExport;
import ru.yandex.autotests.morda.exports.filters.MordaExportFilters;
import ru.yandex.autotests.morda.exports.filters.MordaGeosFilter;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithWeekDay;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.joda.time.format.DateTimeFormat.forPattern;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.fromPredicate;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.tillPredicate;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.POI_REGIONS;

/**
 * User: asamar
 * Date: 16.01.17
 */
@Aqua.Test(title = "Poi groups")
@RunWith(Parameterized.class)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.POI})
public class PoiGroupsCleanvarsTest {
    private static Logger LOGGER = Logger.getLogger(PoiGroupsCleanvarsTest.class);
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private static Map<String, String> intervalMapping = new HashMap<String, String>() {{
        put("morning", "08:30");
        put("day", "15:30");
        put("lunch", "17:00");
        put("evening", "20:30");
        put("night", "23:40");
    }};

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        for (String interval : intervalMapping.keySet()) {
            POI_REGIONS.forEach(region ->
                    data.add(new Object[]{touchMain(CONFIG.pages().getEnvironment()).region(region), interval})
            );
        }

        return data;
    }

    private MainMorda<?> morda;
    private List<String> groupsFromExport;
    private List<String> groupsFromCleanvars;
    private String interval;

    public PoiGroupsCleanvarsTest(MainMorda<?> morda, String interval) {
        this.morda = morda;
        this.interval = interval;
    }

    @Before
    public void init() {
        PoiGroupsExport export = new PoiGroupsExport().populate(morda.getUrl());
        MordaCleanvars cleanvars = new MordaClient().cleanvars(morda)
                .queryParam("time", intervalMapping.get(interval))
                .read();
        LocalDateTime now = forPattern("yyyy-MM-dd HH:mm:ss")
                .parseLocalDateTime(cleanvars.getHiddenTime());

        this.groupsFromCleanvars = cleanvars.getPoiGroups().getList().stream()
                .map(PoiGroupsItem::getGroup)
                .collect(toList());
        LOGGER.info("PoiGroups in cleanvars: " + groupsFromCleanvars);
        this.groupsFromExport = export.getData().stream()
                .filter(MordaGeosFilter.filter(morda.getRegion()))
                .filter(disabledPredicate())
                .filter(weekDayPredicate(cleanvars))
                .filter(tillPredicate(now))
                .filter(fromPredicate(now))
                .filter(intervalPredicate(interval))
                .map(PoiGroupsEntry::getId)
                .distinct()
                .collect(toList());
        LOGGER.info("Groups from poi_groups export: " + groupsFromExport);
    }

    @Test
    public void compareGroups() {
        assertThat("Группы в экспорте poi_groups и в cleanvars разные",
                CollectionUtils.isEqualCollection(groupsFromCleanvars, groupsFromExport));
    }

    private Predicate<EntryWithWeekDay> weekDayPredicate(MordaCleanvars cleanvars) {
        String weekDayNumber = cleanvars.getLocal().getWday() == 0 ? "7" :
                String.valueOf(cleanvars.getLocal().getWday());
        return MordaExportFilters.weekDayPredicate(weekDayNumber);
    }

    private Predicate<PoiGroupsEntry> intervalPredicate(String interval) {
        switch (interval) {
            case "morning":
                return (entry) -> entry.getMorning() != 0;
            case "day":
                return (entry) -> {
                    if (entry.getDay() == 0 && entry.getLunch() != 0) {
                        return entry.getLunch() != 0;
                    } else {
                        return entry.getDay() != 0;
                    }
                };
            case "lunch":
                return (entry) -> {
                    if (entry.getLunch() < 1) {
                        return entry.getDay() != 0;
                    } else {
                        return entry.getLunch() != 0;
                    }
                };
            case "evening":
                return (entry) -> entry.getEvening() != 0;
            case "night":
                return (entry) -> entry.getNight() != 0;
            default:
                return (entry) -> true;
        }
    }

    private Predicate<PoiGroupsEntry> disabledPredicate() {
        return e -> !"1".equals(e.getDisabled());
    }
}
