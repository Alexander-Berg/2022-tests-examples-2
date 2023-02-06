package ru.yandex.metrika.mobmet.crash.breakpad;

import java.io.IOException;
import java.io.InputStream;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;
import org.skyscreamer.jsonassert.JSONAssert;

import static org.junit.Assert.assertTrue;

public class MinidumpStackwalkTest {

    public static final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    public void checkExample() throws Exception {
        byte[] crashData = loadResource("crash/example.dmp");
        Minidump minidump = MinidumpStackwalk.parse(crashData);

        String actualData = objectMapper.writerFor(Minidump.class).writeValueAsString(minidump);
        String expectedData = new String(loadResource("crash/example.expected.json"));

        JSONAssert.assertEquals(expectedData, actualData, true);
    }

    @Test(expected = IllegalArgumentException.class)
    public void checkCorrupted() throws Exception {
        byte[] crashData = loadResource("crash/corrupted.dmp");
        MinidumpStackwalk.parse(crashData);
    }

    @Test
    public void checkLogIsDisabled() {
        assertTrue("JNI Breakpad must be built without -DBPLOG_MINIMUM_SEVERITY setting", MinidumpStackwalk.isLogDisabled());
    }

    private static byte[] loadResource(String resourcePath) throws IOException {
        InputStream resourceAsStream = MinidumpStackwalkTest.class
                .getClassLoader()
                .getResourceAsStream(resourcePath);

        if (resourceAsStream == null) {
            throw new IOException("Missing resource: " + resourcePath);
        }

        return resourceAsStream.readAllBytes();
    }

}
