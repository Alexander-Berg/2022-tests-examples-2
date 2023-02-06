package ru.yandex.metrika.api.management.tests.medium.client;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.CounterSource;

public class CounterSourceTest {

    @Test
    public void getCounterSource() {
        CounterSource counterSource = CounterSource.fromVal("partner");
        Assert.assertEquals(CounterSource.partner, counterSource);
    }

    @Test
    public void getCounterSourceFromNullValue() {
        CounterSource counterSource = CounterSource.fromVal(null);
        Assert.assertNull(counterSource);
    }

    @Test
    public void getCounterSourceFromUndefinedValue() {
        CounterSource counterSource = CounterSource.fromVal("aaaa");
        Assert.assertNull(counterSource);
    }
}
