package ru.yandex.autotests.metrika.tests.ft.report.metrika.group;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.lang.String.format;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 30.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.GROUP})
@Title("Группировка: проверки группирования дат")
@RunWith(Parameterized.class)
public class GroupIntervalsTest {

    private static final List<String> METRICS = asList("ym:s:users", "ym:s:newUsers");
    private static final String DIMENSION = "ym:s:browser";

    private static final int EXPECTED_FIT_SIZE = 1;
    private static final int HOUR_EXPECTED_SIZE = 24;
    private static final int DEKAMINUTE_EXPECTED_SIZE = 144;
    private static final int MINUTE_EXPECTED_SIZE = 1440;

    private static final String START_DATE = "2014-01-01";
    private static final String DAY_DATE = "2014-01-02";
    private static final String WEEK_DATE1 = "2014-01-06";
    private static final String WEEK_DATE2 = "2014-01-12";
    private static final String MONTH_DATE1 = "2014-01-31";
    private static final String MONTH_DATE2 = "2014-02-01";
    private static final String MONTH_DATE3 = "2014-02-03";
    private static final String QUARTER_DATE1 = "2014-03-31";
    private static final String QUARTER_DATE2 = "2014-04-01";
    private static final String YEAR_DATE1 = "2014-12-31";
    private static final String YEAR_DATE2 = "2015-01-01";

    protected static UserSteps user;
    private static final Counter counter = CounterConstants.LITE_DATA;

    protected StatV1DataBytimeGETSchema result;

    @Parameterized.Parameter(0)
    public GroupEnum group;

    @Parameterized.Parameter(1)
    public String date1;

    @Parameterized.Parameter(2)
    public String date2;

    @Parameterized.Parameter(3)
    public int expectedSize;

    @Parameterized.Parameters(name = "{0}: {1} - {2}")
    public static Collection<Object[]> data() {
        return asList(new Object[][]{
                //проверка группирования интервала дат по часу, декаминуте и минуте
                {GroupEnum.HOUR, START_DATE, START_DATE, HOUR_EXPECTED_SIZE},
                {GroupEnum.HOUR, START_DATE, DAY_DATE, HOUR_EXPECTED_SIZE * 2},
                {GroupEnum.DEKAMINUTE, START_DATE, START_DATE, DEKAMINUTE_EXPECTED_SIZE},
                {GroupEnum.DEKAMINUTE, START_DATE, DAY_DATE, DEKAMINUTE_EXPECTED_SIZE * 2},
                {GroupEnum.MINUTE, START_DATE, START_DATE, MINUTE_EXPECTED_SIZE},
                {GroupEnum.MINUTE, START_DATE, DAY_DATE, MINUTE_EXPECTED_SIZE * 2},

                //проверка группирования интервала дат по размеру группировки
                {GroupEnum.ALL, START_DATE, MONTH_DATE1, EXPECTED_FIT_SIZE},
                {GroupEnum.YEAR, START_DATE, YEAR_DATE1, EXPECTED_FIT_SIZE},
                {GroupEnum.QUARTER, START_DATE, QUARTER_DATE1, EXPECTED_FIT_SIZE},
                {GroupEnum.MONTH, START_DATE, MONTH_DATE1, EXPECTED_FIT_SIZE},
                {GroupEnum.WEEK, WEEK_DATE1, WEEK_DATE2, EXPECTED_FIT_SIZE},
                {GroupEnum.DAY, START_DATE, START_DATE, EXPECTED_FIT_SIZE},

                //проверка группирования дат на границе интервала группировки
                {GroupEnum.YEAR, YEAR_DATE1, YEAR_DATE2, EXPECTED_FIT_SIZE * 2},
                {GroupEnum.QUARTER, QUARTER_DATE1, QUARTER_DATE2, EXPECTED_FIT_SIZE * 2},
                {GroupEnum.MONTH, MONTH_DATE1, MONTH_DATE2, EXPECTED_FIT_SIZE * 2},
                {GroupEnum.WEEK, MONTH_DATE1, MONTH_DATE3, EXPECTED_FIT_SIZE * 2},
                {GroupEnum.DAY, MONTH_DATE1, MONTH_DATE2, EXPECTED_FIT_SIZE * 2},

                //проверка автоматической группировки интервала дат
                {GroupEnum.AUTO, START_DATE, START_DATE, HOUR_EXPECTED_SIZE},
                {GroupEnum.AUTO, START_DATE, DAY_DATE, HOUR_EXPECTED_SIZE},
                {GroupEnum.AUTO, START_DATE, WEEK_DATE1, HOUR_EXPECTED_SIZE},
                {GroupEnum.AUTO, YEAR_DATE1, YEAR_DATE2, HOUR_EXPECTED_SIZE}
        });
    }

    @BeforeClass
    public static void beforeClass() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void before() {
        result = user.onReportSteps().getBytimeReportAndExpectSuccess(
                new BytimeReportParameters()
                        .withId(counter.get(ID))
                        .withDimension(DIMENSION)
                        .withMetrics(METRICS)
                        .withGroup(group)
                        .withDate1(date1)
                        .withDate2(date2));
    }

    @Test
    public void bytimeGroupCheckIntervalGrouping() {
        List<List<List<Double>>> metrics = user.onResultSteps().getMetrics(result);

        assertThat(format("результат содержит %s метрики по %s значению", METRICS.size(), expectedSize),
                metrics, both(everyItem(Matchers.<Iterable<Iterable>>iterableWithSize(METRICS.size())))
                        .and(everyItem(everyItem(Matchers.<Iterable>iterableWithSize(expectedSize)))));
    }

    @Test
    public void bytimeGroupCheckTotals() {
        assertThat("результат содержит итоговые значения в формате аналогичном значению метрик",
                result.getTotals(), both(Matchers.<Iterable<Iterable>>iterableWithSize(METRICS.size()))
                        .and(everyItem(Matchers.<Iterable>iterableWithSize(expectedSize))));
    }

}
