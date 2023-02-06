package ru.yandex.autotests.metrika.tests.ft.report.metrika.namespaces;

import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 16.04.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.NAMESPACES})
@Title("Отчет 'таблица': пространства имен, совместимые")
@RunWith(Parameterized.class)
public class TableNamespacesCompatibleTest {

    private static UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = CounterConstants.NO_DATA_WITH_CLICKS;
    protected static final String START_DATE = "2015-06-20";
    protected static final String END_DATE = "2015-06-21";

    private static final String METRIC_VISITS = "ym:s:avgAge";
    private static final String DIMENSION_VISITS = "ym:s:advEngine";

    private static final String DIMENSION_HITS = "ym:pv:dateTime";

    private static final String METRIC_EXTERNAL_LINKS = "ym:el:users";
    private static final String DIMENSION_EXTERNAL_LINKS = "ym:el:UTMTerm";

    private static final String METRIC_DOWNLOADS = "ym:dl:downloads";
    private static final String DIMENSION_DOWNLOADS = "ym:dl:title";

    private static final String METRIC_SITE_SPEED = "ym:sp:users";
    private static final String DIMENSION_SITE_SPEED = "ym:sp:URLPath";

    private static final String METRIC_SHARE_SERVICES = "ym:sh:shares";

    private static final String METRIC_ADVERTISING = "ym:ad:clicks";
    private static final String DIMENSION_ADVERTISING = "ym:ad:gender";

    private static final String USER_CENTRIC_ATTRIBUTE = "ym:u:gender";

    private static List<String> directClientLogins;

    @Parameterized.Parameter(0)
    public String metricName;

    @Parameterized.Parameter(1)
    public Expression filter;

    @Parameterized.Parameters(name = "metrics: {0}, filter: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {METRIC_VISITS, dimension(DIMENSION_HITS).defined()},
                {METRIC_EXTERNAL_LINKS, dimension(DIMENSION_VISITS).defined()},
                {METRIC_DOWNLOADS, dimension(DIMENSION_VISITS).defined()},
                {METRIC_SITE_SPEED, dimension(DIMENSION_VISITS).defined()},
                {METRIC_SHARE_SERVICES, dimension(DIMENSION_VISITS).defined()},
                {METRIC_ADVERTISING, dimension(DIMENSION_ADVERTISING).defined()},

                {METRIC_VISITS, dimension(USER_CENTRIC_ATTRIBUTE).defined()},
                {METRIC_EXTERNAL_LINKS, dimension(USER_CENTRIC_ATTRIBUTE).defined()},
                {METRIC_DOWNLOADS, dimension(USER_CENTRIC_ATTRIBUTE).defined()},
                {METRIC_SITE_SPEED, dimension(USER_CENTRIC_ATTRIBUTE).defined()},
                {METRIC_SHARE_SERVICES, dimension(USER_CENTRIC_ATTRIBUTE).defined()},
                {METRIC_ADVERTISING, dimension(USER_CENTRIC_ATTRIBUTE).defined()},

                {METRIC_ADVERTISING, dimension(DIMENSION_HITS).defined()},
                {METRIC_ADVERTISING, dimension(DIMENSION_EXTERNAL_LINKS).defined()},
                {METRIC_ADVERTISING, dimension(DIMENSION_DOWNLOADS).defined()},
                {METRIC_ADVERTISING, dimension(DIMENSION_SITE_SPEED).defined()},
                {METRIC_ADVERTISING, dimension(DIMENSION_VISITS).defined()},

                {METRIC_SHARE_SERVICES, dimension(DIMENSION_ADVERTISING).defined()},

                {METRIC_VISITS, dimension(DIMENSION_HITS).defined().and(metric(METRIC_VISITS).notEqualTo(0))},
                {METRIC_EXTERNAL_LINKS, dimension(DIMENSION_VISITS).defined().and(metric(METRIC_EXTERNAL_LINKS).notEqualTo(0))},
                {METRIC_DOWNLOADS, dimension(DIMENSION_VISITS).defined().and(metric(METRIC_DOWNLOADS).notEqualTo(0))},
                {METRIC_SITE_SPEED, dimension(DIMENSION_VISITS).defined().and(metric(METRIC_SITE_SPEED).notEqualTo(0))},
                {METRIC_SHARE_SERVICES, dimension(DIMENSION_VISITS).defined().and(metric(METRIC_SHARE_SERVICES).notEqualTo(0))},

                {METRIC_VISITS, dimension(USER_CENTRIC_ATTRIBUTE).defined().and(metric(METRIC_VISITS).notEqualTo(0))},
                {METRIC_EXTERNAL_LINKS, dimension(USER_CENTRIC_ATTRIBUTE).defined().and(metric(METRIC_EXTERNAL_LINKS).notEqualTo(0))},
                {METRIC_DOWNLOADS, dimension(USER_CENTRIC_ATTRIBUTE).defined().and(metric(METRIC_DOWNLOADS).notEqualTo(0))},
                {METRIC_SITE_SPEED, dimension(USER_CENTRIC_ATTRIBUTE).defined().and(metric(METRIC_SITE_SPEED).notEqualTo(0))},
                {METRIC_SHARE_SERVICES, dimension(USER_CENTRIC_ATTRIBUTE).defined().and(metric(METRIC_SHARE_SERVICES).notEqualTo(0))},
                {METRIC_ADVERTISING, dimension(USER_CENTRIC_ATTRIBUTE).defined().and(metric(METRIC_ADVERTISING).notEqualTo(0))},

                {METRIC_EXTERNAL_LINKS, dimension(DIMENSION_HITS).defined().and(metric(METRIC_EXTERNAL_LINKS).notEqualTo(0))},
                {METRIC_DOWNLOADS, dimension(DIMENSION_HITS).defined().and(metric(METRIC_DOWNLOADS).notEqualTo(0))},
                {METRIC_SITE_SPEED, dimension(DIMENSION_HITS).defined().and(metric(METRIC_SITE_SPEED).notEqualTo(0))},
                {METRIC_SHARE_SERVICES, dimension(DIMENSION_HITS).defined().and(metric(METRIC_SHARE_SERVICES).notEqualTo(0))},

                {METRIC_DOWNLOADS, dimension(DIMENSION_EXTERNAL_LINKS).defined().and(metric(METRIC_DOWNLOADS).notEqualTo(0))},
                {METRIC_SITE_SPEED, dimension(DIMENSION_EXTERNAL_LINKS).defined().and(metric(METRIC_SITE_SPEED).notEqualTo(0))},
                {METRIC_SHARE_SERVICES, dimension(DIMENSION_EXTERNAL_LINKS).defined().and(metric(METRIC_SHARE_SERVICES).notEqualTo(0))},
                {METRIC_SITE_SPEED, dimension(DIMENSION_DOWNLOADS).defined().and(metric(METRIC_SITE_SPEED).notEqualTo(0))},
                {METRIC_SHARE_SERVICES, dimension(DIMENSION_DOWNLOADS).defined().and(metric(METRIC_SHARE_SERVICES).notEqualTo(0))},
                {METRIC_SHARE_SERVICES, dimension(DIMENSION_SITE_SPEED).defined().and(metric(METRIC_SHARE_SERVICES).notEqualTo(0))},
        });
    }

    @BeforeClass
    public static void init() {
        directClientLogins = user.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters()
                        .withCounters(COUNTER.get(ID))
                        .withDate1(START_DATE)
                        .withDate2(END_DATE),
                ulogin(COUNTER.get(U_LOGIN)));
    }

    @Test
    public void compatibilityTest() {
        user.onReportSteps().getTableReportAndExpectSuccess(new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withMetric(metricName)
                .withFilters(filter.build())
                .withDirectClientLogins(directClientLogins));
    }
}
