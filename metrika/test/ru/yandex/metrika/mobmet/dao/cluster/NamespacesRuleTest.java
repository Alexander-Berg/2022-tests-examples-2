package ru.yandex.metrika.mobmet.dao.cluster;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.core.parser.QueryParams;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

@RunWith(Parameterized.class)
public class NamespacesRuleTest {

    private static final NamespacesRule RULE = new NamespacesRule("ge", "ce");

    @Parameterized.Parameter
    public String testName;

    @Parameterized.Parameter(1)
    public QueryParams queryParams;

    @Parameterized.Parameter(2)
    public boolean result;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param("Single ge metric", singleGeMetric(), true))
                .add(param("Ge metric with ce filter", geMetricWithCeFilter(), true))
                .add(param("Installation metric", installationsMetric(), false))
                .add(param("Installation filter", installationsFilter(), false))
                .add(param("User centric filter", usercentricFilter(), true))
                .add(param("User centric filter with default namespace", usercentricFilter2(), true))
                .add(param("User centric filter negative", usercentricFilter2Negative(), false))
                .add(param("User centric lower case", usercentricFilterLowerCase(), true))
                .add(param("User centric lower case negative", usercentricFilterLowerCaseNegative(), false))
                .build();
    }

    @Test
    public void testRule() {
        assertThat(RULE.isOkay(queryParams), is(result));
    }

    // region test data

    private static QueryParams singleGeMetric() {
        return queryParams("ym:ge:users", null, null);
    }

    private static QueryParams geMetricWithCeFilter() {
        return queryParams("ym:ge:users", null, "ym:ce:gender == 'male'");
    }

    private static QueryParams installationsMetric() {
        return queryParams("ym:i:installations", "ym:i:publisher", null);
    }

    private static QueryParams installationsFilter() {
        return queryParams("ym:ge:users", "ym:ge:gender", "exists ym:i:device with (publisher == 42)");
    }

    private static QueryParams usercentricFilter() {
        return queryParams("ym:ge:users", "ym:ge:gender",
                "USER_PATTERN(2017-07-01, 2017-07-01, COND(ym:ce, ym:ce:eventLabel=='test')");
    }

    private static QueryParams usercentricFilter2() {
        return queryParams("ym:ge:users", "ym:ge:gender",
                "USER_PATTERN(2017-07-01, 2017-07-01, COND(ym:ce, eventLabel=='test')");
    }

    private static QueryParams usercentricFilter2Negative() {
        return queryParams("ym:ge:users", "ym:ge:gender",
                "USER_PATTERN(2017-07-01, 2017-07-01, COND(ym:abr, eventLabel=='test')");
    }

    private static QueryParams usercentricFilterLowerCase() {
        return queryParams("ym:ge:users", "ym:ge:gender",
                "user_pattern(2017-07-01, 2017-07-01, cond(ym:ce, eventLabel=='test')");
    }

    private static QueryParams usercentricFilterLowerCaseNegative() {
        return queryParams("ym:ge:users", "ym:ge:gender",
                "user_pattern(2017-07-01, 2017-07-01, cond(ym:p, eventLabel=='test')");
    }

    private static QueryParams queryParams(String metrics, String dimensions, String filters) {
        return QueryParams.create()
                .date("2017-07-01")
                .metrics(metrics)
                .dimensions(dimensions)
                .filtersBraces(filters)
                .build();
    }

    private static Object[] param(String testName, QueryParams queryParams, boolean result) {
        return new Object[]{testName, queryParams, result};
    }

    // endregion

}
