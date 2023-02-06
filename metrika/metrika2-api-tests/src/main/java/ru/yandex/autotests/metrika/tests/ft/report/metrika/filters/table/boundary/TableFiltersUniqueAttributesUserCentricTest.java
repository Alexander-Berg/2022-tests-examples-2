package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 17.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC
})
@Title("Отчет 'таблица': фильтры, не более 20-ти уникальных метрик и измерений в условиях, user-centric")
public class TableFiltersUniqueAttributesUserCentricTest {

    private static final int ATTRIBUTES_LIMIT = 20;
    private static final Counter COUNTER = CounterConstants.NO_DATA;

    private static UserSteps user;

    private static Collection<String> metrics;

    private static final List<String> DIMENSIONS = asList(
            "ym:s:startURLPath",
            "ym:s:startURLPathLevel1",
            "ym:s:startURLPathLevel2",
            "ym:s:startURLPathLevel3",
            "ym:s:startURLPathLevel4",
            "ym:s:startURLPathLevel5",
            "ym:s:endURLPath",
            "ym:s:endURLPathLevel1",
            "ym:s:endURLPathLevel2",
            "ym:s:endURLPathLevel3",
            "ym:s:endURLPathLevel4",
            "ym:s:endURLPathLevel5",
            "ym:s:visitYear",
            "ym:s:visitMonth",
            "ym:s:visitDayOfMonth",
            "ym:s:firstVisitYear",
            "ym:s:firstVisitMonth",
            "ym:s:firstVisitDayOfMonth",
            "ym:s:totalVisits",
            "ym:s:pageViews",
            "ym:s:visitDuration",
            "ym:s:visits"
    );

    private static final String USER_CENTRIC_ATTRIBUTE = "ym:u:gender";
    private static final String USER_ID = "ym:u:userID";

    private TableReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
        metrics = user.onMetadataSteps().getMetrics(
                table(VISITS).and(nonParameterized())
                        .and(matches(not(equalTo("ym:s:affinityIndexInterests")))).and(matches(not(equalTo("ym:s:affinityIndexInterests2")))));

        assumeThat("для теста доступен список метрик", metrics,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));

        assumeThat("для теста доступен список измерений", DIMENSIONS,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters();
        reportParameters.setId(COUNTER.get(ID));
        reportParameters.setMetric(metrics.stream().findFirst().get());
    }

    @Test
    public void maximumMetricsInFilter() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterExpressionWithAttributes(metrics, ATTRIBUTES_LIMIT - 1)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumMetricsInFilter() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterExpressionWithAttributes(metrics, ATTRIBUTES_LIMIT)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getTableReportAndExpectError(
                ReportError.TOO_MANY_ATTRIBUTES_IN_FILTERS, reportParameters);
    }

    @Test
    public void maximumDimensionsInFilter() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterExpressionWithAttributes(DIMENSIONS, ATTRIBUTES_LIMIT - 1)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumDimensionsInFilter() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterExpressionWithAttributes(DIMENSIONS, ATTRIBUTES_LIMIT)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getTableReportAndExpectError(
                ReportError.TOO_MANY_ATTRIBUTES_IN_FILTERS, reportParameters);
    }

}
