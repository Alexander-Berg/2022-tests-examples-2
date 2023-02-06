package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.bytime;

import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 11.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'по времени': фильтры, метрики и измерения, которые не присутствуют в запросе")
public class ByTimeFiltersNotInQueryTest {

    private static UserSteps user;

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final String CONDITION_METRIC = "ym:s:newUsers";
    private static final String CONDITION_DIMENSION = "ym:s:endURL";
    private static final String QUERY_METRIC = "ym:s:users";
    private static final String QUERY_DIMENSION = "ym:s:browser";

    private BytimeReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new BytimeReportParameters();
        reportParameters.setId(COUNTER.get(ID));
        reportParameters.setMetric(QUERY_METRIC);
        reportParameters.setDimension(QUERY_DIMENSION);
    }

    @Test
    public void filterByDimensionTest() {
        reportParameters.setFilters(dimension(CONDITION_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByMetricTest() {
        reportParameters.setFilters(metric(CONDITION_METRIC).equalTo(0).build());

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }
}
