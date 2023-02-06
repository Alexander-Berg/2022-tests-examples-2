package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;


/**
 * Created by konkov on 12.11.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC
})
@Title("Фильтры: операторы для атрибутов user centric сегментации")
@RunWith(Parameterized.class)
public class FilterSyntaxUserCentricOperatorsTest extends FilterSyntaxBaseTest {

    private static final String VISIT_DIMENSION_NAME = "ym:s:gender";
    private static final String VISIT_METRIC_NAME = "ym:s:visits";

    private static final String HIT_DIMENSION_NAME = "ym:pv:gender";
    private static final String HIT_METRIC_NAME = "ym:pv:pageviews";

    private static final String USER_CENTRIC_ATTR = "ym:u:firstSearchPhrase";
    private static final String USER_CENTRIC_ATTR_INTEREST = "ym:u:interest";
    private static final String USER_CENTRIC_EVENT_VISIT_PARAMS = "ym:s:paramsLevel1";
    private static final String USER_CENTRIC_METRIC = "ym:u:userVisits";
    private static final String USER_CENTRIC_EVENT_VISIT = "ym:s:searchPhrase";
    private static final String USER_CENTRIC_EVENT_HIT = "ym:pv:URL";
    private static final String USER_CENTRIC_GENDER = "ym:s:gender";

    private static final String USER_ID = "ym:u:userID";
    private static final String USER_ID_VISITS = "ym:s:userID";
    private static final String USER_ID_HITS = "ym:pv:userID";

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder().vectorValues(
                of(VISIT_DIMENSION_NAME, VISIT_METRIC_NAME),
                of(HIT_DIMENSION_NAME, HIT_METRIC_NAME)
        ).values(
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).notMatchStar("*amf*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).notEqualTo("amf")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).notMatchSubstring("market")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).notMatchRegEx(".*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).lessThan("amf")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).lessThanOrEqualTo("amf")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).matchStar("*amf*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).equalTo("amf")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).in("amf")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).in("amf", "амф")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).notIn("amf", "амф")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).matchSubstring("market")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).matchRegEx(".*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).greaterThan("amf")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR).greaterThanOrEqualTo("amf")),

                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).defined()),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).notDefined()),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).notEqualTo("literature")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).equalTo("literature")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).in("literature")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).in("literature", "cinema")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).notIn("literature", "cinema")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).greaterThan("cinema")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).lessThan("cinema")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).greaterThanOrEqualTo("cinema")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).lessThanOrEqualTo("cinema")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).matchSubstring("cin")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).notMatchSubstring("cin")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).matchRegEx(".*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).notMatchRegEx(".*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).matchStar("*")),
                exists(USER_ID, dimension(USER_CENTRIC_ATTR_INTEREST).notMatchStar("*")),

                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).notMatchStar("*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).notEqualTo("category")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).notMatchSubstring("cat")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).notMatchRegEx(".*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).lessThan("category")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).lessThanOrEqualTo("category")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).matchStar("*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).equalTo("category")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).in("category")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).in("category", "level")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).notIn("category", "level")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).matchSubstring("cat")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).matchRegEx(".*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT_PARAMS).greaterThan("category")),

                exists(USER_ID_VISITS, dimension(USER_CENTRIC_GENDER).equalTo("male"))
                        .and(dimension(USER_CENTRIC_GENDER).equalTo("male")),

                exists(USER_ID, dimension(USER_CENTRIC_METRIC).equalTo(0)),
                exists(USER_ID, dimension(USER_CENTRIC_METRIC).greaterThan(0)),
                exists(USER_ID, dimension(USER_CENTRIC_METRIC).lessThan(0)),
                exists(USER_ID, dimension(USER_CENTRIC_METRIC).greaterThanOrEqualTo(0)),
                exists(USER_ID, dimension(USER_CENTRIC_METRIC).lessThanOrEqualTo(0)),
                exists(USER_ID, dimension(USER_CENTRIC_METRIC).notEqualTo(0)),

                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).notMatchStar("*amf*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).notEqualTo("amf")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).notMatchSubstring("market")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).notMatchRegEx(".*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).lessThan("amf")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).lessThanOrEqualTo("amf")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).matchStar("*amf*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).equalTo("amf")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).in("amf")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).in("amf", "амф")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).notIn("amf", "амф")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).matchSubstring("market")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).matchRegEx(".*")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).greaterThan("amf")),
                exists(USER_ID_VISITS, dimension(USER_CENTRIC_EVENT_VISIT).greaterThanOrEqualTo("amf")),

                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).notMatchStar("*ya*")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).notEqualTo("http://market.yandex.ru/")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).notMatchSubstring("market")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).notMatchRegEx(".*")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).lessThan("http://market.yandex.ru/")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).lessThanOrEqualTo("http://market.yandex.ru/")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).matchStar("*ya*")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).equalTo("http://market.yandex.ru/")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).in("http://market.yandex.ru/")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).in("http://market.yandex.ru/", "http://google.com")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).notIn("http://market.yandex.ru/", "http://google.com")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).matchSubstring("market")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).matchRegEx(".*")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).greaterThan("http://market.yandex.ru/")),
                exists(USER_ID_HITS, dimension(USER_CENTRIC_EVENT_HIT).greaterThanOrEqualTo("http://market.yandex.ru/"))
        ).build();
    }

}
