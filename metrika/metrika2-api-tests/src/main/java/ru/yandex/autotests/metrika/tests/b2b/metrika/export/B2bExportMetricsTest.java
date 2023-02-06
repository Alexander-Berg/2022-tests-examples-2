package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MARKET;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

/**
 * Created by sourx on 07/02/2018.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Format.CSV,
        Requirements.Story.Report.Format.XLSX})
@Title("B2B - Экспорт отчета в excel по избранным метрикам")
@RunWith(Parameterized.class)
public class B2bExportMetricsTest extends BaseB2bExportTest {
    private static Counter COUNTER = YANDEX_MARKET;

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String DIMENSION_HITS = "ym:pv:regionCountry";
    public static final String DIMENSION_VISITS = "ym:s:regionCountry";
    public static final String DIMENSION_EXTERNAL_LINK = "ym:el:gender";
    public static final String DIMENSION_DOWNLOAD = "ym:dl:datePeriod<group>";
    public static final String DIMENSION_SHARE_SERVICES = "ym:sh:datePeriod<group>";
    public static final String DIMENSION_SITE_SPEED = "ym:sp:gender";
    public static final String DIMENSION_USER_PARAMS = "ym:up:paramsLevel1";
    public static final String DIMENSION_ADVERISING = "ym:ad:<attribution>DirectBanner";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps()
                        .getMetrics(favorite()),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1("10daysAgo")
                                .withDate2("10daysAgo")
                                .withId(COUNTER.get(Counter.ID))
                                .withAccuracy("1"))
                        .append(new ComparisonReportParameters()
                                .withDate1_a("12daysAgo")
                                .withDate2_a("11daysAgo")
                                .withDate1_b("11daysAgo")
                                .withDate2_b("10daysAgo")
                                .withAccuracy("1"))))
                .apply(table(TableEnum.ADVERTISING), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_ADVERISING)
                        .withDirectClientLogins(userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                                new ClientsParameters()
                                        .withCounters(COUNTER.get(ID))
                                        .withDate1("10daysAgo")
                                        .withDate2("10daysAgo"),
                                ulogin(COUNTER.get(U_LOGIN))))))
                .apply(table(TableEnum.HITS), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_HITS)))
                .apply(table(TableEnum.VISITS), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_VISITS)))
                .apply(table(TableEnum.SHARE_SERVICES), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_SHARE_SERVICES)))
                .apply(table(TableEnum.DOWNLOADS), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_DOWNLOAD)))
                .apply(table(TableEnum.EXTERNAL_LINKS), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_EXTERNAL_LINK)))
                .apply(table(TableEnum.SITE_SPEED), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_SITE_SPEED)))
                .apply(table(TableEnum.USER_PARAM), setParameters(new CommonReportParameters()
                        .withDimension(DIMENSION_USER_PARAMS)))
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(ParametrizationTypeEnum.ATTRIBUTION), addAttributions())
                .apply(parameterized(ParametrizationTypeEnum.CURRENCY), setParameters(currency("643")))
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .apply(
                        matches(anyOf(
                                equalTo("ym:s:sumParams"),
                                equalTo("ym:s:avgParams"))),
                        setParameters(new TableReportParameters().withId(SENDFLOWERS_RU)))
                .build(identity());
    }

    @Before
    public void setup() {
        requestType = TABLE;
        reportParameters = tail.append(new TableReportParameters()
                .withMetric(metricName));
    }
}
