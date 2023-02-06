package ru.yandex.autotests.metrika.tests.ft.report.global;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 18.07.17.
 */
@Features(Requirements.Feature.GLOBAL_REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME,
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Type.DRILLDOWN,
        Requirements.Story.Report.Type.COMPARISON,
        Requirements.Story.Report.Type.COMPARISON_DRILLDOWN})
@Title("API глобалного отчета")
@RunWith(Parameterized.class)
public class GlobalReportTest {
    private static final UserSteps user = new UserSteps();

    private static final String VISITS_METRIC_NAME = "ym:s:affinityIndexInterests";
    private static final String HITS_METRIC_NAME = "ym:pv:pageviews";
    private static final String EXTERNAL_LINKS_METRIC_NAME = "ym:el:links";
    private static final String DOWNLOADS_METRIC_NAME = "ym:dl:downloads";
    private static final String SHARE_SERVICES_METRIC_NAME = "ym:sh:users";
    private static final String SITE_SPEED_METRIC_NAME = "ym:sp:pageviewsPerDay";

    private static final String START_DATE = "3daysAgo";
    private static final String END_DATE = "3daysAgo";
    private static final String ACCURACY = "0.0001";

    @Parameterized.Parameter(0)
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public String metric;

    @Parameterized.Parameter(2)
    public String dimension;

    @Parameterized.Parameter(3)
    public String filter;

    @Parameterized.Parameters(name = "Тип запроса: {0}, метрика: {1}, измерение: {2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                        {GLOBAL_TABLE, VISITS_METRIC_NAME, "ym:s:interest",
                                Term.dimension("ym:s:interest").equalTo("tourism").build()},
                        {GLOBAL_BY_TIME, HITS_METRIC_NAME, "ym:pv:date",
                                Term.dimension("ym:pv:date").equalTo("2018-06-08").build()},
                        {GLOBAL_DRILLDOWN, EXTERNAL_LINKS_METRIC_NAME, "ym:el:browserCountry",
                                Term.dimension("ym:el:browserCountry").equalTo("ru").build()},
                        {GLOBAL_COMPARISON, DOWNLOADS_METRIC_NAME, "ym:dl:ageInterval",
                                Term.dimension("ym:dl:ageInterval").equalTo("25").build()},
                        {GLOBAL_COMPARISON_DRILLDOWN, SHARE_SERVICES_METRIC_NAME, "ym:sh:browserAndVersion",
                                Term.dimension("ym:sh:browserAndVersion").equalTo("70.18.4").build()},
                        {GLOBAL_TABLE, SITE_SPEED_METRIC_NAME, "ym:sp:clientTimeZone",
                                Term.dimension("ym:sp:clientTimeZone").equalTo("GMT+03:00").build()},
                        {GLOBAL_DRILLDOWN, VISITS_METRIC_NAME, "ym:s:physicalScreenHeight",
                                Term.dimension("ym:s:physicalScreenHeight").equalTo("768").build()},
                        {GLOBAL_COMPARISON, HITS_METRIC_NAME, "ym:pv:gender",
                                Term.dimension("ym:pv:gender").equalTo("male").build()},
                        {GLOBAL_BY_TIME, SHARE_SERVICES_METRIC_NAME, "ym:sh:browserEngine",
                                Term.dimension("ym:sh:browserEngine").equalTo("WebKit").build()}
                }
        );
    }

    private Report result;

    @Before
    public void setup() {
        result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters().apply(START_DATE, END_DATE),
                new CommonReportParameters()
                        .withMetric(metric)
                        .withDimension(dimension)
                        .withAccuracy(ACCURACY)
                        .withFilters(filter));
    }

    @Test
    public void checkFilteredResult() {
        assertThat("отчет содержит данные", result, is(not(empty())));
    }
}
