package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.experiments;

import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ReferenceRowIdParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static jersey.repackaged.com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.EXPERIMENT_ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.REFERENCE_ROW_ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DIRECT;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CDP;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.DRILLDOWN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;


@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Type.DRILLDOWN, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B экспериментов - метрики по просмотрам и визитам, методы TABLE/DRILLDOWN")
public class MetricsB2bExperimentsABTest extends BaseB2bTest {
    public static final String DIMENSION_EXPERIMENTS = "ym:s:experimentAB<experiment_ab>";

    @Parameterized.Parameter
    public RequestType request;

    @Parameterized.Parameter(1)
    public String metricName;

    @Parameterized.Parameter(2)
    public FreeFormParameters tail;

    @Parameterized.Parameters(name = "Запрос {0} Метрика {1}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder().vectorValues(of(DRILLDOWN), of(TABLE))
                .vectorValues(MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                        userOnTest.onMetadataSteps().getMetrics(
                                table(TableEnum.VISITS)
                                        .and(offlineCalls().negate())
                                        .and(ecommerce().negate())
                                        .and(publishers().negate())
                                        .and(yan().negate())
                                        .and(vacuum().negate())
                                        .and(recommendationWidget().negate())
                                        .and(crossDeviceAttribution().negate())),
                        FreeFormParameters::makeParameters)
                        .apply(any(), setParameters(makeParameters()
                                .append(new ExperimentParameters().withExperimentId(String.valueOf(DIRECT.get(EXPERIMENT_ID))))
                                .append(new ReferenceRowIdParameters().withReferenceRowId(DIRECT.get(REFERENCE_ROW_ID)))
                                .append(new TableReportParameters()
                                        .withDate1("10daysAgo")
                                        .withDate2("10daysAgo")
                                        .withId(DIRECT.get(Counter.ID))
                                        .withDimensions(Collections.singleton(DIMENSION_EXPERIMENTS)))))
                        .apply(cdp(), setParameters(
                                makeParameters()
                                        .append(new ExperimentParameters().withExperimentId(String.valueOf(TEST_CDP.get(EXPERIMENT_ID))))
                                        .append(new ReferenceRowIdParameters().withReferenceRowId(TEST_CDP.get(REFERENCE_ROW_ID)))
                                        .append(new TableReportParameters()
                                                .withId(TEST_CDP.get(Counter.ID))
                                                .withAccuracy("1")
                                                .withDate1(DateConstants.Cdp.START_DATE)
                                                .withDate2(DateConstants.Cdp.END_DATE)
                                                .withDimensions(Collections.singleton(DIMENSION_EXPERIMENTS)))))
                        .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(DIRECT)))
                        .apply(parameterized(ParametrizationTypeEnum.EXPERIMENT), setParameters(experimentId(DIRECT)))
                        .buildVectorValues(identity())).build();
    }


    @Before
    public void before() {
        requestType = request;
        reportParameters = tail
                .append(new CommonReportParameters().withMetric(metricName));
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {anything(), equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {anything(), equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()},
                {anything(), equalTo("ym:s:pvlAll1Window"), anything()},
                {anything(), equalTo("ym:s:pvlAll3Window"), anything()},
                {anything(), equalTo("ym:s:pvlAll7Window"), anything()},
                {anything(), equalTo("ym:s:pvlAll<offline_window>Window"), anything()},
                {anything(), equalTo("ym:s:avgParams"), anything()},
                {anything(), equalTo("ym:s:sumParams"), anything()}
        });
    }
}
