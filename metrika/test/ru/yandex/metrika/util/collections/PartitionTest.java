package ru.yandex.metrika.util.collections;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.junit.Test;

import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.empty;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.util.collections.Partition.byShares;

/**
 * Created by graev on 18/07/16.
 */
public class PartitionTest {
    @Test
    public void testByShares1() {
        assertThat(byShares(ImmutableList.of(1, 2, 3), ImmutableList.of(0.3, 0.7)), contains(
                contains(1),
                contains(2, 3)
        ));
    }

    @Test
    public void testNumberOfHypothesesGreaterThanNumberOfUsers() {
        // Or whatever else, but not IndexOutOfBoundsException
        assertThat(
                byShares(
                        ImmutableList.of(1, 2, 3),
                        ImmutableList.of(0.2, 0.2, 0.2, 0.2, 0.2)
                ),
                contains(
                        (Matcher) contains(1),
                        (Matcher) contains(2),
                        (Matcher) contains(3),
                        empty(),
                        empty()
                ));
    }
}
