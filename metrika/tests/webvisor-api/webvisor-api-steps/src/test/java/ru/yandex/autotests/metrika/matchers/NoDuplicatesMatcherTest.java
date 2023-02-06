package ru.yandex.autotests.metrika.matchers;

import org.junit.Test;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.core.IsNot.not;
import static ru.yandex.autotests.metrika.matchers.NoDuplicatesMatcher.hasNoDuplicates;

/**
 * Created by konkov on 25.07.2016.
 */
public class NoDuplicatesMatcherTest {

    @Test
    public void testDuplicates() {
        assertThat(of("A", "B", "A"), not(hasNoDuplicates()));
    }

    @Test
    public void testNoDuplicates() {
        assertThat(of("A", "B", "C"), hasNoDuplicates());
    }

    @Test(expected = AssertionError.class)
    public void testDuplicatesPositive() {
        assertThat(of("A", "B", "A"), hasNoDuplicates());
    }

    @Test(expected = AssertionError.class)
    public void testNoDuplicatesPositive() {
        assertThat(of("A", "B", "C"), not(hasNoDuplicates()));
    }
}
