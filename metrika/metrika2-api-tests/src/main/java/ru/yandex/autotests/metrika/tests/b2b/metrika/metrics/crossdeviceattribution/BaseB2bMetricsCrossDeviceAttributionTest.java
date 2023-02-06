package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.crossdeviceattribution;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bCrossDeviceAttributionTest;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;

import java.util.Collection;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

public abstract class BaseB2bMetricsCrossDeviceAttributionTest extends BaseB2bCrossDeviceAttributionTest {

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    private static final String DIMENSION_VISITS = "ym:s:browser";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<MetricMetaExternal, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getMetricsMeta(metric(table(TableEnum.VISITS).and(crossDeviceAttribution()))),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withId(COUNTER.get(Counter.ID))
                                .withDimension(DIMENSION_VISITS)
                                .withAccuracy("0.1"))
                        .append(new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)
                                .withDimension(DIMENSION_VISITS)
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
