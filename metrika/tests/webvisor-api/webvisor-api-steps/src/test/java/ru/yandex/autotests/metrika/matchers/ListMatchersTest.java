package ru.yandex.autotests.metrika.matchers;

import org.junit.Before;
import org.junit.Test;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

public class ListMatchersTest {

    ListMatchers<String> target;

    @Before
    public void setUp() throws Exception {
        target = new ListMatchers<>(3, i -> i != 1, i -> equalTo("" + i));
    }

    @Test
    public void ok() throws Exception {
        assertThat("ok", asList("0", "1", "2"), target);
    }

    @Test
    public void assumptionWorks() throws Exception {
        assertThat("also ok", asList("0", "xyz", "2"), target);
    }

    @Test(expected = AssertionError.class)
    public void fail() throws Exception {
        assertThat("fail", asList("2", "1", "0"), target);
    }

    @Test(expected = AssertionError.class)
    public void wrongSize() throws Exception {
        assertThat("too short", asList("0", "1"), target);
    }

    @Test(expected = AssertionError.class)
    public void wrongSize2() throws Exception {
        assertThat("too long", asList("0", "1", "2", "3"), target);
    }
}