package ru.yandex.autotests.metrika.tests.ft.report.metrika.lang;

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
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.lang;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by omaz on 07.07.16.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.LANG})
@Title("Локализация")
@RunWith(Parameterized.class)
public class LangTest {

    private static UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = Counters.SENDFLOWERS_RU;

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:interest";

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    private static final String DIMENSION_ID = "literature";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String lang;

    @Parameterized.Parameter(3)
    public String expectedDimensionName;

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
                        of("ru", "Литература и учебные материалы"),
                        of("en", "Literature and educational materials"),
                        of("tr", "Edebiyat ve eğitim materyalleri"),
                        of("ua", "Литература и учебные материалы"),
                        of("uk", "Литература и учебные материалы"),
                        of("fi", "Literature and educational materials"),
                        of("de", "Literatur und Bildungsmaterialien"),
                        of("", "Литература и учебные материалы"))
                .build();
    }

    @Test
    public void checkDimensionName() {
        Report result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withFilters(dimension(DIMENSION_NAME).equalTo(DIMENSION_ID).build()),
                parameters,
                lang(lang));

        assumeThat("получена одна строка данных",
                result.getTotalRows(),
                equalTo(1L));

        assertThat("значение измерение совпадает с ожидаемым",
                result.getDimension(DIMENSION_NAME).get(0),
                equalTo(expectedDimensionName));
    }

}
