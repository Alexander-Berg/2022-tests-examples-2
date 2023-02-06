package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.drilldown;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilledAllowNull;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasMetricValues;
import static ru.yandex.autotests.metrika.matchers.NoDuplicatesMatcher.hasNoDuplicates;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.autotests.metrika.utils.Utils.flatten;

/**
 * Created by okunev on 09.09.2015.
 */
public abstract class EcommerceOrdersDrilldownDimensionsAndMetricsBaseTest {

    protected static final Counter COUNTER = ECOMMERCE_TEST;
    protected static final String START_DATE = DateConstants.Ecommerce.START_DATE;
    protected static final String END_DATE = DateConstants.Ecommerce.END_DATE;

    protected static Collection<String> DIMENSION_NAMES;
    protected static Collection<String> METRIC_NAMES;

    private static final UserSteps user = new UserSteps();

    private StatV1DataDrilldownGETSchema result;

    protected abstract DrillDownReportParameters getReportParameters();

    @BeforeClass
    public static void init() {
        DIMENSION_NAMES = user.onMetadataSteps().getDimensionsEcommerceOrders();
        METRIC_NAMES = user.onMetadataSteps().getMetricsEcommerceOrders();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getEcommerceOrdersDrilldownReportAndExpectSuccess(getReportParameters());
    }

    @Test
    public void checkDimensionInQuery() {
        assertThat("результат содержит наименование измерения", result.getQuery().getDimensions(),
                equalTo(DIMENSION_NAMES));
    }

    @Test
    public void checkDimensionUniqueness() {
        List<String> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("результат не содержит неуникальных измерений", dimensions, hasNoDuplicates());
    }

    @Test
    public void checkDimensionValuesValidity() {
        List<String> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("значения измерений не содержат пустых и некорректных значений", dimensions,
                iterableHasDimensionValuesFilledAllowNull());
    }

    @Test
    public void checkMetricInQuery() {

        assertThat("результат содержит наименование метрики", result.getQuery().getMetrics(),
                equalTo(METRIC_NAMES));
    }

    @Test
    public void checkMetricValues() {
        //для проверки корректности значений метрик извлекаем их в линейный список
        List<Double> metrics = flatten(user.onResultSteps().getMetrics(result));

        assumeThat("значения метрик присутствуют", metrics, not(empty()));

        assertThat("все значения метрик числа либо null", metrics, iterableHasMetricValues());
    }

}
