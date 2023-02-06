package ru.yandex.metrika.util.io;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.zip.GZIPInputStream;

import com.google.common.io.ByteStreams;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import static org.junit.Assert.assertArrayEquals;

@RunWith(Parameterized.class)
public class GzipCompressingInputStreamTest {

    @Parameter
    public String dataInfo;

    @Parameter(1)
    public byte[] data;

    @Parameters(name = "{0}")
    public static Object[][] params() {
        return new Object[][]{
                {"Empty data", new byte[0]},
                {"Random data", RandomStringUtils.randomAlphanumeric(1024 * 1024).getBytes()}
        };
    }

    @Test
    public void test() throws Exception {
        InputStream uncompressedIn = new ByteArrayInputStream(data);
        InputStream compressedIn = new GzipCompressingInputStream(uncompressedIn);
        InputStream uncompressedOut = new GZIPInputStream(compressedIn);

        byte[] result = ByteStreams.toByteArray(uncompressedOut);

        assertArrayEquals("Test failed for: " + dataInfo, data, result);
    }
}
