package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.table.singlerowfilter;

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
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 29.09.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("Отчет 'Содержимое заказов': фильтр по значению группировки в строке отчета")
@RunWith(Parameterized.class)
public class EcommerceOrdersTableSingleRowFilterByDimensionTest extends EcommerceOrdersTableSingleRowFilterBaseTest {

    private String dimensionValue;

    @Parameterized.Parameter(value = 0)
    public String dimensionName;

    @Parameterized.Parameters(name = "Группировка: {0}")
    public static Collection createParameters() {
        return with(DIMENSION_NAMES).convert(new ToArrayConverter<>());
    }

    @Before
    public void setup() {
        StatV1DataGETSchema result = user.onReportSteps()
                .getEcommerceOrdersTableReportAndExpectSuccess(getReportParameters().withLimit(1));

        assumeThat("запрос вернул ровно одну строку", result.getData(), iterableWithSize(1));

        dimensionValue = user.onResultSteps().getDimensionValues(dimensionName, result).get(0);

        filter = dimension(dimensionName).equalTo(dimensionValue).build();

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void singleRowTest() {
        StatV1DataGETSchema result = user.onReportSteps()
                .getEcommerceOrdersTableReportAndExpectSuccess(getReportParameters().withFilters(filter));

        List<String> dimensions = user.onResultSteps().getDimensionValues(dimensionName, result);

        assertThat("значение группировки в каждой строке равно заданному", dimensions,
                both(Matchers.<String>iterableWithSize(greaterThan(0)))
                        .and(everyItem(equalTo(dimensionValue))));
    }
}
