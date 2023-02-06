package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.function.Function;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.function.Function.identity;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.BY_TIME;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.CURRENCY;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum.HOUR;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

/**
 * Created by sourx on 06.06.16.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Format.CSV,
        Requirements.Story.Report.Format.CSV})
@Title("B2B - Экспорт ByTime отчета в excel")
@RunWith(Parameterized.class)
public class B2bExportByTimeTest extends BaseB2bExportTest {
    private static final Counter COUNTER = SENDFLOWERS_RU;
    private static final String START_DATE = "yesterday";
    private static final String END_DATE = "yesterday";

    private static final String VISIT_DIMENSION_NAME = "ym:s:gender";
    private static final String HIT_DIMENSION_NAME = "ym:pv:gender";
    private static final String SHARE_SERVICES_DIMENSION_NAME = "ym:sh:date";
    private static final String SITE_SPEED_DIMENSION_NAME = "ym:sp:gender";
    private static final String EXTERNAL_LINKS_DIMENSION_NAME = "ym:el:gender";
    private static final String DOWNLOADS_DIMENSION_NAME = "ym:dl:gender";
    private static final String ADVERTISING_DIMENSION_NAME = "ym:ad:gender";
    private static final String USER_PARAM_DIMENSION_NAME = "ym:up:paramsLevel1";

    private static final List<List<String>> ROW_IDS = of(singletonList("male"), emptyList());
    private static final List<List<String>> USER_PARAM_ROW_IDS = of(singletonList("ddd"), emptyList());
    private static final List<List<String>> SHARE_SERVICES_ROW_IDS = of(singletonList("2016-01-01"), emptyList());

    @Parameter()
    public String metric;

    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getMetrics(favorite()),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(
                        new BytimeReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withDimension(VISIT_DIMENSION_NAME)
                                .withId(COUNTER)
                                .withGroup(HOUR)
                                .withRowIds(ROW_IDS)
                                .withAccuracy("0.1")))
                .apply(table(HITS), setParameters(new BytimeReportParameters()
                        .withDimension(HIT_DIMENSION_NAME)))
                .apply(table(VISITS), setParameters(new BytimeReportParameters()
                        .withDimension(VISIT_DIMENSION_NAME)))
                .apply(table(SITE_SPEED), setParameters(new BytimeReportParameters()
                        .withDimension(SITE_SPEED_DIMENSION_NAME)))
                .apply(table(SHARE_SERVICES), setParameters(
                        new BytimeReportParameters()
                                .withDimension(SHARE_SERVICES_DIMENSION_NAME)
                                .withRowIds(SHARE_SERVICES_ROW_IDS)))
                .apply(table(EXTERNAL_LINKS), setParameters(new BytimeReportParameters()
                        .withDimension(EXTERNAL_LINKS_DIMENSION_NAME)))
                .apply(table(DOWNLOADS), setParameters(new BytimeReportParameters()
                        .withDimension(DOWNLOADS_DIMENSION_NAME)))
                .apply(table(USER_PARAM), setParameters(new BytimeReportParameters()
                        .withDimension(USER_PARAM_DIMENSION_NAME)
                        .withRowIds(USER_PARAM_ROW_IDS)))
                .apply(table(ADVERTISING), setParameters(
                        new BytimeReportParameters()
                                .withDimension(ADVERTISING_DIMENSION_NAME)
                                .withDirectClientIds(
                                        userOnTest.onManagementSteps().onClientSteps().getClientIds(
                                                new ClientsParameters()
                                                        .withCounters(COUNTER.get(ID))
                                                        .withDate1(START_DATE)
                                                        .withDate2(END_DATE),
                                                ulogin(COUNTER.get(U_LOGIN))))))
                .apply(parameterized(GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(CURRENCY), setParameters(
                        currency(userOnTest.onManagementSteps()
                                .onCountersSteps().getCounterInfo(COUNTER.get(ID)).getCurrency().toString())))
                .build(identity());
    }

    @Before
    public void setup() {
        requestType = BY_TIME;
        reportParameters = tail.append(new BytimeReportParameters()
                .withMetric(metric));
    }
}
