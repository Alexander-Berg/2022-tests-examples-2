package ru.yandex.autotests.metrika.tests.ft.report.metrika.query;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ConfidenceParameters;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Collections.singletonList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.COMPARISON_DRILLDOWN;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 18.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.QUERY)
@Title("Запрос в ответе")
@RunWith(Parameterized.class)
public class QueryTest {
    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final String METRIC_NAME = "ym:s:users";
    private static final String DIMENSION_NAME = "ym:s:gender";

    private Report result;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(toArray(BY_TIME))
                .add(toArray(TABLE))
                .add(toArray(DRILLDOWN))
                .add(toArray(COMPARISON))
                .add(toArray(COMPARISON_DRILLDOWN))
                .build();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withMetric(METRIC_NAME)
                        .withDimension(DIMENSION_NAME),
                new ConfidenceParameters()
                        .withWithConfidence(true)
                        .withExcludeInsignificant(true));
    }

    @Test
    public void checkDimensionInQuery() {
        assertThat("результат содержит наименование группировки", result.getQueryDimensions(),
                equalTo(singletonList(DIMENSION_NAME)));
    }

    @Test
    public void checkMetricInQuery() {
        assertThat("результат содержит наименование метрики", result.getQueryMetrics(),
                equalTo(singletonList(METRIC_NAME)));
    }

    @Test
    public void checkWithConfidence() {
        assertThat("значение поля with_confidence совпадает с ожидаемым", result.getWithConfidence(),
                equalTo(true));
    }

    @Test
    public void checkExcludeInsignificant() {
        assertThat("значение поля exclude_insignificant совпадает с ожидаемым", result.getExcludeInsignificant(),
                equalTo(true));
    }
}
