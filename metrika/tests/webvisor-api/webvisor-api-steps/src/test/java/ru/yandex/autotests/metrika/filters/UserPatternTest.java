package ru.yandex.autotests.metrika.filters;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.user.TimeSequenceRelation.*;
import static ru.yandex.autotests.metrika.filters.user.User.cond;
import static ru.yandex.autotests.metrika.filters.user.User.user;

/**
 * Created by konkov on 19.06.2015.
 */
public class UserPatternTest {

    @Test
    public void testUserWithoutCond() {
        Expression filter = user("89daysAgo", "today");

        assertThat(filter.build(), equalTo("USER_PATTERN(89daysAgo, today)"));
    }

    @Test
    public void testUser() {
        Expression filter = user("2015-01-01", "2015-01-02", cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru'))"));
    }

    @Test
    public void testUserCond() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondCond() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru"))
                        .cond("ym:pv", dimension("ym:pv:URL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') COND(ym:s, ym:s:endURL=='ya.ru') COND(ym:pv, ym:pv:URL=='ya.ru'))"));
    }

    @Test
    public void testUserCondAny() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru")).any()
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') ANY COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondNext() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru")).next()
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') NEXT COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeGreaterThan() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(greaterThan(1).sec())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(>1 sec) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeGreaterThanOrEqual() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(greaterThanOrEqual(1).sec())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(>=1 sec) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeLessThan() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(lessThan(1).sec())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(<1 sec) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeLessThanOrEqual() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(lessThanOrEqual(1).sec())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(<=1 sec) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeGreaterThanMin() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(greaterThan(1).min())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(>1 min) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeGreaterThanHour() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(greaterThan(1).hour())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(>1 hour) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }

    @Test
    public void testUserCondTimeGreaterThanDay() {
        Expression filter = user("2015-01-01", "2015-01-02",
                cond("ym:s", dimension("ym:s:startURL").equalTo("ya.ru"))
                        .time(greaterThan(1).day())
                        .cond("ym:s", dimension("ym:s:endURL").equalTo("ya.ru")));

        assertThat(filter.build(), equalTo("USER_PATTERN(2015-01-01, 2015-01-02, COND(ym:s, ym:s:startURL=='ya.ru') TIME(>1 day) COND(ym:s, ym:s:endURL=='ya.ru'))"));
    }
}
