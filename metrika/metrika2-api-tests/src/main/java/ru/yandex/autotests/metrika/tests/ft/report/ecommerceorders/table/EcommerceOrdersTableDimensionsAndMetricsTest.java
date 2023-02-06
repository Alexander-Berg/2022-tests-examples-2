package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.table;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
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
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("Отчет 'Содержимое заказов': измерения и метрики")
public class EcommerceOrdersTableDimensionsAndMetricsTest {

    private static final Counter COUNTER = ECOMMERCE_TEST;
    private static final String START_DATE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE = DateConstants.Ecommerce.END_DATE;

    private static Collection<String> DIMENSION_NAMES;
    private static Collection<String> METRIC_NAMES;

    private static final UserSteps user = new UserSteps();

    private StatV1DataGETSchema result;

    @BeforeClass
    public static void init() {
        DIMENSION_NAMES = user.onMetadataSteps().getDimensionsEcommerceOrders();
        METRIC_NAMES = user.onMetadataSteps().getMetricsEcommerceOrders();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getEcommerceOrdersTableReportAndExpectSuccess(new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withDimensions(DIMENSION_NAMES)
                .withMetrics(METRIC_NAMES)
                .withDate1(START_DATE)
                .withDate2(END_DATE));
    }

    @Test
    public void checkDimensionInQuery() {
        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataGETSchema.class).getQuery(), notNullValue()));

        assertThat("результат содержит наименование измерения", result.getQuery().getDimensions(),
                equalTo(DIMENSION_NAMES));
    }

    @Test
    public void checkDimensionUniqueness() {
        List<List<String>> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("результат не содержит неуникальных измерений", dimensions, hasNoDuplicates());
    }

    @Test
    public void checkDimensionValuesValidity() {
        List<List<String>> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("значения измерений не содержат пустых и некорректных значений", dimensions,
                everyItem(iterableHasDimensionValuesFilledAllowNull()));
    }

    @Test
    public void checkMetricInQuery() {
        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataGETSchema.class).getQuery(), notNullValue()));

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
