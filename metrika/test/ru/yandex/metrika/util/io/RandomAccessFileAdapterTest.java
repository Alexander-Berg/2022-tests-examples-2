package ru.yandex.metrika.util.io;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

/**
 * @author Arthur Suilin
 */
public class RandomAccessFileAdapterTest {
    RandomAccessFileAdapter adapter;
    File f;
    RandomAccessFile raf;

    @Before
    public void setup() throws IOException {
        f = File.createTempFile("RandomAccessFileAdapterTest", "test");
        raf = new RandomAccessFile(f, "rw");
        raf.write(new byte[]{1,2,3,4});
        raf.close();
        raf = new RandomAccessFile(f, "r");
        adapter = new RandomAccessFileAdapter(raf);
    }

    @After
    public void destroy() throws IOException {
        raf.close();
        f.delete();
    }

    @Test
    public void testSingleRead() throws IOException {
        assertEquals(4, adapter.available());
        assertEquals(1, adapter.read());
        assertEquals(3, adapter.available());
        assertEquals(2, adapter.read());
        assertEquals(2, adapter.available());
        assertEquals(3, adapter.read());
        assertEquals(1, adapter.available());
        assertEquals(4, adapter.read());
        assertEquals(0, adapter.available());
        assertEquals(-1, adapter.read());
    }

    @Test
    public void testSkip() throws IOException {
        assertEquals(4, adapter.skip(100));
    }

    @Test
    public void testHugeSkip() throws IOException {
        assertEquals(4, adapter.skip(Long.MAX_VALUE));
    }

    @Test
    public void testBufferRead() throws IOException {
        byte[] buffer = new byte[5];
        assertEquals(4, adapter.read(buffer));
        assertArrayEquals(new byte[]{1, 2, 3, 4, 0}, buffer);
    }


}
