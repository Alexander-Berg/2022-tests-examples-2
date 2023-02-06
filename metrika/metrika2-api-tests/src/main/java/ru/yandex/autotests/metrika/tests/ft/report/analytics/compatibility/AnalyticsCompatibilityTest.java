package ru.yandex.autotests.metrika.tests.ft.report.analytics.compatibility;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum.HIGHER_PRECISION;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DEMOCRAT_SPB;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 30.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'google analytics': совместимость id и ids")
public class AnalyticsCompatibilityTest {
    private UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = DEMOCRAT_SPB;
    private static final String METRIC = "ga:users";

    private static final String START_DATE = "2015-09-01";
    private static final String END_DATE = "2015-09-01";

    private List<List<String>> report1;
    private List<List<String>> report2;

    @Before
    public void setup() {
        report1 = user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                new AnalyticsParameters()
                        .withIds(COUNTER)
                        .withMetrics(METRIC)
                        .withStartDate(START_DATE)
                        .withEndDate(END_DATE)
                        .withSamplingLevel(HIGHER_PRECISION)
                        .withStartIndex(1)).getRows();

        report2 = user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                new AnalyticsParameters()
                        .withId(COUNTER.get(ID))
                        .withMetrics(METRIC)
                        .withStartDate(START_DATE)
                        .withEndDate(END_DATE)
                        .withSamplingLevel(HIGHER_PRECISION)
                        .withStartIndex(1)).getRows();
    }

    @Test
    public void idsTest() {
        assertThat("значение метрик в отчете совпадает", report2, equalTo(report1));
    }
}
