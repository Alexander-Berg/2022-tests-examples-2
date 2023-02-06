package ru.yandex.autotests.metrika.tests.ft.report.metrika.empty;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.function.BiFunction;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.comparisonDateParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME,
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Type.DRILLDOWN,
        Requirements.Story.Report.Type.COMPARISON,
        Requirements.Story.Report.Type.COMPARISON_DRILLDOWN})
@Title("Пустые отчеты")
@RunWith(Parameterized.class)
public class EmptyReportTest {

    private static final Counter COUNTER = TEST_CONDITIONS_LIMIT;
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    private static final List<String> METRICS = ImmutableList.<String>builder()
            .add(toArray("ym:s:visits"))
            .add(toArray("ym:pv:pageviews"))
            .add(toArray("ym:dl:downloads"))
            .add(toArray("ym:el:links"))
            .add(toArray("ym:sh:shares"))
            .add(toArray("ym:sp:pageviews"))
            .build();

    private UserSteps user;

    @Parameterized.Parameter(0)
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public String metric;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(GLOBAL_TABLE, dateParameters()),
                        of(GLOBAL_BY_TIME, dateParameters()),
                        of(GLOBAL_DRILLDOWN, dateParameters()),
                        of(GLOBAL_COMPARISON, comparisonDateParameters()),
                        of(GLOBAL_COMPARISON_DRILLDOWN, comparisonDateParameters()))
                .values(METRICS)
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Test
    public void emptyReportTest() {
        Report report = user.onReportSteps()
                .getReportAndExpectSuccess(
                        requestType,
                        dateParameters.apply(START_DATE, END_DATE),
                        new CommonReportParameters()
                                .withId(COUNTER.get(ID))
                                .withMetric(metric));

        assertThat("отчет не содержит данных", report.getMetrics(),
                everyItem(everyItem(everyItem(equalTo(0d)))));
    }
}
