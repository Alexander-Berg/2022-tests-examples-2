package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
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
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.BIG_COUNTER;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

/**
 * Created by sourx on 08/02/2018.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Format.CSV,
        Requirements.Story.Report.Format.XLSX})
@Title("B2B - Экспорт отчета в excel по избранным измерениям")
@RunWith(Parameterized.class)
public class B2bExportDimensionsTest extends BaseB2bExportTest {
    private static Counter COUNTER = BIG_COUNTER;

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String METRIC_HITS = "ym:pv:pageviews";
    public static final String METRIC_VISITS = "ym:s:goal<goal_id><currency>revenue";
    public static final String METRIC_EXTERNAL_LINK = "ym:el:links";
    public static final String METRIC_DOWNLOAD = "ym:dl:blockedPercentage";
    public static final String METRIC_SHARE_SERVICES = "ym:sh:users";
    public static final String METRIC_SITE_SPEED = "ym:sp:qTime<quantile>TimingsResponse";
    public static final String METRIC_USER_PARAMS = "ym:up:params";
    public static final String METRIC_ADVERISING = "ym:ad:goal<goal_id><currency>CPA";

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps()
                        .getDimensions(favorite()),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                        .withDate1("10daysAgo")
                                        .withDate2("10daysAgo")
                                        .withId(COUNTER.get(Counter.ID))
                                        .withAccuracy("1"),
                                goalId(COUNTER.get(Counter.GOAL_ID)))
                        .append(new ComparisonReportParameters()
                                .withDate1_a("12daysAgo")
                                .withDate2_a("11daysAgo")
                                .withDate1_b("11daysAgo")
                                .withDate2_b("10daysAgo")
                                .withAccuracy("1"))))
                .apply(table(TableEnum.ADVERTISING), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_ADVERISING)
                        .withDirectClientLogins(userOnTest.onManagementSteps().onClientSteps()
                                .getClientLogins(new ClientsParameters()
                                                .withCounters(COUNTER.get(ID))
                                                .withDate1("10daysAgo")
                                                .withDate2("10daysAgo"),
                                        ulogin(COUNTER.get(U_LOGIN))))))
                .apply(table(TableEnum.HITS), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_HITS)))
                .apply(table(TableEnum.VISITS), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_VISITS)))
                .apply(table(TableEnum.SHARE_SERVICES), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_SHARE_SERVICES)))
                .apply(table(TableEnum.DOWNLOADS), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_DOWNLOAD)))
                .apply(table(TableEnum.EXTERNAL_LINKS), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_EXTERNAL_LINK)))
                .apply(table(TableEnum.SITE_SPEED), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_SITE_SPEED)))
                .apply(table(TableEnum.USER_PARAM), setParameters(new CommonReportParameters()
                        .withMetric(METRIC_USER_PARAMS)))
                .build(identity());
    }

    @Before
    public void setup() {
        requestType = TABLE;
        reportParameters = tail.append(new TableReportParameters()
                .withDimension(dimensionName));
    }
}
