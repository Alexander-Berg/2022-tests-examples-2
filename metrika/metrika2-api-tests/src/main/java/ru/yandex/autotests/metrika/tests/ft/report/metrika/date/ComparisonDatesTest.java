package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by konkov on 24.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.COMPARISON)
@Title("Тесты на временные границы сегментов")
@RunWith(Parameterized.class)
public class ComparisonDatesTest {

    private static final Counter counter = CounterConstants.NO_DATA;

    private static final String METRIC_NAME = "ym:s:users";
    private static final String DIMENSION_NAME = "ym:s:operatingSystem";

    private static final String[] DATES_ABS = {"2014-08-01", "2014-08-02", "2014-08-03", "2014-08-04"};
    private static final String[] DATES_REL = {"3daysAgo", "2daysAgo", "yesterday", "today"};

    private static UserSteps user;

    @Parameterized.Parameter(value = 0)
    public String date1a;

    @Parameterized.Parameter(value = 1)
    public String date2a;

    @Parameterized.Parameter(value = 2)
    public String date1b;

    @Parameterized.Parameter(value = 3)
    public String date2b;

    private ComparisonReportParameters reportParameters;

    @Parameterized.Parameters(name = "{0} - {1}, {2} - {3}")
    public static Collection createParameters() {
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

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        AllureUtils.addTestParameter("date1_a", date1a);
        AllureUtils.addTestParameter("date2_a", date2a);
        AllureUtils.addTestParameter("date1_b", date1b);
        AllureUtils.addTestParameter("date2_b", date2b);

        reportParameters = new ComparisonReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(METRIC_NAME);
        reportParameters.setDimension(DIMENSION_NAME);
        reportParameters.setSort(sort().by(METRIC_NAME).descending().build());
        reportParameters.setDate1_a(date1a);
        reportParameters.setDate2_a(date2a);
        reportParameters.setDate1_b(date1b);
        reportParameters.setDate2_b(date2b);
    }

    @Test
    public void comparisonDatesTest() {
        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }
}
