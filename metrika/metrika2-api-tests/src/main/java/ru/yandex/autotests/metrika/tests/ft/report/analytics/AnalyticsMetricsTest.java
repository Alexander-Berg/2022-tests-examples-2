package ru.yandex.autotests.metrika.tests.ft.report.analytics;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.Function;

import static java.util.function.Function.identity;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum.DEFAULT;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.WIKIMART_RU;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;

/**
 * Created by sourx on 30.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.METRICS})
@Title("Отчет 'google analytics': метрики")
@RunWith(Parameterized.class)
public class AnalyticsMetricsTest {
    private static final Counter COUNTER = WIKIMART_RU;
    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";

    private static UserSteps user = new UserSteps().withDefaultAccuracy();

    @Parameter()
    public String metric;

    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "Метрика = {0}")
    public static Collection createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                user.onMetadataSteps().getAnalyticsMetrics(any()),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(
                        new AnalyticsParameters()
                                .withIds(COUNTER)
                                .withStartDate(START_DATE)
                                .withEndDate(END_DATE)
                                .withSamplingLevel(DEFAULT)
                                .withStartIndex(1)))
                .apply(parameterized(GOAL_ID), setParameters(goalId(COUNTER)))
                .build(identity());
    }

    @Test
    public void metricsTest() {
        user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                new AnalyticsParameters()
                        .withMetrics(metric),
                tail);
    }
}
