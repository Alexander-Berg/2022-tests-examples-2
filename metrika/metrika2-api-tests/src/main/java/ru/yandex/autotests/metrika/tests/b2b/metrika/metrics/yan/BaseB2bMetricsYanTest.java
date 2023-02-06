package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.yan;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bYanTest;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addAttributions;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.metric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;

public abstract class BaseB2bMetricsYanTest extends BaseB2bYanTest {

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    private static final String DIMENSION_YAN = "ym:s:yanPageID";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<MetricMetaExternal, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getMetricsMeta(metric(table(TableEnum.VISITS).and(yan()))),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withId(COUNTER.get(Counter.ID))
                                .withDimension(DIMENSION_YAN)
                                .withAccuracy("0.1"))
                        .append(new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)
                                .withDimension(DIMENSION_YAN)
                                .withAccuracy("0.1")
                        )))
                //размножим по всем атрибуциям
                .apply(metric(parameterized(ParametrizationTypeEnum.ATTRIBUTION)), addAttributions())
                //размножим по всем валютам
                .apply(metric(parameterized(ParametrizationTypeEnum.CURRENCY)), addCurrencies())
                //размножим по всем периодам группировки
                .apply(metric(parameterized(ParametrizationTypeEnum.GROUP)), addGroups())
                .build(MetricMetaExternal::getDim);
    }

}
