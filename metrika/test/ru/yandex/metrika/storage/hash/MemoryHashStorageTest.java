package ru.yandex.metrika.storage.hash;

import java.io.File;
import java.io.IOException;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.log.Log4jSetup;

/** @author Artur Suilin */
public class MemoryHashStorageTest {
    MemoryHashStorage hs;

    @Before
    public void setup() throws IOException {

        hs = new HeapMemoryHashStorage((long) MemoryHashStorage.DEFAULT_CHUNK_SIZE * 2);
        Log4jSetup.basicSetup();
    }

    @Test
    public void testNearChunkBounds() {
        hs.putNew(0, new byte[]{0}, 1, new byte[]{1});
        byte[] buf = new byte[1];
        hs.get(1, buf);
        Assert.assertArrayEquals(new byte[]{1}, buf);

        hs.putNew(MemoryHashStorage.DEFAULT_CHUNK_SIZE *2-2, new byte[]{2}, MemoryHashStorage.DEFAULT_CHUNK_SIZE *2-1, new byte[]{3});
        hs.get(MemoryHashStorage.DEFAULT_CHUNK_SIZE *2-1, buf);
        Assert.assertArrayEquals(new byte[]{3}, buf);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testBadOffset() {
        hs.putNew(MemoryHashStorage.DEFAULT_CHUNK_SIZE *2, new byte[]{4}, MemoryHashStorage.DEFAULT_CHUNK_SIZE *2+1, new byte[]{5});
    }

    @Test
    public void testChunkCrossing() {
        hs.putNew(MemoryHashStorage.DEFAULT_CHUNK_SIZE -1, new byte[]{2,3}, MemoryHashStorage.DEFAULT_CHUNK_SIZE +1, new byte[]{3, 4});
        byte[] buf = new byte[2];
        hs.get(MemoryHashStorage.DEFAULT_CHUNK_SIZE -1, buf);
        Assert.assertArrayEquals(new byte[]{2, 3}, buf);
    }

    @Test
    public void testBigData() {
        byte[] bigArray = new byte[MemoryHashStorage.DEFAULT_CHUNK_SIZE * 2-1];
        for (int i = 0; i < bigArray.length; i++) {
            bigArray[i] = (byte)(i % Byte.MAX_VALUE);
        }
        byte[] bigBuffer = new byte[MemoryHashStorage.DEFAULT_CHUNK_SIZE * 2-1];
        hs.putNew(0, bigArray, MemoryHashStorage.DEFAULT_CHUNK_SIZE *2-1, new byte[]{127});
        hs.get(0, bigBuffer);
        for (int i = 0; i < bigBuffer.length; i++) {
            byte b = bigBuffer[i];
            Assert.assertEquals(i % Byte.MAX_VALUE, b);
        }
    }

    @Test
    public void testCheckpoint() throws IOException {
        File f = File.createTempFile("ArrayMemoryHashStorageTest", "test");
        //File f = new File("/tmp/mhs");
        byte[] bigArray = new byte[MemoryHashStorage.DEFAULT_CHUNK_SIZE * 2-1];
        for (int i = 0; i < bigArray.length; i++) {
            bigArray[i] = (byte)(i % Byte.MAX_VALUE);
        }
        byte[] bigBuffer = new byte[MemoryHashStorage.DEFAULT_CHUNK_SIZE * 2-1];
        hs.putNew(0, bigArray, MemoryHashStorage.DEFAULT_CHUNK_SIZE *2-1, new byte[]{127});
        hs.dump(f);
        MemoryHashStorage hs2 = new HeapMemoryHashStorage(f, 1024);
        Assert.assertEquals(hs.getSize(), hs2.getSize());
        Assert.assertEquals(hs.getCount(), hs2.getCount());
        hs2.get(0, bigBuffer);
        for (int i = 0; i < bigBuffer.length; i++) {
            byte b = bigBuffer[i];
            Assert.assertEquals(i % Byte.MAX_VALUE, b);
        }

        f.delete();
    }
}
