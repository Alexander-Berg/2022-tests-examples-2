package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import java.util.Collection;

import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

/**
 * Created by omaz on 05.12.2014.
 */
public abstract class BaseB2bMetricsTest extends BaseB2bTest {

    protected static final Counter COUNTER = YANDEX_MARKET;

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String DIMENSION_HITS = "ym:pv:regionCountry";
    public static final String DIMENSION_VISITS = "ym:s:regionCountry";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection<?> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps()
                        .getMetrics(table(TableEnum.HITS).or(table(TableEnum.VISITS)).and(ecommerce().negate())
                                .and(yan().negate()).and(crossDeviceAttribution().negate())),
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
                .apply(vacuum(), setParameters(
                        new ComparisonReportParameters()
                                .withId(YANDEX_EATS_ON_MAPS)
                                .withAccuracy("1")
                                .withDate1_a(DateConstants.Vacuum.START_DATE)
                                .withDate2_a(DateConstants.Vacuum.END_DATE)
                                .withDate1_b(DateConstants.Vacuum.START_DATE)
                                .withDate2_b(DateConstants.Vacuum.END_DATE)))
                .apply(cdp(), setParameters(
                        new ComparisonReportParameters()
                                .withId(TEST_CDP)
                                .withAccuracy("1")
                                .withDate1_a(DateConstants.Cdp.START_DATE)
                                .withDate2_a(DateConstants.Cdp.END_DATE)
                                .withDate1_b(DateConstants.Cdp.START_DATE)
                                .withDate2_b(DateConstants.Cdp.END_DATE)))
                .apply(table(TableEnum.HITS), setParameters(new CommonReportParameters().withDimension(DIMENSION_HITS)))
                .apply(table(TableEnum.VISITS), setParameters(new CommonReportParameters().withDimension(DIMENSION_VISITS)))
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(COUNTER)))
                //размножим по всем атрибуциям
                .apply(parameterized(ParametrizationTypeEnum.ATTRIBUTION), addAttributions())
                //размножим по всем валютам
                .apply(parameterized(ParametrizationTypeEnum.CURRENCY), addCurrencies())
                //размножим по всем периодам группировки
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .apply(
                        matches(anyOf(
                                equalTo("ym:s:sumParams"),
                                equalTo("ym:s:avgParams"))),
                        setParameters(new TableReportParameters().withId(SENDFLOWERS_RU)))
                .build(identity());
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
