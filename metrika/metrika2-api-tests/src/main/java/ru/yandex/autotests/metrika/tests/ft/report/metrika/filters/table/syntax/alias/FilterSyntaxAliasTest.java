package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax.alias;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax.FilterSyntaxBaseTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 30.06.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: алиасы для операторов")
@RunWith(Parameterized.class)
public class FilterSyntaxAliasTest extends FilterSyntaxBaseTest {

    private static final String DIMENSION = "ym:pv:URL";
    private static final String METRIC = "ym:pv:pageviews";

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, metric(METRIC).equalToAlias(0)},

                {DIMENSION, METRIC, metric(METRIC).notEqualToAlias(0)},

                {DIMENSION, METRIC, dimension(DIMENSION).notDefinedAlias()},
                {DIMENSION, METRIC, dimension(DIMENSION).notDefinedAlias2()},
                {DIMENSION, METRIC, dimension(DIMENSION).notDefinedAlias3()},

                {DIMENSION, METRIC, dimension(DIMENSION).definedAlias()},
                {DIMENSION, METRIC, dimension(DIMENSION).definedAlias2()},
                {DIMENSION, METRIC, dimension(DIMENSION).definedAlias3()},

                {DIMENSION, METRIC, dimension(DIMENSION).matchSubstringAlias("ya.ru")},
                {DIMENSION, METRIC, dimension(DIMENSION).matchSubstringAlias2("ya.ru")},

                {DIMENSION, METRIC, dimension(DIMENSION).notMatchSubstringAlias("ya.ru")},
                {DIMENSION, METRIC, dimension(DIMENSION).notMatchSubstringAlias2("ya.ru")},

                {DIMENSION, METRIC, dimension(DIMENSION).matchRegExAlias(".*")},
                {DIMENSION, METRIC, dimension(DIMENSION).matchRegExAlias2(".*")},

                {DIMENSION, METRIC, dimension(DIMENSION).notMatchRegExAlias(".*")},
                {DIMENSION, METRIC, dimension(DIMENSION).notMatchRegExAlias2(".*")},

                {DIMENSION, METRIC, dimension(DIMENSION).matchStarAlias("y*")},
                {DIMENSION, METRIC, dimension(DIMENSION).notMatchStarAlias("y*")},
        });
    }
}
