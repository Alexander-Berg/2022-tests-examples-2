package ru.yandex.autotests.metrika.tests.b2b.metrika.conversion;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.stream.Collectors;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 17.08.16.
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Report.Type.TABLE)
@Title("B2B - Значение конверсии")
public class B2bConversionTest {
    protected final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();
    protected final UserSteps userOnRef = new UserSteps().useReference().withDefaultAccuracy();

    private final String SUM_VISITS_METRIC = "ym:s:sumVisits";
    private final String DIMENSION = "ym:s:goalDimension";

    private final Counter COUNTER = CounterConstants.LITE_DATA;
    private final String START_DATE = "2016-04-20";
    private final String END_DATE = "2016-05-19";

    int metricIndex;

    protected IFormParameters reportParameters;

    List<Double> referenceData;
    List<Double> testingData;

    Double testTotal;
    Double referenceTotal;

    @Before
    public void setup() {
        reportParameters = new TableReportParameters()
                .withMetric(SUM_VISITS_METRIC)
                .withDimension(DIMENSION)
                .withId(COUNTER)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withAccuracy("1")
                .withIncludeUndefined(true);

        StatV1DataGETSchema referenceResult = userOnRef.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
        StatV1DataGETSchema testResult = userOnRef.onReportSteps().getTableReportAndExpectSuccess(reportParameters);

        metricIndex = userOnRef.onResultSteps().getMetricIndex(referenceResult.getQuery(), SUM_VISITS_METRIC);

        referenceTotal = referenceResult.getTotals().get(metricIndex);
        testTotal = testResult.getTotals().get(metricIndex);

        referenceData = userOnRef.onResultSteps().getMetrics(SUM_VISITS_METRIC, referenceResult);
        testingData = userOnTest.onResultSteps().getMetrics(SUM_VISITS_METRIC, testResult);
    }

    @Test
    @Title("Значения конверсии не отличаются")
    public void checkConversion() {
        List<Double> testConversion = testingData.stream()
                .map(g -> g / testTotal).collect(Collectors.toList());
        List<Double> referenceConversion = referenceData.stream()
                .map(g -> g / referenceTotal).collect(Collectors.toList());

        assertThat("конверсии одинаковы",
                testConversion,
                beanEquivalent(referenceConversion));
    }
}
