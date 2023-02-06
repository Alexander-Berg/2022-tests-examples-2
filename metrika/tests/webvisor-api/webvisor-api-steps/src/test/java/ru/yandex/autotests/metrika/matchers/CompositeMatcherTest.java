package ru.yandex.autotests.metrika.matchers;

import org.junit.Test;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;

/**
 * Created by konkov on 20.07.2016.
 */
public class CompositeMatcherTest {

    @Test(expected = AssertionError.class)
    public void testFail() {
        assertThat(of(1,2,3), matchEvery(iterableWithSize(equalTo(2)), everyItem(greaterThan(0)), everyItem(greaterThan(1))));
    }
}
