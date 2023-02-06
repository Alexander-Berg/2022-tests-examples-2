package ru.yandex.autotests.metrika.tests.ft.report.analytics.dimensions;

import org.apache.commons.lang3.ArrayUtils;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;

/**
 * Created by sourx on 30.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Отчет 'google analytics': измерения (custom)")
@RunWith(Parameterized.class)
public class AnalyticsDimensionsSelectedTest {
    /**
     * Специально отобранные измерения, при использовании которых возникала бесконечная рекурсия.
     */
    private static final List<String> DIMENSIONS = asList(
            "ga:socialNetwork",
            "ga:browser",
            "ga:operatingSystem",
            "ga:operatingSystemVersion",
            "ga:mobileDeviceBranding",
            "ga:interestAffinityCategory",
            "ga:trafficSource",
            "ga:searchEngine",
            "ga:advEngine"
    );

    private final String METRIC = "ga:pageviews";
    private final Counter COUNTER = CounterConstants.NO_DATA;
    private final String START_DATE = "2015-01-01";
    private final String END_DATE = "2015-01-02";

    private UserSteps user;

    @Parameterized.Parameter()
    public String dimension;

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return DIMENSIONS.stream().map(ArrayUtils::toArray).collect(toList());
    }

    @Before
    public void setup() {
        user = new UserSteps();
    }

    @Test
    public void stackOverflowTest() {
        user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                new AnalyticsParameters()
                        .withIds(COUNTER)
                        .withStartDate(START_DATE)
                        .withEndDate(END_DATE)
                        .withMetrics(METRIC)
                        .withDimensions(dimension)
                        .withStartIndex(1)
        );
    }

}
