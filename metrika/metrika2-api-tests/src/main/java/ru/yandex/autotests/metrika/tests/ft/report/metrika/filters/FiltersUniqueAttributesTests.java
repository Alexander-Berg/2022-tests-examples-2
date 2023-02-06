package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.function.Function;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет: фильтры, не более 20-ти уникальных измерений/метрик в условиях")
@RunWith(Parameterized.class)
public class FiltersUniqueAttributesTests {
    private static final int ATTRIBUTES_LIMIT = 20;

    private static final Counter COUNTER = CounterConstants.NO_DATA;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

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

    private CommonReportParameters reportParameters;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public Function<String, IFormParameters> filter;

    @Parameterized.Parameter(2)
    public Collection<String> attribute;

    @Parameterized.Parameters(name = "Отчет {0}. Фильтры: не более 20/более 20 измерений или метрик")
    public static Collection createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(CombinatorialBuilder.builder()
                        .vectorValues(
                                of(TABLE, filterParameters()),
                                of(DRILLDOWN, filterParameters()),
                                of(BY_TIME, filterParameters()),
                                of(COMPARISON, filterParameters_a()),
                                of(COMPARISON, filterParameters_b()),
                                of(COMPARISON_DRILLDOWN, filterParameters_a()),
                                of(COMPARISON_DRILLDOWN, filterParameters_b()))
                        .vectorValue(of(DIMENSIONS))
                        .build())
                .addAll(CombinatorialBuilder.builder()
                        .vectorValues(
                                of(DRILLDOWN, filterParameters()),
                                of(BY_TIME, filterParameters()),
                                of(TABLE, filterParameters()))
                        .vectorValue(of(user.onMetadataSteps().getMetrics(table(VISITS)
                                .and(nonParameterized()).and(matches(not(equalTo("ym:s:affinityIndexInterests"))))
                                .and(matches(not(equalTo("ym:s:affinityIndexInterests2")))))))
                        .build())
                .build();
    }

    @Before
    public void setup() {
        assumeThat("для теста доступен список измерений/метрик", attribute,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));

        reportParameters = new CommonReportParameters()
                .withId(COUNTER.getId())
                .withMetric(user.onMetadataSteps().getMetrics(table(VISITS)
                        .and(nonParameterized()).and(matches(not(equalTo("ym:s:affinityIndexInterests"))))
                        .and(matches(not(equalTo("ym:s:affinityIndexInterests2"))))).stream().findFirst().get());
    }

    @Test
    public void maximumAttributesInFilter() {
        user.onReportSteps().getReportAndExpectSuccess(requestType, reportParameters,
                filter.apply(user.onFilterSteps().getFilterWithAttributes(attribute, ATTRIBUTES_LIMIT)));
    }

    @Test
    public void moreThanMaximumAttributesInFilter() {
        user.onReportSteps().getReportAndExpectError(requestType, ReportError.TOO_MANY_ATTRIBUTES_IN_FILTERS,
                reportParameters, filter.apply(user.onFilterSteps()
                        .getFilterWithAttributes(attribute, ATTRIBUTES_LIMIT + 1)));
    }

    private static Function<String, IFormParameters> filterParameters_a() {
        return (filters) -> new ComparisonReportParameters().withFilters_a(filters);
    }

    private static Function<String, IFormParameters> filterParameters_b() {
        return (filters) -> new ComparisonReportParameters().withFilters_b(filters);
    }

    private static Function<String, IFormParameters> filterParameters() {
        return (filters) -> new CommonReportParameters().withFilters(filters);
    }
}
