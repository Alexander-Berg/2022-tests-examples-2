package ru.yandex.autotests.metrika.tests.ft.report.analytics;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.AnalyticsV3DataGaGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.empty;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 25.05.2016.
 */
@Features({Requirements.Feature.ANALYTICS, "METR-28377"})
@Stories({Requirements.Story.Report.Type.ANALYTICS})
@Title("Отчет 'Google Analytics': пустые отчеты")
@RunWith(Parameterized.class)
public class ExcludedAnalyticsEmptyReportTest {
    private static final Counter COUNTER = TEST_CONDITIONS_LIMIT;
    private static final String USER_METRIC = "ga:users";
    private static final String SESSION_METRIC = "ga:sessions";
    private static final String GOAL_CONVERSION_METRIC = "ga:goalValueAll";
    private static final String PAGE_TRACKING_METRIC = "ga:pageviews";
    private static final String SITE_SPEED_METRIC = "ga:pageLoadTime";
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    private UserSteps user;

    @Parameter()
    public String metric;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {USER_METRIC},
                {SESSION_METRIC},
                {GOAL_CONVERSION_METRIC},
                {PAGE_TRACKING_METRIC},
                {SITE_SPEED_METRIC}
        });
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Test
    public void analyticsEmptyReportUsersTest() {
        AnalyticsV3DataGaGETSchema report = user.onReportSteps()
                .getAnalyticsReportAndExpectSuccess(new AnalyticsParameters()
                        .withIds(COUNTER.get(ID))
                        .withMetrics(metric)
                        .withStartDate(START_DATE)
                        .withEndDate(END_DATE)
                        .withStartIndex(1));

        assertThat("отчет не содержит данных", report.getRows(), empty());
    }
}
