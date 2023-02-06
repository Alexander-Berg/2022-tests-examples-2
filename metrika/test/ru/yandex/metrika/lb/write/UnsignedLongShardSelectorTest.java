package ru.yandex.metrika.lb.write;

import org.junit.Assert;
import org.junit.Test;

/**
 * {@link UnsignedLongShardSelector}.
 */
public class UnsignedLongShardSelectorTest {

    @Test
    public void minUnsignedLongToZero() {
        UnsignedLongShardSelector<Long> selector = new UnsignedLongShardSelector<>(2, value -> value);
        Assert.assertEquals(0, selector.apply(0L).intValue());
    }

    @Test
    public void beforeMaxUnsignedLongToLast() {
        UnsignedLongShardSelector<Long> selector = new UnsignedLongShardSelector<>(2, value -> value);
        long value = -1L - 1;
        Assert.assertEquals(1, selector.apply(value).intValue());
    }

    @Test
    public void maxUnsignedLongToLast() {
        UnsignedLongShardSelector<Long> selector = new UnsignedLongShardSelector<>(2, value -> value);
        long value = -1L;
        Assert.assertEquals(1, selector.apply(value).intValue());
    }

}
