package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.errors.AnalyticsReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sourx on 27.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'google analytics': фильтры, не более 20-ти уникальных метрик и измерений в условиях")
public class AnalyticsFiltersUniqueAttributesTest {
    private static final int ATTRIBUTES_LIMIT = 20;
    private static final Counter COUNTER = CounterConstants.NO_DATA;
    protected static final String START_DATE = "14daysAgo";
    protected static final String END_DATE = "7daysAgo";

    private static UserSteps user;

    private static final List<String> DIMENSIONS = asList(
            "ga:referralPath",
            "ga:fullReferrer",
            "ga:campaign",
            "ga:source",
            "ga:medium",
            "ga:sourceMedium",
            "ga:keyword",
            "ga:adContent",
            "ga:region",
            "ga:day",
            "ga:hour",
            "ga:year",
            "ga:month",
            "ga:week",
            "ga:sessionCount",
            "ga:browserVersion",
            "ga:mobileDeviceModel",
            "ga:mobileDeviceInfo",
            "ga:continent",
            "ga:country",
            "ga:city"
    );

    private static final List<String> METRICS = asList(
            "ga:users",
            "ga:newUsers",
            "ga:percentNewSessions",
            "ga:sessions",
            "ga:sessionsPerUser",
            "ga:bounces",
            "ga:bounceRate",
            "ga:sessionDuration",
            "ga:hits",
            "ga:pageviewsPerSession",
            "ga:pageviews",
            "ga:adClicks",
            "ga:impressions",
            "ga:adCost",
            "ga:CPM",
            "ga:CPC",
            "ga:CTR",
            "ga:costPerTransaction",
            "ga:costPerGoalConversion",
            "ga:costPerConversion",
            "ga:RPC",
            "ga:ROAS"
    );

    private AnalyticsParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();

        assumeThat("для теста доступен список метрик", METRICS,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));

        assumeThat("для теста доступен список измерений", DIMENSIONS,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));
    }

    @Before
    public void setup() {
        reportParameters = new AnalyticsParameters()
                .withIds(COUNTER.get(ID))
                .withStartDate(START_DATE)
                .withEndDate(END_DATE)
                .withMetrics(METRICS.get(0))
                .withStartIndex(1);
    }

    @Test
    public void maximumMetricsInFilter() {
        reportParameters.setFilters(
                user.onAnalyticsFilterSteps().getAnalyticsFilterWithAttributes(METRICS, ATTRIBUTES_LIMIT));

        user.onReportSteps().getAnalyticsReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumMetricsInFilter() {
        reportParameters.setFilters(
                user.onAnalyticsFilterSteps().getAnalyticsFilterWithAttributes(METRICS, ATTRIBUTES_LIMIT + 1));

        user.onReportSteps().getAnalyticsReportAndExpectError(
                AnalyticsReportError.TOO_MANY_ATTRIBUTES, reportParameters);
    }


    @Test
    public void maximumDimensionsInFilter() {
        reportParameters.setFilters(
                user.onAnalyticsFilterSteps().getAnalyticsFilterWithAttributes(DIMENSIONS, ATTRIBUTES_LIMIT));

        user.onReportSteps().getAnalyticsReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumDimensionsInFilter() {
        reportParameters.setFilters(
                user.onAnalyticsFilterSteps().getAnalyticsFilterWithAttributes(DIMENSIONS, ATTRIBUTES_LIMIT + 1));

        user.onReportSteps().getAnalyticsReportAndExpectError(
                AnalyticsReportError.TOO_MANY_ATTRIBUTES, reportParameters);
    }
}

