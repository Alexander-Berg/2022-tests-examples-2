package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.advertising;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bAdvertisingTest;

import static java.util.function.Function.identity;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addAttributions;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;

/**
 * Created by konkov on 30.07.2015.
 */
public abstract class BaseB2bMetricsAdvertisingTest extends BaseB2bAdvertisingTest {

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String DIMENSION_NAME = "ym:ad:regionCountry";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getMetrics(table(TableEnum.ADVERTISING)),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withId(COUNTER)
                                .withDimension(DIMENSION_NAME)
                                .withIncludeUndefined(true)
                                .withDirectClientLogins(userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                                        new ClientsParameters()
                                                .withCounters(COUNTER.get(ID))
                                                .withDate1(START_DATE)
                                                .withDate2(END_DATE),
                                        ulogin(COUNTER.get(U_LOGIN)))))
                        .append(new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE))))
                //подставим goal_id
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(COUNTER)))
                //размножим по всем атрибуциям
                .apply(parameterized(ParametrizationTypeEnum.ATTRIBUTION), addAttributions())
                //размножим по всем валютам
                .apply(parameterized(ParametrizationTypeEnum.CURRENCY), addCurrencies())
                //размножим по всем периодам группировки
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .build(identity());
    }
}
