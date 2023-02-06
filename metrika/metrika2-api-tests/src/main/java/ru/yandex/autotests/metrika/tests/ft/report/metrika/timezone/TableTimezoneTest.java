package ru.yandex.autotests.metrika.tests.ft.report.metrika.timezone;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.timezone;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.TIMEZONE})
@Title("Таймзоны")
@RunWith(Parameterized.class)
public class TableTimezoneTest {

    private static final UserSteps USER = new UserSteps();
    /* берем счетчик на котором очень мало данных, порядка одного визита в день,
    чтобы посмотреть как в отчете меняется время конкретного визита при изменении передаваемой таймзоны */
    private static final Counter COUNTER = Counters.DEMOCRAT_SPB;

    private static final String DATE_START = "2017-01-24";
    private static final String DATE_END = "2017-01-25";

    @Parameterized.Parameter()
    public String timezone;

    @Parameterized.Parameter(value = 1)
    public String timezoneValue;

    @Parameterized.Parameters(name = "Таймзона {0}")
    public static Collection createParameters() {
        return asList(new Object[][]{
                {"-10:00", "10:47:57"},
                {"-02:00", "18:47:57"},
                {"-01:00", "19:47:57"},
                {"+00:00", "20:47:57"},
                {"+01:00", "21:47:57"},
                {"+02:00", "22:47:57"},
                {"+03:00", "23:47:57"},
                {null, "23:47:57"},
                {"+04:00", "00:47:57"},
                {"+12:00", "08:47:57"},
                {"+13:00", "09:47:57"},
        });
    }

    @Test
    public void testTimezone() {
        StatV1DataGETSchema result = USER.onReportSteps().getTableReportAndExpectSuccess(
                    new TableReportParameters()
                        .withId(COUNTER)
                        .withDate1(DATE_START)
                        .withDate2(DATE_END)
                        .withDimension("ym:s:time")
                        .withSort("ym:s:time")
                        .withMetric("ym:s:visits"),
                    timezone(timezone));

        assertThat("Время совпадает с ожидаемым", result.getData().get(0).getDimensions().get(0).get("name"), equalTo(timezoneValue));
    }

}
