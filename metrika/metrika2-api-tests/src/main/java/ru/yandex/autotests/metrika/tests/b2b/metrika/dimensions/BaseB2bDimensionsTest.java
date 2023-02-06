package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addAttributions;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.interest2Name;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;


/**
 * Created by omaz on 05.12.2014.
 */
public abstract class BaseB2bDimensionsTest extends BaseB2bTest {

    protected static final Counter COUNTER = SENDFLOWERS_RU;

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String METRIC_HITS = "ym:pv:pageviews";
    public static final String METRIC_VISITS = "ym:s:visits";

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getDimensions(
                        table(TableEnum.HITS).or(table(TableEnum.VISITS))
                                .and(ecommerce().negate()).and(yan().negate()).and(interest2Name().negate())
                ),
                FreeFormParameters::makeParameters)
                //общее
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1("10daysAgo")
                                .withDate2("10daysAgo")
                                .withId(COUNTER.get(Counter.ID)))
                        .append(new ComparisonReportParameters()
                                .withDate1_a("12daysAgo")
                                .withDate2_a("11daysAgo")
                                .withDate1_b("11daysAgo")
                                .withDate2_b("10daysAgo"))))
                .apply(matches(anyOf(
                        containsString("DirectBanner"),
                        containsString("directBanner"),
                        containsString("DirectPhraseOrCond"),
                        containsString("DirectPlatform"))),
                        setParameters(makeParameters()
                                .append(
                                        new TableReportParameters()
                                                .withAccuracy("0.1")
                                                .withDate1("2018-09-23")
                                                .withDate2("2018-09-24"))
                                .append(new ComparisonReportParameters()
                                        .withAccuracy("low")
                                        .withDate1_a("2018-09-23")
                                        .withDate2_a("2018-09-23")
                                        .withDate1_b("2018-09-24")
                                        .withDate2_b("2018-09-24"))))
                .apply(table(TableEnum.HITS), setParameters(new CommonReportParameters().withMetric(METRIC_HITS)))
                .apply(table(TableEnum.VISITS), setParameters(new CommonReportParameters().withMetric(METRIC_VISITS)))
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(ParametrizationTypeEnum.EXPERIMENT), setParameters(aggregate(
                        new CommonReportParameters().withId(KVAZI_KAZINO), experimentId(KVAZI_KAZINO))))
                //размножим по всем атрибуциям
                .apply(parameterized(ParametrizationTypeEnum.ATTRIBUTION), addAttributions())
                //размножим по всем валютам
                .apply(parameterized(ParametrizationTypeEnum.CURRENCY), addCurrencies())
                //размножим по всем периодам группировки
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .build(identity());
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }

    @IgnoreParameters.Tag(name = "METRIQA-3319")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {containsString("SearchPhrase"), anything()}
        });
    }
}
