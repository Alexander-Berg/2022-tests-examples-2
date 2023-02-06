package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.lang.String.valueOf;
import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MARKET;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.Utils.combineCollections;

/**
 * Created by konkov on 29.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.COMPARISON_DRILLDOWN)
@Title("Тесты на временные границы сегментов drill down")
@RunWith(Parameterized.class)
public class ComparisonDrillDownDatesTest {

    private static String METRIC_NAME = "ym:s:users";

    private static String[] DIMENSION_NAMES = {
            "ym:s:startURLPathLevel1",
            "ym:s:startURLPathLevel2",
            "ym:s:startURLPathLevel3",
            "ym:s:startURLPathLevel4",
            "ym:s:startURLPathLevel5",
            "ym:s:endURLPathLevel1",
            "ym:s:endURLPathLevel2",
            "ym:s:endURLPathLevel3",
            "ym:s:endURLPathLevel4",
            "ym:s:endURLPathLevel5"
    };

    private static final String[] DATES_ABS = {"2014-08-01", "2014-08-02", "2014-08-03", "2014-08-04"};
    private static final String[] DATES_REL = {"3daysAgo", "2daysAgo", "yesterday", "today"};

    private static UserSteps user;
    private static Counter counter = YANDEX_MARKET;

    @Parameter(value = 0)
    public String date1a;

    @Parameter(value = 1)
    public String date2a;

    @Parameter(value = 2)
    public String date1b;

    @Parameter(value = 3)
    public String date2b;

    @Parameter(value = 4)
    public List<String> parentIds;

    @Parameters(name = "parent_id={4} {0} - {1}, {2} - {3}")
    public static Collection createParameters() {
        return combineCollections(getDatesParameters(), getParentsParameters());
    }

    private static List<Object[]> getDatesParameters() {
        return asList(new Object[][]{
                {DATES_ABS[0], DATES_ABS[1], DATES_ABS[2], DATES_ABS[3]},
                {DATES_ABS[2], DATES_ABS[3], DATES_ABS[0], DATES_ABS[1]},
                {DATES_ABS[0], DATES_ABS[2], DATES_ABS[1], DATES_ABS[3]},
                {DATES_ABS[0], DATES_ABS[1], DATES_ABS[1], DATES_ABS[2]},
                {DATES_ABS[1], DATES_ABS[3], DATES_ABS[0], DATES_ABS[2]},

                {DATES_REL[0], DATES_REL[1], DATES_REL[2], DATES_REL[3]},
                {DATES_REL[2], DATES_REL[3], DATES_REL[0], DATES_REL[1]},
                {DATES_REL[0], DATES_REL[2], DATES_REL[1], DATES_REL[3]},
                {DATES_REL[0], DATES_REL[1], DATES_REL[1], DATES_REL[2]},
                {DATES_REL[1], DATES_REL[3], DATES_REL[0], DATES_REL[2]},
        });
    }

    private static List<Object[]> getParentsParameters() {
        return asList(new Object[][]{
                {asList()},
                {asList("http://metrika.yandex.ru/")},
                {asList("http://metrika.yandex.ru/", "http://metrika.yandex.ru/list/")}
        });
    }

    private ComparisonDrilldownReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        addTestParameter("date1_a", date1a);
        addTestParameter("date2_a", date2a);
        addTestParameter("date1_b", date1b);
        addTestParameter("date2_b", date2b);
        addTestParameter("parent_id", valueOf(parentIds));

        reportParameters = new ComparisonDrilldownReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(METRIC_NAME);
        reportParameters.setDimensions(DIMENSION_NAMES);
        reportParameters.setSort(sort().by(METRIC_NAME).descending().build());
        reportParameters.setDate1_a(date1a);
        reportParameters.setDate2_a(date2a);
        reportParameters.setDate1_b(date1b);
        reportParameters.setDate2_b(date2b);

        reportParameters.setParent_id(JsonUtils.toString(parentIds));
    }

    @Test
    public void comparisonDrilldownDatesTest() {
        user.onReportSteps().getComparisonDrilldownReportAndExpectSuccess(reportParameters);
    }
}
