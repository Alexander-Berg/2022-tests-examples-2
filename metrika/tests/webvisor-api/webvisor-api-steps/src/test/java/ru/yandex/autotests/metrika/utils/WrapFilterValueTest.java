package ru.yandex.autotests.metrika.utils;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;

/**
 * Created by konkov on 06.06.2016.
 */
public class WrapFilterValueTest {
    @Test
    public void checkNull() {
        assertThat(Utils.wrapFilterValue(null), equalTo("null"));
    }

    @Test
    public void checkString() {
        assertThat(Utils.wrapFilterValue("s"), equalTo("'s'"));
    }

    @Test
    public void checkNumber() {
        assertThat(Utils.wrapFilterValue(42), equalTo("42"));
    }
}
