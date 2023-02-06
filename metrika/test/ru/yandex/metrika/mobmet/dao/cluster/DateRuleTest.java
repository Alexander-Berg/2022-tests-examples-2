package ru.yandex.metrika.mobmet.dao.cluster;

import java.util.Collection;
import java.util.Set;

import com.google.common.collect.ImmutableList;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.core.parser.QueryParams;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

@RunWith(Parameterized.class)
public class DateRuleTest {

    private static DateRule rule;

    @Parameterized.Parameter
    public String testName;

    @Parameterized.Parameter(1)
    public QueryParams queryParams;

    @Parameterized.Parameter(2)
    public boolean result;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param("Old date", oldDate(), false))
                .add(param("Old filters", oldFilters(), false))
                .add(param("Old filters with inner exists", oldFilterInneerExists(), false))
                .add(param("Old metric filters", oldMetricFilters(), false))
                .add(param("All okay", allOkay(), true))
                .add(param("Lifetime filters", lifetimeFiltersOkay(), true))
                .add(param("New filters inner exists", filterInneerExistsOkay(), true))
                .build();
    }

    @BeforeClass
    public static void beforeClass() {
        rule = new DateRule("2017-01-01", Set.of("i", "d"), ApiUtilsTestUtils.buildMobApiUtils());
        rule.init();
    }

    @Test
    public void testRule() {
        assertThat(rule.isOkay(queryParams), is(result));
    }


    private static QueryParams oldDate() {
        return queryParams("2016-12-01", "2017-06-01", null, "ym:ge:users");
    }

    private static QueryParams oldFilters() {
        return queryParams("2017-06-01", "2017-07-01",
                "exists ym:pc:device with (specialDefaultDate >= '2015-01-01')", "ym:ge:users");
    }

    private static QueryParams oldMetricFilters() {
        return queryParams("2017-06-01", "2017-07-01",
                null, "ym:ge:users(exists ym:i:device with (specialDefaultDate >= '2015-01-01'))");
    }

    private static QueryParams oldFilterInneerExists() {
        return queryParams("2017-06-01", "2017-07-01",
                "exists ym:i:device with (specialDefaultDate >= '2015-01-01' and exists ym:pc:device with (specialDefaultDate >= '2015-01-01'))",
                "ym:ge:users");
    }

    private static QueryParams allOkay() {
        return queryParams("2017-06-01", "2017-07-01",
                "exists ym:i:device with (specialDefaultDate >= '2017-02-01')",
                "ym:ge:users(exists ym:i:device with (specialDefaultDate >= '2017-02-01'))");
    }

    private static QueryParams lifetimeFiltersOkay() {
        return queryParams("2017-06-01", "2017-07-01",
                "exists ym:i:device with (exists(urlParamKey=='utm_medium' and urlParamValue=='organic') and specialDefaultDate >= '2015-01-01')",
                "ym:ge:users");
    }

    private static QueryParams filterInneerExistsOkay() {
        return queryParams("2017-06-01", "2017-07-01",
                "exists ym:i:device with (specialDefaultDate >= '2015-01-01' and exists ym:d:device with (specialDefaultDate >= '2015-01-01'))",
                "ym:ge:users");
    }

    private static QueryParams queryParams(String date1, String date2, String filters, String metrics) {
        return QueryParams.create()
                .startDate(date1)
                .endDate(date2)
                .metrics(metrics)
                .filtersBraces(filters)
                .build();
    }

    private static Object[] param(String testName, QueryParams queryParams, boolean result) {
        return new Object[]{testName, queryParams, result};
    }

}
