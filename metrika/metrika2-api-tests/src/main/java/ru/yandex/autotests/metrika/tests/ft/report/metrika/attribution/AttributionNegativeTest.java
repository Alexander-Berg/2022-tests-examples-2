package ru.yandex.autotests.metrika.tests.ft.report.metrika.attribution;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;

/**
 * Created by konkov on 18.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.ATTRIBUTION)
@Title("Атрибуция, негативный тест")
@RunWith(Parameterized.class)
public class AttributionNegativeTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final String METRIC = "ym:s:users";
    private static final String DIMENSION = "ym:s:<attribution>TrafficSource";

    private static final String ATTRIBUTION = "xxx";

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

    @Test
    public void attributionNegativeTest() {
        user.onReportSteps().getReportAndExpectError(
                requestType,
                ReportError.WRONG_ATTRIBUTION_VALUE,
                new CommonReportParameters()
                        .withId(COUNTER.get(ID))
                        .withMetric(METRIC)
                        .withDimension(DIMENSION),
                new ParametrizationParameters()
                        .withAttribution(ATTRIBUTION));
    }
}
