package ru.yandex.autotests.metrika.filters;

import org.junit.Test;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 26.06.2015.
 */
public class MultiArgumentTest {
    @Test
    public void testInSingle() {
        Expression filter = metric("ym:s:visits").in(150);

        assertThat(filter.build(), equalTo("ym:s:visits=.150"));
    }

    @Test
    public void testInMulti() {
        Expression filter = metric("ym:s:visits").in(150, 200);

        assertThat(filter.build(), equalTo("ym:s:visits=.(150,200)"));
    }

    @Test
    public void testInMultiList() {
        Expression filter = metric("ym:s:visits").in(asList(150, 200));

        assertThat(filter.build(), equalTo("ym:s:visits=.(150,200)"));
    }

    @Test
    public void testNotInMulti() {
        Expression filter = metric("ym:s:visits").notIn(150, 200);

        assertThat(filter.build(), equalTo("ym:s:visits!.(150,200)"));
    }

    @Test
    public void testNotEqualSingle() {
        Expression filter = metric("ym:s:visits").notEqualTo(150);

        assertThat(filter.build(), equalTo("ym:s:visits!=150"));
    }

    @Test
    public void testNotEqualMultiList() {
        Expression filter = metric("ym:s:visits").notEqualTo(asList(150, 200));

        assertThat(filter.build(), equalTo("ym:s:visits!=(150,200)"));
    }
}
