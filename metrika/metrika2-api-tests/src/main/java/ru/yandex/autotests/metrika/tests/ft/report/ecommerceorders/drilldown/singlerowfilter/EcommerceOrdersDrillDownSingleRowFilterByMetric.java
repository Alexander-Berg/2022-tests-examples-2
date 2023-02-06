package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.drilldown.singlerowfilter;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.metrika.filters.Term.metric;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 29.09.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("Отчет 'Drill down - содержимое заказов': фильтр по значению метрики в строке отчета")
@RunWith(Parameterized.class)
public class EcommerceOrdersDrillDownSingleRowFilterByMetric
        extends EcommerceOrdersDrillDownSingleRowFilterBaseTest {

    private static final Double EPSILON = 0.01;
    private Double metricValue;

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public List<String> orderId;

    @Parameterized.Parameters(name = "Метрика: {0}; заказ: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {METRIC_NAMES.stream().findFirst().get(), singletonList(ORDER_ID)},
                {METRIC_NAMES.stream().skip(1).findFirst().get(), singletonList(ORDER_ID)},
        });
    }

    @Before
    public void setup() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps()
                .getEcommerceOrdersDrilldownReportAndExpectSuccess(
                        getReportParameters()
                                .withLimit(1)
                                .withParentIds(orderId));

        assumeThat("запрос вернул ровно одну строку", result.getData(), iterableWithSize(1));

        metricValue = user.onResultSteps().getMetrics(metricName, result).get(0);

        assumeThat("метрика имеет не пустое значение", metricValue, notNullValue());

        filter = metric(metricName).greaterThan(metricValue - EPSILON)
                .and(metric(metricName).lessThan(metricValue + EPSILON))
                .build();

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void singleRowTest() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps()
                .getEcommerceOrdersDrilldownReportAndExpectSuccess(
                        getReportParameters()
                                .withFilters(filter)
                                .withParentIds(orderId));

        List<Double> metrics = user.onResultSteps().getMetrics(metricName, result);

        assertThat("значение метрики в каждой строке равно заданному", metrics,
                both(Matchers.<Double>iterableWithSize(greaterThan(0)))
                        .and(everyItem(closeTo(metricValue, EPSILON))));
    }
}
