package ru.yandex.autotests.metrika.filters;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.filters.Relation.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 12.11.2015.
 */
public class UserCentricTest {

    @Test
    public void testExists() {
        Expression filter = exists("ym:u:userID", dimension("ym:u:gender").equalTo("male"));

        assertThat(filter.build(), equalTo("EXISTS ym:u:userID WITH(ym:u:gender=='male')"));
    }

    @Test
    public void testAll() {
        Expression filter = all("ym:u:userID", dimension("ym:u:gender").equalTo("male"));

        assertThat(filter.build(), equalTo("ALL ym:u:userID WITH(ym:u:gender=='male')"));
    }

    @Test
    public void testNone() {
        Expression filter = none("ym:u:userID", dimension("ym:u:gender").equalTo("male"));

        assertThat(filter.build(), equalTo("NONE ym:u:userID WITH(ym:u:gender=='male')"));
    }
}
