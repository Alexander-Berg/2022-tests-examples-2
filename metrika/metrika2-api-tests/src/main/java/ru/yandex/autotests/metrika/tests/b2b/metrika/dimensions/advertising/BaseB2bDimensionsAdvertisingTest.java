package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.advertising;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bAdvertisingTest;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addAttributions;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;

/**
 * Created by konkov on 30.07.2015.
 */
public abstract class BaseB2bDimensionsAdvertisingTest extends BaseB2bAdvertisingTest {

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String METRIC_NAME = "ym:ad:clicks";

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection createParameters() {

        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getDimensions(table(TableEnum.ADVERTISING)),
                FreeFormParameters::makeParameters)
                //общее
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withId(COUNTER.get(Counter.ID))
                                .withMetric(METRIC_NAME)
                                .withIncludeUndefined(true)
                                .withDirectClientLogins(userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                                        new ClientsParameters()
                                                .withCounters(COUNTER.get(Counter.ID))
                                                .withDate1(START_DATE)
                                                .withDate2(END_DATE),
                                        ulogin(COUNTER.get(Counter.U_LOGIN)))))
                        .append(new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE))))
                .apply(matches(anyOf(
                        containsString("DirectBanner"),
                        containsString("directBanner"),
                        containsString("DirectPhraseOrCond"),
                        containsString("DirectPlatform"))), setParameters(makeParameters()
                        .append(
                                new TableReportParameters()
                                        .withAccuracy("low")
                                        .withDate1("2016-03-01")
                                        .withDate2("2016-03-01"))
                        .append(new ComparisonReportParameters()
                                .withAccuracy("low")
                                .withDate1_a("2016-03-01")
                                .withDate2_a("2016-03-01")
                                .withDate1_b("2016-03-01")
                                .withDate2_b("2016-03-01"))))
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(ParametrizationTypeEnum.EXPERIMENT), setParameters(experimentId(COUNTER)))
                //размножим по всем атрибуциям
                .apply(parameterized(ParametrizationTypeEnum.ATTRIBUTION), addAttributions())
                //размножим по всем валютам
                .apply(parameterized(ParametrizationTypeEnum.CURRENCY), addCurrencies())
                //размножим по всем периодам группировки
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .build(identity());
    }

    @IgnoreParameters.Tag(name = "METR-26049")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:ad:ASN"), anything()}
        });
    }
}
