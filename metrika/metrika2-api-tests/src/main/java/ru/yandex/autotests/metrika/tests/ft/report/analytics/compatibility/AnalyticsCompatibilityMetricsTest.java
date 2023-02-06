package ru.yandex.autotests.metrika.tests.ft.report.analytics.compatibility;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.AnalyticsV3DataGaGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum.FASTER;
import static ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum.HIGHER_PRECISION;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.*;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters.parametrization;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasMetricValues;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;
import static ru.yandex.autotests.metrika.utils.Utils.flatten;

/**
 * Created by sourx on 03.08.16.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.METRICS})
@Title("Отчет 'google analytics': метрики (совместимость)")
@RunWith(Parameterized.class)
public class AnalyticsCompatibilityMetricsTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = YANDEX_MARKET;
    private static final String START_DATE = "2015-06-20";
    private static final String END_DATE = "2015-06-21";

    private static final Counter SHARE_SERVICES_COUNTER = YANDEX_METRIKA;

    private static final String VISIT_DIMENSION_NAME = "ym:s:gender";
    private static final String VISIT_ECOMMERCE_DIMENSION_NAME = "ym:s:date";
    private static final String HIT_DIMENSION_NAME = "ym:pv:gender";
    private static final String SHARE_SERVICES_DIMENSION_NAME = "ym:sh:gender";
    private static final String SITE_SPEED_DIMENSION_NAME = "ym:sp:gender";
    private static final String EXTERNAL_LINKS_DIMENSION_NAME = "ym:el:gender";
    private static final String DOWNLOADS_DIMENSION_NAME = "ym:dl:gender";
    private static final String USER_PARAM_DIMENSION_NAME = "ym:up:paramsLevel1";

    private static final Counter USER_PARAM_COUNTER = YANDEX_METRIKA_2_0;

    private static final Counter COUNTER_OFFLINE_CALLS = TEST_UPLOADINGS;
    private static final String START_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.START_DATE;
    private static final String END_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.END_DATE;
    private static final String START_DATE_PUBLISHERS = DateConstants.Publishers.START_DATE;
    private static final String END_DATE_PUBLISHERS = DateConstants.Publishers.END_DATE;


    @Parameter()
    public String metricName;

    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                user.onMetadataSteps().getMetrics((table(ADVERTISING).or(table(EXPENSES_VISITS))).negate()),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(
                        new AnalyticsParameters()
                                .withStartDate(START_DATE)
                                .withEndDate(END_DATE)
                                .withIds(COUNTER)
                                .withStartIndex(1)))
                .apply(table(HITS), setParameters(new AnalyticsParameters().withDimensions(HIT_DIMENSION_NAME)))
                .apply(table(VISITS), setParameters(new AnalyticsParameters().withDimensions(VISIT_DIMENSION_NAME)))
                .apply(ecommerce(), setParameters(
                        new AnalyticsParameters()
                                .withIds(ECOMMERCE_TEST)
                                .withDimensions(VISIT_ECOMMERCE_DIMENSION_NAME)
                                .withStartDate(DateConstants.Ecommerce.START_DATE)
                                .withEndDate(DateConstants.Ecommerce.END_DATE)
                                .withSamplingLevel(HIGHER_PRECISION)))
                .apply(yan(), setParameters(
                        new AnalyticsParameters()
                                .withIds(Counters.YANDEX_NEWS)
                                .withDimensions(VISIT_DIMENSION_NAME)
                                .withStartDate(DateConstants.Yan.START_DATE)
                                .withEndDate(DateConstants.Yan.END_DATE)
                                .withSamplingLevel(FASTER)))
                .apply(table(SITE_SPEED), setParameters(new AnalyticsParameters().withDimensions(SITE_SPEED_DIMENSION_NAME)))
                .apply(table(SHARE_SERVICES), setParameters(
                        new AnalyticsParameters()
                                .withIds(SHARE_SERVICES_COUNTER)
                                .withDimensions(SHARE_SERVICES_DIMENSION_NAME)
                                .withSamplingLevel(HIGHER_PRECISION)))
                .apply(table(EXTERNAL_LINKS), setParameters(new AnalyticsParameters().withDimensions(EXTERNAL_LINKS_DIMENSION_NAME)))
                .apply(table(DOWNLOADS), setParameters(new AnalyticsParameters().withDimensions(DOWNLOADS_DIMENSION_NAME)))
                .apply(table(USER_PARAM), setParameters(
                        new AnalyticsParameters()
                                .withIds(USER_PARAM_COUNTER)
                                .withDimensions(USER_PARAM_DIMENSION_NAME)))
                .apply(offlineCalls(), setParameters(
                        new AnalyticsParameters()
                                .withIds(COUNTER_OFFLINE_CALLS)
                                .withSamplingLevel(HIGHER_PRECISION)
                                .withStartDate(START_DATE_OFFLINE_CALLS)
                                .withEndDate(END_DATE_OFFLINE_CALLS)))
                .apply(publishers(), setParameters(
                        new AnalyticsParameters()
                                .withIds(EUROPA_PLUS)
                                .withSamplingLevel(HIGHER_PRECISION)
                                .withStartDate(START_DATE_PUBLISHERS)
                                .withEndDate(END_DATE_PUBLISHERS)))
                .apply(vacuum(), setParameters(
                        new AnalyticsParameters()
                                .withIds(YANDEX_EATS_ON_MAPS)
                                .withSamplingLevel(HIGHER_PRECISION)
                                .withStartDate(DateConstants.Vacuum.START_DATE)
                                .withEndDate(DateConstants.Vacuum.END_DATE)))
                .apply(recommendationWidget(), setParameters(
                        new AnalyticsParameters()
                                .withIds(YANDEX_WEATHER)
                                .withSamplingLevel(FASTER)
                                .withStartDate(DateConstants.RecommendationWidget.START_DATE)
                                .withEndDate(DateConstants.RecommendationWidget.END_DATE)))
                .apply(cdp(), setParameters(
                        new AnalyticsParameters()
                                .withIds(TEST_CDP)
                                .withSamplingLevel(HIGHER_PRECISION)
                                .withStartDate(DateConstants.Cdp.START_DATE)
                                .withEndDate(DateConstants.Cdp.END_DATE)))
                .apply(crossDeviceAttribution(), setParameters(
                        new AnalyticsParameters()
                                .withIds(YANDEX_METRIKA_2_0)
                                .withSamplingLevel(HIGHER_PRECISION)
                                .withStartDate(DateConstants.CrossDeviceAttribution.START_DATE)
                                .withEndDate(DateConstants.CrossDeviceAttribution.END_DATE)))
                .apply(parameterized(GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(GOAL_ID).and(ecommerce()),
                        setParameters(goalId(ECOMMERCE_TEST)))
                .apply(parameterized(ATTRIBUTION), addAttributions())
                .apply(parameterized(CURRENCY), addCurrencies())
                .apply(parameterized(GROUP), addGroups())
                .apply(parameterized(QUANTILE), setParameters(parametrization().withQuantile(50)))
                .build(identity());
    }

    private AnalyticsV3DataGaGETSchema result;

    @Before
    public void setup() {
        addTestParameter("Метрика", metricName);
        addTestParameter("Остальное", tail.toString());
        result = user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                tail, new CommonReportParameters()
                        .withMetric(metricName));
    }

    @Test
    @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkMetricValues() {
        List<List<Double>> metrics = flatten(user.onResultSteps().getMetrics(result));

        assumeThat("значения метрик присутствуют", metrics, not(empty()));

        assertThat("все значения метрик числа либо null", metrics, iterableHasMetricValues());
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvlAll<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {containsString("adfox"), anything()}
        });
    }
}
