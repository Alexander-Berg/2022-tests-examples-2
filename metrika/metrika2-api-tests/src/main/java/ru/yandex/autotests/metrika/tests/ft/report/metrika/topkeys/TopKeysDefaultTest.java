package ru.yandex.autotests.metrika.tests.ft.report.metrika.topkeys;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.core.Every.everyItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasMetricValues;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.autotests.metrika.utils.Utils.flatten;

/**
 * Created by okunev on 17.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.TOP_KEYS})
@Title("Ограничение количества строк: проверка значения по умолчанию")
@RunWith(value = Parameterized.class)
public class TopKeysDefaultTest {

    /**
     * Значение по умолчанию ограничения количества строк
     */
    private static final int TOP_KEYS_DEFAULT_VALUE = 7;

    private static final String METRIC_HIT = "ym:pv:users";
    private static final String DIMENSION_HIT = "ym:pv:URL";

    private static final String METRIC_VISIT = "ym:s:users";
    private static final String DIMENSION_VISIT = "ym:s:startURL";
    private static final String START_DATE = "2015-06-01";
    private static final String END_DATE = "2015-06-02";

    private static UserSteps user;
    private static final Counter counter = YANDEX_METRIKA_2_0;

    private StatV1DataBytimeGETSchema result;

    @Parameter(value = 0)
    public String metric;

    @Parameter(value = 1)
    public String dimension;

    @Parameters(name = "метрика {0}; измерение {1}")
    public static Collection<Object[]> data() {
        return asList(new Object[][]{
                {METRIC_HIT, DIMENSION_HIT},
                {METRIC_VISIT, DIMENSION_VISIT}
        });
    }

    @BeforeClass
    public static void beforeClass() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void before() {
        BytimeReportParameters reportParameters = new BytimeReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(metric);
        reportParameters.setDimension(dimension);
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);
        reportParameters.setGroup("day");

        result = user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);

        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataBytimeGETSchema.class).getQuery(), notNullValue()));
    }

    @Test
    public void bytimeTopkeysDefaultCheckRowCount() {
        List<List<List<Double>>> metrics = user.onResultSteps().getMetrics(result);

        // В параметрах передавалась одна метрика, поэтому в ответе ожидаем тоже одну
        assertThat(format("результат содержит %s строк по 1 метрике", TOP_KEYS_DEFAULT_VALUE), metrics,
                both(Matchers.<Iterable<Iterable>>iterableWithSize(TOP_KEYS_DEFAULT_VALUE))
                        .and(everyItem(Matchers.<Iterable>iterableWithSize(1))));
    }

    @Test
    public void bytimeTopkeysDefaultCheckMetricValues() {
        List<Double> metrics = flatten(user.onResultSteps().getMetrics(result));

        assertThat("все значения метрик числа либо null", metrics, iterableHasMetricValues());
    }

}
