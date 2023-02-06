package ru.yandex.autotests.metrika.tests.ft.report.metrika.lang;

import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.lang;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.LANG)
@Title("Локализация сообщений об ошибках")
@RunWith(Parameterized.class)
public class LangErrorMessageTest {

    private static UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = Counters.SENDFLOWERS_RU;

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:interest";

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    private static final Long EXPECTED_ERROR_CODE = 400L;
    private static final String WRONG_DIMENSION = "ym:xx:dimension";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String lang;

    @Parameterized.Parameter(3)
    public String expectedErrorMessage;

    @Parameterized.Parameters(name = "{0}: {2}: {3}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(DRILLDOWN, new DrillDownReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(COMPARISON, new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)),
                        of(COMPARISON_DRILLDOWN, new ComparisonDrilldownReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)),
                        of(BY_TIME, new BytimeReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)))
                .vectorValues(
                        of("ru", "Неверно указан атрибут, значение: ym:xx:dimension, код ошибки: 4001"),
                        of("en", "Incorrectly specified attribute, value: ym:xx:dimension, error code: 4001"),
                        of("tr", "Özellik hatalı belirtildi, değer: ym:xx:dimension, Hata kodu: 4001"),
                        of("ua", "Неверно указан атрибут, значение: ym:xx:dimension, код ошибки: 4001"),
                        of("uk", "Неверно указан атрибут, значение: ym:xx:dimension, код ошибки: 4001"))
                .build();
    }

    @Test
    public void checkErrorMessage() {
        user.onReportSteps().getReportAndExpectError(
                requestType,
                expect(EXPECTED_ERROR_CODE, expectedErrorMessage),
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withFilters(dimension(WRONG_DIMENSION).equalTo(StringUtils.EMPTY).build()),
                parameters,
                lang(lang));
    }
}
