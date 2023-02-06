package ru.yandex.autotests.metrika.filters;

import org.junit.Test;
import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyString;
import static ru.yandex.autotests.metrika.filters.Not.not;
import static ru.yandex.autotests.metrika.filters.Relation.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.empty;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 08.10.2014.
 */
public class FiltersBuilderTest {
    private final ReportFilterType ANALYTICS = ReportFilterType.ANALYTICS;

    @Test
    public void testFilterBuilder() {
        Expression filter = metric("ym:s:visits").equalTo(150);

        assertThat(filter.build(), equalTo("ym:s:visits==150"));
    }

    @Test
    public void testAnd() {
        Expression filter = metric("ym:s:visits").greaterThan(150).and(metric("ym:s:visits").lessThan(160));

        assertThat(filter.build(), equalTo("(ym:s:visits>150 AND ym:s:visits<160)"));
    }

    @Test
    public void testAnalyticsAnd() {
        Expression filter = metric("ga:users").greaterThan(100).and(metric("ga:users").lessThan(110));

        assertThat(filter.build(ANALYTICS), equalTo("ga:users>100;ga:users<110"));
    }

    @Test
    public void testOrAnd() {

        Expression filter = metric("ym:s:visits").lessThan(150).or(metric("ym:s:visits").greaterThan(160))
                .and(metric("ym:s:newUsers").greaterThan(10));


        assertThat(filter.build(),
                equalTo("((ym:s:visits<150 OR ym:s:visits>160) AND ym:s:newUsers>10)"));
    }

    @Test
    public void testAnalyticsOrAnd() {
        Expression filter = metric("ga:users").lessThan(150).or(metric("ga:users").greaterThan(160))
                .and(metric("ga:newUsers").greaterThan(10));


        assertThat(filter.build(ANALYTICS),
                equalTo("ga:users<150,ga:users>160;ga:newUsers>10"));
    }

    @Test
    public void testOrAndOr() {

        Expression filter = metric("ym:s:visits").lessThan(150).or(metric("ym:s:visits").greaterThan(160))
                .and(metric("ym:s:users").lessThan(1000).or(metric("ym:s:users").greaterThan(2000)));

        assertThat(filter.build(),
                equalTo("((ym:s:visits<150 OR ym:s:visits>160) AND (ym:s:users<1000 OR ym:s:users>2000))"));
    }

    @Test
    public void testAnalyticsOrAndOr() {
        Expression filter = metric("ga:users").lessThan(150).or(metric("ga:users").greaterThan(160))
                .and(metric("ga:sessions").lessThan(1000).or(metric("ga:sessions").greaterThan(2000)));

        assertThat(filter.build(ANALYTICS),
                equalTo("ga:users<150,ga:users>160;ga:sessions<1000,ga:sessions>2000"));
    }

    @Test
    public void testOrOrOr() {
        Expression filter = dimension("ym:s:topLevelDomain").equalTo("ru")
                .or(dimension("ym:s:topLevelDomain").equalTo("com"))
                .or(dimension("ym:s:topLevelDomain").equalTo("org"));

        assertThat(filter.build(),
                equalTo("((ym:s:topLevelDomain=='ru' OR ym:s:topLevelDomain=='com') OR ym:s:topLevelDomain=='org')"));
    }

    @Test
    public void testAnalyticsOrOrOr() {
        Expression filter = dimension("ga:country").equalTo("Russia")
                .or(dimension("ga:country").equalTo("Finland"))
                .or(dimension("ga:country").equalTo("Germany"));

        assertThat(filter.build(ANALYTICS),
                equalTo("ga:country=='Russia',ga:country=='Finland',ga:country=='Germany'"));
    }

    @Test
    public void testExists() {
        Expression filter = exists(dimension("ym:s:paramsLevel1").equalTo("client_id"));

        assertThat(filter.build(),
                equalTo("EXISTS(ym:s:paramsLevel1=='client_id')"));
    }

    @Test
    public void testAll() {
        Expression filter = all(dimension("ym:s:paramsLevel1").equalTo("client_id"));

        assertThat(filter.build(),
                equalTo("ALL(ym:s:paramsLevel1=='client_id')"));
    }

    @Test
    public void testNone() {
        Expression filter = none(dimension("ym:s:paramsLevel1").equalTo("client_id"));

        assertThat(filter.build(),
                equalTo("NONE(ym:s:paramsLevel1=='client_id')"));
    }

    @Test
    public void testExistsAndNone() {
        Expression filter = exists(dimension("ym:s:paramsLevel1").equalTo("client_id"))
                .and(none(dimension("ym:s:paramsLevel2").equalTo("cart")));

        assertThat(filter.build(),
                equalTo("(EXISTS(ym:s:paramsLevel1=='client_id') AND NONE(ym:s:paramsLevel2=='cart'))"));
    }

    @Test
    public void testExistsAnd() {
        Expression filter = exists(dimension("ym:s:paramsLevel1").equalTo("new_client")
                .and(dimension("ym:s:paramsLevel2").equalTo("no")));

        assertThat(filter.build(),
                equalTo("EXISTS((ym:s:paramsLevel1=='new_client' AND ym:s:paramsLevel2=='no'))"));
    }

    @Test
    public void testEmptyLeft() {
        Expression filter = empty().and(dimension("ym:s:endURL").equalTo("X"));

        assertThat(filter.build(), equalTo("ym:s:endURL=='X'"));
    }

    @Test
    public void testEmptyRight() {
        Expression filter = dimension("ym:s:endURL").equalTo("X").and(empty());

        assertThat(filter.build(), equalTo("ym:s:endURL=='X'"));
    }

    @Test
    public void testEmptyLeftRight() {
        Expression filter = empty().and(empty());

        assertThat(filter.build(), isEmptyString());
    }

    @Test
    public void testNot() {
        Expression filter = not(dimension("ym:s:endURL").equalTo("X"));

        assertThat(filter.build(), equalTo("NOT(ym:s:endURL=='X')"));
    }

    @Test
    public void testNotNot() {
        Expression filter = not(not(dimension("ym:s:endURL").equalTo("X")));

        assertThat(filter.build(), equalTo("NOT(NOT(ym:s:endURL=='X'))"));
    }

    @Test
    public void testNotAnd() {
        Expression filter = not(dimension("ym:s:endURL").equalTo("X")).and(dimension("ym:s:startURL").equalTo("Z"));

        assertThat(filter.build(), equalTo("(NOT(ym:s:endURL=='X') AND ym:s:startURL=='Z')"));
    }

    @Test
    public void testNotOr() {
        Expression filter = not(dimension("ym:s:endURL").equalTo("X")).or(dimension("ym:s:startURL").equalTo("Z"));

        assertThat(filter.build(), equalTo("(NOT(ym:s:endURL=='X') OR ym:s:startURL=='Z')"));
    }
}
