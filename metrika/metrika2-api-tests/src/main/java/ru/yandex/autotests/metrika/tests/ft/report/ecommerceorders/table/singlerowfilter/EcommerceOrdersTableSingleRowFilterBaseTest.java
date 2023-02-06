package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.table.singlerowfilter;

import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.sort.SortBuilder;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.Collection;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by konkov on 29.09.2015.
 */
public abstract class EcommerceOrdersTableSingleRowFilterBaseTest {

    private static final Counter COUNTER = ECOMMERCE_TEST;
    private static final String START_DATE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE = DateConstants.Ecommerce.END_DATE;

    protected static final UserSteps user = new UserSteps();
    protected static final Collection<String> DIMENSION_NAMES = user.onMetadataSteps().getDimensionsEcommerceOrders();
    protected static final Collection<String> METRIC_NAMES = user.onMetadataSteps().getMetricsEcommerceOrders();

    protected String filter;

    protected TableReportParameters getReportParameters() {
        return new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withMetrics(METRIC_NAMES)
                .withDimensions(DIMENSION_NAMES)
                .withSort(getSort())
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    private String getSort() {
        SortBuilder sort = sort();
        for (String metricName : METRIC_NAMES) {
            sort = sort.by(metricName).descending();
        }
        return sort.build();
    }
}
