package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.FilterParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;

/**
 * Created by sourx on 27/02/2018.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.FILTERS)
@Title("Запросы с пустым фильтром")
@RunWith(Parameterized.class)
public class EmptyFilterTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = Counters.YANDEX_MARKET;

    private static final String METRIC = "ym:s:users";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameters(name = "Тип запроса: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                        {TABLE},
                        {BY_TIME},
                        {DRILLDOWN},
                        {COMPARISON},
                        {COMPARISON_DRILLDOWN}
                }
        );
    }

    @Test
    public void checkEmptyFilter() {
        FilterParameters filters = FilterParameters.filters(EMPTY);
        filters.ignoreEmptyParameters(false);

        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withMetric(METRIC),
                filters
        );
    }
}
