package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonDrilldownGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.ComparisonRowDrillDownAB;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.matchers.ComparisonDataObjectMatcher.noDifference;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 29.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.COMPARISON_DRILLDOWN)
@Title("Тест на совпадение данных в одном и том же сегменте drill down")
@RunWith(Parameterized.class)
public class ComparisonDrillDownSameSegmentTest {

    private static final String date1 = "2014-09-01";
    private static final String date2 = "2014-09-02";

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

    private static UserSteps user;
    private static Counter counter = CounterConstants.LITE_DATA;

    @Parameterized.Parameter()
    public List<String> parentIds;

    private ComparisonDrilldownReportParameters reportParameters;
    private StatV1DataComparisonDrilldownGETSchema result;

    @Parameterized.Parameters(name = "parent_id={0}")
    public static Collection createParameters() {
        return asList(new Object[][] {
                { asList() },
                { asList("http://yandex.com.tr/") },
                { asList("http://yandex.com.tr/", "http://yandex.com.tr/?clid=") }
        });
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new ComparisonDrilldownReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(METRIC_NAME);
        reportParameters.setDimensions(DIMENSION_NAMES);
        reportParameters.setSort(sort().by(METRIC_NAME).descending().build());
        reportParameters.setDate1_a(date1);
        reportParameters.setDate2_a(date2);
        reportParameters.setDate1_b(date1);
        reportParameters.setDate2_b(date2);

        reportParameters.setParent_id(JsonUtils.toString(parentIds));

        result = user.onReportSteps().getComparisonDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void comparisonDrilldownCheckSegmentsEquality() {
        assertThat("данные в сегментах совпадают", result,
                both(having(on(StatV1DataComparisonDrilldownGETSchema.class).getData(),
                        everyItem(having(on(ComparisonRowDrillDownAB.class).getMetrics(), noDifference()))))
                        .and(having(on(StatV1DataComparisonDrilldownGETSchema.class).getTotals(), noDifference())));
    }
}
