package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 12.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: измерения без явного указания таблицы (негативные)")
@RunWith(Parameterized.class)
public class FilterSyntaxNegativeNoNamespaceTest extends FilterNegativeBaseTest {

    private static final String HIT_METRIC = "ym:pv:pageviews";
    private static final String HIT_DIMENSION = "ym:pv:browser";

    private static final String VISIT_ONLY_DIMENSION = "startURL";

    private static final Expression VISIT_FILTER = dimension(VISIT_ONLY_DIMENSION).equalTo("url");

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {HIT_DIMENSION, HIT_METRIC, VISIT_FILTER},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return ReportError.WRONG_ATTRIBUTE_REAL;
    }
}
