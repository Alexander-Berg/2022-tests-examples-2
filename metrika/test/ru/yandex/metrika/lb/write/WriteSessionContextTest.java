package ru.yandex.metrika.lb.write;

import org.junit.Assert;
import org.junit.Test;

public class WriteSessionContextTest {

    @Test
    public void testLbDc() {
        Assert.assertEquals("vla", WriteSessionContext.getLbDc("rt3.vla--metrika@test--metrika-reduced-webvisor-to-crypta-log").get());
        Assert.assertEquals("sas", WriteSessionContext.getLbDc("rt3.sas--metrika--wv-scrolls-log").get());
    }

}
