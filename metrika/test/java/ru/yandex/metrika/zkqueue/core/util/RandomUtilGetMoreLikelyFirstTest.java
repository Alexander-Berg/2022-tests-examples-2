package ru.yandex.metrika.zkqueue.core.util;

import java.util.Collection;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import org.mockito.Mockito;

@RunWith(Parameterized.class)
public class RandomUtilGetMoreLikelyFirstTest {

    @Parameter
    public List<Integer> items;

    @Parameter(1)
    public double randomWeight;

    @Parameter(2)
    public Integer expectedItem;

    @Parameters(name = "Input: {0}. Random weight: {1}")
    public static Collection<Object[]> params() {
        return List.of(
                // Random variable distribution: 50%, 25%, 12.5%, 6.25%, 3.125%, ... etc.
                new Object[]{List.of(1, 2, 3, 4), 0.00, 1},
                new Object[]{List.of(1, 2, 3, 4), 0.50, 2},
                new Object[]{List.of(1, 2, 3, 4), 0.75, 3},
                new Object[]{List.of(1, 2, 3, 4), 0.875, 4},
                new Object[]{List.of(1, 2, 3, 4), 999.0, 4}
        );
    }

    @Test
    public void checkMoreLikelyFirst() {
        ThreadLocalRandom random = Mockito.mock(ThreadLocalRandom.class);
        Mockito.when(random.nextDouble()).thenReturn(randomWeight);

        Integer item = RandomUtil.getMoreLikelyFirst(items, random);
        Assert.assertEquals(expectedItem, item);
    }
}
