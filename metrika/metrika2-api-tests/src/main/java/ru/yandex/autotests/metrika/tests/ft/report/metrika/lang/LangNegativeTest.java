package ru.yandex.autotests.metrika.tests.ft.report.metrika.lang;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.lang;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.LANG})
@Title("Локализация некорректный язык")
@RunWith(Parameterized.class)
public class LangNegativeTest {
    private static UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = Counters.SENDFLOWERS_RU;

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:interest";

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    private static final String INCORRECT_LANG = "xz";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(toArray(TABLE, new TableReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)))
                .add(toArray(DRILLDOWN, new DrillDownReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)))
                .add(toArray(COMPARISON, new ComparisonReportParameters()
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)))
                .add(toArray(COMPARISON_DRILLDOWN, new ComparisonDrilldownReportParameters()
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)))
                .add(toArray(BY_TIME, new BytimeReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)))
                .build();
    }

    @Test
    public void checkUnsupportedLang() {
        user.onReportSteps().getReportAndExpectError(requestType,
                ReportError.WRONG_LANG,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withMetric(METRIC_NAME)
                        .withDimension(DIMENSION_NAME),
                parameters,
                lang(INCORRECT_LANG));
    }
}
