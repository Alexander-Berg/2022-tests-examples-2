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
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 12.11.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC
})
@Title("Фильтры: операторы для атрибутов user centric сегментации (негативные)")
@RunWith(Parameterized.class)
public class FilterSyntaxNegativeUserCentricOperatorsTest extends FilterNegativeBaseTest {

    private static final String DIMENSION_NAME = "ym:s:gender";
    private static final String METRIC_NAME = "ym:s:visits";

    private static final String USER_CENTRIC_METRIC = "ym:u:userVisits";
    private static final String USER_ID = "ym:u:userID";

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createParams(exists(USER_ID, metric(USER_CENTRIC_METRIC).matchSubstring("1"))),
                createParams(exists(USER_ID, metric(USER_CENTRIC_METRIC).notMatchSubstring("1"))),
                createParams(exists(USER_ID, metric(USER_CENTRIC_METRIC).matchRegEx(".*"))),
                createParams(exists(USER_ID, metric(USER_CENTRIC_METRIC).notMatchRegEx(".*"))),
                createParams(exists(USER_ID, metric(USER_CENTRIC_METRIC).matchStar("*"))),
                createParams(exists(USER_ID, metric(USER_CENTRIC_METRIC).notMatchStar("*")))
        );
    }

    @Override
    protected IExpectedError getExpectedError() {
        return ReportError.OPERATOR_NOT_SUPPORTED_FOR_DIMENSION;
    }

    private static Object[] createParams(Expression expression) {
        return toArray(DIMENSION_NAME, METRIC_NAME, expression);
    }
}
