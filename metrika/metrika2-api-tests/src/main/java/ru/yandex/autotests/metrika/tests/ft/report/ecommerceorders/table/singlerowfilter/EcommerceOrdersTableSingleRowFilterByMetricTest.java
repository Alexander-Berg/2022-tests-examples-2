package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.table.singlerowfilter;

/**
 * Created by konkov on 29.09.2015.
 */

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.converters.ToArrayConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.collection.LambdaCollections.with;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.metrika.filters.Term.metric;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("Отчет 'Содержимое заказов': фильтр по значению метрики в строке отчета")
@RunWith(Parameterized.class)
public class EcommerceOrdersTableSingleRowFilterByMetricTest extends EcommerceOrdersTableSingleRowFilterBaseTest {

    private static final Double EPSILON = 0.01;
    private Double metricValue;

    @Parameterized.Parameter(value = 0)
    public String metricName;

    @Parameterized.Parameters(name = "Метрика: {0}")
    public static Collection createParameters() {
        return with(METRIC_NAMES).convert(new ToArrayConverter<>());
    }

    @Before
    public void setup() {
        StatV1DataGETSchema result = user.onReportSteps()
                .getEcommerceOrdersTableReportAndExpectSuccess(getReportParameters().withLimit(1));

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
        StatV1DataGETSchema result = user.onReportSteps()
                .getEcommerceOrdersTableReportAndExpectSuccess(getReportParameters().withFilters(filter));

        List<Double> metrics = user.onResultSteps().getMetrics(metricName, result);

        assertThat("значение метрики в каждой строке равно заданному", metrics,
                both(Matchers.<Double>iterableWithSize(greaterThan(0)))
                        .and(everyItem(closeTo(metricValue, EPSILON))));
    }

}
