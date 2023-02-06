package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.ecommerce;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.SubTable;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bEcommerceTest;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addAttributions;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Metric.subTable;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.metric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;

/**
 * Created by konkov on 28.09.2015.
 */
public abstract class BaseB2bMetricsEcommerceTest extends BaseB2bEcommerceTest {

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    private static final String DIMENSION_EACTION = "ym:s:productBrand";
    private static final String DIMENSION_EPURCHASE = "ym:s:purchaseID";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<MetricMetaExternal, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getMetricsMeta(metric(table(TableEnum.VISITS).and(ecommerce()))),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withId(COUNTER.get(Counter.ID))
                                .withAccuracy("1"))
                        .append(new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE))))
                .apply(subTable(SubTable.EACTION), setParameters(
                        new TableReportParameters().withDimension(DIMENSION_EACTION)))
                .apply(subTable(SubTable.EPURCHASE), setParameters(
                        new TableReportParameters().withDimension(DIMENSION_EPURCHASE)))
                .apply(subTable(SubTable.NONE), setParameters(
                        new TableReportParameters().withDimension(DIMENSION_EACTION)))
                .apply(metric(parameterized(ParametrizationTypeEnum.GOAL_ID)), setParameters(goalId(COUNTER)))
                //размножим по всем атрибуциям
                .apply(metric(parameterized(ParametrizationTypeEnum.ATTRIBUTION)), addAttributions())
                //размножим по всем валютам
                .apply(metric(parameterized(ParametrizationTypeEnum.CURRENCY)), addCurrencies())
                //размножим по всем периодам группировки
                .apply(metric(parameterized(ParametrizationTypeEnum.GROUP)), addGroups())
                .build(MetricMetaExternal::getDim);
    }
}
