package ru.yandex.metrika.mobmet.crash.decoder.service.ios.group;

import org.junit.Assert;
import org.junit.Test;

public class NsExceptionNameTrimmerTest {

    private NsExceptionNameTrimmer nameTrimmer = new NsExceptionNameTrimmer();

    @Test
    public void testNormal() {
        String actual = nameTrimmer.trim("NSException");
        Assert.assertEquals("NSException", actual);
    }

    @Test
    public void testNormalWithSpecialCharacters() {
        String actual = nameTrimmer.trim("MetricaSample.SomeError.some_case");
        Assert.assertEquals("MetricaSample.SomeError.some_case", actual);
    }

    @Test
    public void testTrimWithSpecialCharacters() {
        String actual = nameTrimmer.trim("MetricaSample.SomeError.some_case(message: \"Some message\")");
        Assert.assertEquals("MetricaSample.SomeError.some_case(message: \"Some m...", actual);
    }

    @Test
    public void testReactUnhandled() {
        String actual = nameTrimmer.trim("RCTFatalException: Unhandled JS Exception: scrollToIndex out of range: -1 vs 19");
        Assert.assertEquals("RCTFatalException: Unhandled JS Exception: scrollT...", actual);
    }
}
