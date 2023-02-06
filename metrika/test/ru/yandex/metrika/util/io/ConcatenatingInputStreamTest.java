package ru.yandex.metrika.util.io;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.junit.Assert;
import org.junit.Test;

/**
 * @author Arthur Suilin
 */
public class ConcatenatingInputStreamTest {

    @Test
    public void testEmpty() throws IOException {
        List<InputStream> src = Collections.emptyList();
        ConcatenatingInputStream stream = new ConcatenatingInputStream(src.iterator());
        Assert.assertEquals(0, stream.available());
        Assert.assertEquals(-1, stream.read());
    }

    @Test
    public void testOne() throws IOException {
        List<InputStream> lst = Arrays.asList(new InputStream[]{new ByteArrayInputStream(new byte[]{1})});
        ConcatenatingInputStream stream = new ConcatenatingInputStream(lst.iterator());
        Assert.assertEquals(1, stream.available());
        Assert.assertEquals(1, stream.read());
        Assert.assertEquals(-1, stream.read());
    }

    private ConcatenatingInputStream createTwoStream() {
        List<InputStream> lst = Arrays.asList(new InputStream[]{
                new ByteArrayInputStream(new byte[]{1, 2, 3}),
                new ByteArrayInputStream(new byte[]{4, 5, 6}),
        });
        return new ConcatenatingInputStream(lst.iterator());
    }

    @Test
    public void testTwoSingleRead() throws IOException {
        ConcatenatingInputStream stream = createTwoStream();
        Assert.assertEquals(3, stream.available());
        Assert.assertEquals(1, stream.read());
        Assert.assertEquals(2, stream.available());
        Assert.assertEquals(2, stream.read());
        Assert.assertEquals(1, stream.available());
        Assert.assertEquals(3, stream.read());
        Assert.assertEquals(0, stream.available());
        Assert.assertEquals(4, stream.read());
        Assert.assertEquals(5, stream.read());
        Assert.assertEquals(6, stream.read());
        Assert.assertEquals(-1, stream.read());
    }

    @Test
    public void testTwoBigBuffer() throws IOException {
        ConcatenatingInputStream stream = createTwoStream();
        byte[] buffer = new byte[7];
        int result = stream.read(buffer);
        Assert.assertEquals(3, result);
        Assert.assertArrayEquals(new byte[]{1,2,3,0,0,0, 0}, buffer);
        int result2 = stream.read(buffer);
        Assert.assertEquals(3, result2);
        Assert.assertArrayEquals(new byte[]{4,5,6,0,0,0, 0}, buffer);
    }

}
