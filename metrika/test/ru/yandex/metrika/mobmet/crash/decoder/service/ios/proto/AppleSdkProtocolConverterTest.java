package ru.yandex.metrika.mobmet.crash.decoder.service.ios.proto;

import java.util.List;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.ios.protocol.NonFatalParameter;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;

public class AppleSdkProtocolConverterTest {

    @Test
    public void testEmptyString() {
        List<NonFatalParameter> actual = AppleSdkProtocolConverter.convertParameters("");
        Assert.assertEquals(emptyList(), actual);
    }

    @Test
    public void testEmpty() {
        List<NonFatalParameter> actual = AppleSdkProtocolConverter.convertParameters("{}");
        Assert.assertEquals(emptyList(), actual);
    }

    @Test
    public void testSimple() {
        List<NonFatalParameter> actual = AppleSdkProtocolConverter.convertParameters("{\"key\":4}");
        Assert.assertEquals(singletonList(createNonFatal("key", "4")), actual);
    }

    @Test
    public void testManyParams() {
        List<NonFatalParameter> actual = AppleSdkProtocolConverter.convertParameters("{\"key\":4, \n \"key2\": \"test\"}");
        List<NonFatalParameter> expected = List.of(createNonFatal("key", "4"), createNonFatal("key2", "test"));
        Assert.assertEquals(expected, actual);
    }

    @Test
    public void testNull() {
        List<NonFatalParameter> actual = AppleSdkProtocolConverter.convertParameters("{\"key\":4, \n \"key2\": null}");
        List<NonFatalParameter> expected = List.of(createNonFatal("key", "4"), createNonFatal("key2", null));
        Assert.assertEquals(expected, actual);
    }

    @Test
    public void testNested() {
        String json = "{\"key\":4, \n \"key2\": { \"nested\": 0}, \"key3\": [{ \"nested4\": 0}]}";
        List<NonFatalParameter> actual = AppleSdkProtocolConverter.convertParameters(json);
        List<NonFatalParameter> expected = List.of(
                createNonFatal("key", "4"),
                createNonFatal("key2", "{\"nested\":0}"),
                createNonFatal("key3", "[{\"nested4\":0}]"));
        Assert.assertEquals(expected, actual);
    }

    private static NonFatalParameter createNonFatal(String key, String value) {
        NonFatalParameter param = new NonFatalParameter();
        param.setKey(key);
        param.setValue(value);
        return param;
    }
}
