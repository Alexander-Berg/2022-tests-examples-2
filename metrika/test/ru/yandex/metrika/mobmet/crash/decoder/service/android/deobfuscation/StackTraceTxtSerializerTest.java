package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_JVM_CRASH;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.getExpectedStackTraceAsText;

public class StackTraceTxtSerializerTest {

    private static final String EXPECTED_STACK_TRACE_AS_TEXT = getExpectedStackTraceAsText();

    private final StackTraceTxtSerializer stackTraceTxtSerializer = new StackTraceTxtSerializer();

    @Test
    public void testToText() {
        String actual = stackTraceTxtSerializer.toText(EXPECTED_JVM_CRASH);
        assertEquals(EXPECTED_STACK_TRACE_AS_TEXT, actual);
    }
}
