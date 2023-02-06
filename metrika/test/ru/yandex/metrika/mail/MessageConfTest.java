package ru.yandex.metrika.mail;

import java.util.HashMap;
import java.util.Map;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class MessageConfTest extends Assert {
    public MessageConf conf;

    @Before
    public void setUp() throws Exception {
        conf = new MessageConf();
        conf.addRetryConf("timeRanges", "0;;;;;;");
    }

    @After
    public void tearDown() throws Exception {
        conf = null;
    }

    @Test
    public void addRetryConf() {
        conf.addRetryConf("test", "value");

        HashMap<String, String> expected = new HashMap<>();
        expected.put("timeRanges", "0;;;;;;");
        expected.put("test", "value");

        assertEquals(
                expected,
                conf.getConf().get("retry")
        );
    }

    @Test
    public void getRetryConf() {
        HashMap<String, String> expected = new HashMap<>();
        expected.put("timeRanges", "0;;;;;;");

        assertEquals(
                expected,
                conf.getRetryConf()
        );
    }

    @Test
    public void getRetryConfJson() {
        assertEquals(
                "{\"timeRanges\":\"0;;;;;;\"}",
                conf.getRetryConfJson()
        );

    }

    @Test
    public void getConf() {
        Map<String, Map<String, String>> expected = new HashMap<>();
        expected.put("retry", new HashMap<>());
        expected.get("retry").put("timeRanges", "0;;;;;;");
        assertEquals(
                expected,
                conf.getConf()
        );

    }

    @Test
    public void setConf() {
        Map<String, Map<String, Object>> val = new HashMap<>();
        val.put("retry", new HashMap<>());
        val.get("retry").put("other", "value");

        conf.setConf(val);

        assertEquals(
                "{\"other\":\"value\"}",
                conf.getRetryConfJson()
        );

    }

    @Test
    public void isEmpty() {
        assertFalse(conf.isEmpty());
        assertTrue(new MessageConf().isEmpty());
    }

    @Test
    public void getConfJson() {
        assertEquals(
                "{\"retry\":{\"timeRanges\":\"0;;;;;;\"}}",
                conf.getConfJson()
        );
    }

    @Test
    public void fromJson() {
        MessageConf conf = MessageConf.fromJson("{\"retry\":{\"timeRanges\":\"0;;;;;;\"}}");
        HashMap<String, String> expected = new HashMap<>();
        expected.put("timeRanges", "0;;;;;;");

        assertEquals(
                expected,
                conf.getRetryConf()
        );

    }
}
