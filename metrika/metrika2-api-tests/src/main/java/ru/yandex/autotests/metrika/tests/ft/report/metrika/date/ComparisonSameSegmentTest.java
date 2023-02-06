package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.ComparisonRowStaticAB;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.matchers.ComparisonDataObjectMatcher.noDifference;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 24.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.COMPARISON)
@Title("Тест на совпадение данных в одном и том же сегменте")
public class ComparisonSameSegmentTest {

    private static final Counter counter = CounterConstants.LITE_DATA;

    private static final String METRIC_NAME = "ym:s:users";
    private static final String DIMENSION_NAME = "ym:s:operatingSystem";

    private static UserSteps user;

    private static final String date1 = "2014-09-01";
    private static final String date2 = "2014-09-02";

    private ComparisonReportParameters reportParameters;
    private StatV1DataComparisonGETSchema result;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new ComparisonReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(METRIC_NAME);
        reportParameters.setDimension(DIMENSION_NAME);
        reportParameters.setSort(sort().by(METRIC_NAME).descending().build());
        reportParameters.setDate1_a(date1);
        reportParameters.setDate2_a(date2);
        reportParameters.setDate1_b(date1);
        reportParameters.setDate2_b(date2);

        result = user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void comparisonCheckSegmentsEquality() {
        assertThat("данные в сегментах совпадают", result,
                both(having(on(StatV1DataComparisonGETSchema.class).getData(),
                        everyItem(having(on(ComparisonRowStaticAB.class).getMetrics(), noDifference()))))
                        .and(having(on(StatV1DataComparisonGETSchema.class).getTotals(), noDifference())));
    }
}
