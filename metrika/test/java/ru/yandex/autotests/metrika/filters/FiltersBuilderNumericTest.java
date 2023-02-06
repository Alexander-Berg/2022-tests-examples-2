package ru.yandex.autotests.metrika.filters;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 02.07.2015.
 */
public class FiltersBuilderNumericTest {
    @Test
    public void testStringValue() {
        Expression filter = dimension("ym:s:paramsLevel1").equalTo("X");

        assertThat(filter.build(), equalTo("ym:s:paramsLevel1=='X'"));
    }

    @Test
    public void testIntegerValue() {
        Expression filter = metric("ym:s:sumParams").equalTo(1);

        assertThat(filter.build(), equalTo("ym:s:sumParams==1"));
    }

    @Test
    public void testFloatValue() {
        Expression filter = metric("ym:s:sumParams").equalTo(1.5);

        assertThat(filter.build(), equalTo("ym:s:sumParams==1.5"));
    }
}
