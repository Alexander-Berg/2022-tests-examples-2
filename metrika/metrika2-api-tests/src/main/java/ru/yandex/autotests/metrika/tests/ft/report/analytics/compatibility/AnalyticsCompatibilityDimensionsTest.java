package ru.yandex.autotests.metrika.tests.ft.report.analytics.compatibility;

import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.AnalyticsV3DataGaGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;
import static ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum.FASTER;
import static ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum.HIGHER_PRECISION;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.IKEA_VSEM;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.ATTRIBUTION;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.CURRENCY;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GROUP;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.ADVERTISING;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.DOWNLOADS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.EXPENSES_VISITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.EXTERNAL_LINKS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.HITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.SHARE_SERVICES;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.SITE_SPEED;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.USER_PARAM;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilled;
import static ru.yandex.autotests.metrika.matchers.NoDuplicatesMatcher.hasNoDuplicates;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;

/**
 * Created by sourx on 03.08.16.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Отчет 'google analytics': измерения (совместимость)")
@RunWith(Parameterized.class)
public class AnalyticsCompatibilityDimensionsTest {
    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = IKEA_VSEM;
    private static final Counter USER_PARAM_COUNTER = Counters.YANDEX_METRIKA_2_0;
    private static final String START_DATE = "2015-06-20";
    private static final String END_DATE = "2015-06-21";

    private static final String VISIT_METRIC = "ym:s:visits";
    private static final String HIT_METRIC = "ym:pv:pageviews";
    private static final String SHARE_SERVICES_METRIC = "ym:sh:shares";
    private static final String SITE_SPEED_METRIC = "ym:sp:pageviews";
    private static final String EXTERNAL_LINKS_METRIC = "ym:el:links";
    private static final String DOWNLOADS_METRIC = "ym:dl:downloads";
    private static final String USER_PARAM_METRIC = "ym:up:params";

    @Parameter()
    public String dimensionName;

    @Parameter(value = 1)
    public FreeFormParameters tail;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                user.onMetadataSteps().getDimensions((table(ADVERTISING).or(table(EXPENSES_VISITS))).negate()),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(
                        new AnalyticsParameters()
                                .withIds(COUNTER.get(ID))
                                .withStartDate(START_DATE)
                                .withEndDate(END_DATE)))
                .apply(table(VISITS), setParameters(
                        new AnalyticsParameters().withMetrics(VISIT_METRIC)))
                .apply(table(HITS), setParameters(
                        new AnalyticsParameters().withMetrics(HIT_METRIC)))
                .apply(table(SHARE_SERVICES), setParameters(
                        new AnalyticsParameters().withMetrics(SHARE_SERVICES_METRIC)))
                .apply(table(SITE_SPEED), setParameters(
                        new AnalyticsParameters().withMetrics(SITE_SPEED_METRIC)))
                .apply(table(EXTERNAL_LINKS), setParameters(
                        new AnalyticsParameters().withMetrics(EXTERNAL_LINKS_METRIC)))
                .apply(table(DOWNLOADS), setParameters(
                        new AnalyticsParameters().withMetrics(DOWNLOADS_METRIC)))
                .apply(table(USER_PARAM), setParameters(
                        new AnalyticsParameters()
                                .withIds(USER_PARAM_COUNTER)
                                .withMetrics(USER_PARAM_METRIC)))
                .apply(ecommerce(), setParameters(
                        new AnalyticsParameters()
                                .withIds(Counters.ECOMMERCE_TEST)
                                .withStartDate(DateConstants.Ecommerce.START_DATE)
                                .withEndDate(DateConstants.Ecommerce.END_DATE)
                                .withSamplingLevel(HIGHER_PRECISION)))
                .apply(yan(), setParameters(
                        new AnalyticsParameters()
                                .withIds(Counters.YANDEX_NEWS)
                                .withStartDate(DateConstants.Yan.START_DATE)
                                .withEndDate(DateConstants.Yan.END_DATE)
                                .withSamplingLevel(FASTER)))
                .apply(parameterized(GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(GOAL_ID).and(ecommerce()),
                        setParameters(goalId(Counters.ECOMMERCE_TEST)))
                .apply(parameterized(ParametrizationTypeEnum.EXPERIMENT), setParameters(aggregate(
                        new CommonReportParameters().withId(KVAZI_KAZINO), experimentId(KVAZI_KAZINO))))
                .apply(parameterized(ATTRIBUTION), setParameters(
                        new ParametrizationParameters().withAttribution(LAST)))
                .apply(parameterized(CURRENCY), addCurrencies())
                .apply(parameterized(GROUP), addGroups())
                .apply(matches(equalTo("ym:s:networkType")), setParameters(
                        new AnalyticsParameters()
                                .withStartDate("2017-01-20")
                                .withEndDate("2017-01-21")))
                .build(identity());
    }

    private AnalyticsV3DataGaGETSchema result;

    @Before
    public void setup() {
        addTestParameter("Измерение", dimensionName);

        result = user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                new TableReportParameters().withDimension(dimensionName),
                tail);
    }

    @Test
    public void checkDimensionValuesValidityAndUniqueness() {
        List<List<String>> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("значения измерений не содержат пустых и некорректных значений, а также дубликатов", dimensions,
                matchEvery(everyItem(iterableHasDimensionValuesFilled()), hasNoDuplicates()));
    }
}
