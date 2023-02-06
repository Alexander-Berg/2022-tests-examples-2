package ru.yandex.autotests.metrika.sort;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by konkov on 25.12.2014.
 */
public class SortBuilderTest {

    @Test
    public void testAscending() {
        assertThat(
                sort().by("ym:s:users").build(),
                equalTo("ym:s:users"));
    }

    @Test
    public void testDescending() {
        assertThat(
                sort().by("ym:s:users").descending().build(),
                equalTo("-ym:s:users"));
    }

    @Test
    public void testAscendingAscending() {
        assertThat(
                sort().by("ym:s:users").by("ym:s:visits").build(),
                equalTo("ym:s:users,ym:s:visits"));
    }

    @Test
    public void testAscendingDescending() {
        assertThat(
                sort().by("ym:s:users").by("ym:s:visits").descending().build(),
                equalTo("ym:s:users,-ym:s:visits"));
    }

    @Test
    public void testDescendingAscending() {
        assertThat(
                sort().by("ym:s:users").descending().by("ym:s:visits").build(),
                equalTo("-ym:s:users,ym:s:visits"));
    }

    @Test
    public void testDescendingDescending() {
        assertThat(
                sort().by("ym:s:users").descending().by("ym:s:visits").descending().build(),
                equalTo("-ym:s:users,-ym:s:visits"));
    }
}
