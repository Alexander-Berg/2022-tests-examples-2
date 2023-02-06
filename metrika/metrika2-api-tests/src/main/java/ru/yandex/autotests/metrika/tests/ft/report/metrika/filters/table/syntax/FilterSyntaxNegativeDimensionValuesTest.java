package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: значения (негативные)")
@RunWith(Parameterized.class)
public class FilterSyntaxNegativeDimensionValuesTest extends FilterNegativeBaseTest {

    private final static String DIMENSION_DATE = "ym:pv:date";
    private final static String DIMENSION_DEVICE_CATEGORY_NAME = "ym:pv:deviceCategoryName";

    private final static String METRIC_HIT = "ym:pv:pageviews";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                // METR-30971
                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("crypta_interest_tablets_name")},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return ReportError.VALUE_NOT_SUPPORTED_FOR_DIMENSION;
    }
}
