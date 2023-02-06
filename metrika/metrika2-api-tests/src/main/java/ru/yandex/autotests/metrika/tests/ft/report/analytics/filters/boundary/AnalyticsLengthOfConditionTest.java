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

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by sourx on 27.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS})
@Title("Отчет 'google analytics': фильтры, не более 2000 символов в строке в одном условии)")
public class AnalyticsLengthOfConditionTest {
    private static final Counter COUNTER = CounterConstants.NO_DATA;
    protected static final String START_DATE = "14daysAgo";
    protected static final String END_DATE = "7daysAgo";
    private static final int CONDITIONS_LENGTH_LIMIT = 2000;

    private static UserSteps user;

    private final static String DIMENSION = "ga:country";
    private final static String METRIC = "ga:users";

    private AnalyticsParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new AnalyticsParameters()
                .withIds(COUNTER.get(ID))
                .withStartDate(START_DATE)
                .withEndDate(END_DATE)
                .withDimensions(DIMENSION)
                .withMetrics(METRIC)
                .withStartIndex(1);
    }

    @Test
    public void maximumConditionLength() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterWithSingleCondition(DIMENSION, CONDITIONS_LENGTH_LIMIT));

        user.onReportSteps().getAnalyticsReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumConditionLength() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterWithSingleCondition(DIMENSION, CONDITIONS_LENGTH_LIMIT + 1));

        user.onReportSteps().getAnalyticsReportAndExpectError(
                AnalyticsReportError.TOO_LONG_TERMS,
                reportParameters);
    }
}
