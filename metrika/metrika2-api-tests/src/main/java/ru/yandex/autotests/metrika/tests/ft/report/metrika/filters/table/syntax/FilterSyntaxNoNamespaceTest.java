package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Relation.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 25.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: измерения без явного указания таблицы")
@RunWith(Parameterized.class)
public class FilterSyntaxNoNamespaceTest extends FilterSyntaxBaseTest {

    private static final String VISIT_METRIC = "ym:s:users";
    private static final String VISIT_DIMENSION = "ym:s:browser";

    private static final String HIT_METRIC = "ym:pv:pageviews";
    private static final String HIT_DIMENSION = "ym:pv:browser";
    // compatible with visits and hits
    private static final String CONDITION_DIMENSION = "regionID";

    private static final String VISIT_ONLY_DIMENSION = "startURL";

    private static final Expression MOSCOW = dimension(CONDITION_DIMENSION).equalTo("213");
    // внутри квантора атрибут без таблицы получает таблицу квантора. снаружи кванторов - таблицу из dimensions
    private static final Expression VISITS_MOSCOW = exists("ym:s:userID", dimension(CONDITION_DIMENSION).equalTo("213"));
    private static final Expression HITS_MOSCOW = exists("ym:pv:userID", dimension(CONDITION_DIMENSION).equalTo("213"));


    private static final Expression VISIT_FILTER = dimension(VISIT_ONLY_DIMENSION).equalTo("url");


    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {VISIT_DIMENSION, VISIT_METRIC, MOSCOW},
                {VISIT_DIMENSION, VISIT_METRIC, VISITS_MOSCOW},
                {VISIT_DIMENSION, VISIT_METRIC, HITS_MOSCOW},
                {VISIT_DIMENSION, VISIT_METRIC, VISIT_FILTER},
                {HIT_DIMENSION, HIT_METRIC, MOSCOW},
                {HIT_DIMENSION, HIT_METRIC, VISITS_MOSCOW},
                {HIT_DIMENSION, HIT_METRIC, HITS_MOSCOW}
        });
    }

}
