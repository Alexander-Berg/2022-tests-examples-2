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
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 29.09.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("Отчет 'Drill down - содержимое заказов': фильтр по значению группировки в строке отчета")
@RunWith(Parameterized.class)
public class EcommerceOrdersDrillDownSingleRowFilterByDimension
        extends EcommerceOrdersDrillDownSingleRowFilterBaseTest {

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public List<String> orderId;

    @Parameterized.Parameters(name = "Группировка: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_NAMES.stream().findFirst().get(), emptyList()},
                {DIMENSION_NAMES.stream().skip(1).findFirst().get(), singletonList(ORDER_ID)},
        });
    }

    private String dimensionValue;

    @Before
    public void setup() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps()
                .getEcommerceOrdersDrilldownReportAndExpectSuccess(
                        getReportParameters()
                                .withLimit(1)
                                .withParentIds(orderId));

        assumeThat("запрос вернул ровно одну строку", result.getData(), iterableWithSize(1));

        dimensionValue = user.onResultSteps().getDimensions(result).get(0);

        filter = dimension(dimensionName).equalTo(dimensionValue).build();

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void singleRowTest() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps()
                .getEcommerceOrdersDrilldownReportAndExpectSuccess(
                        getReportParameters()
                                .withFilters(filter)
                                .withParentIds(orderId));

        List<String> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("значение группировки в каждой строке равно заданному", dimensions,
                both(Matchers.<String>iterableWithSize(greaterThan(0)))
                        .and(everyItem(equalTo(dimensionValue))));
    }
}
