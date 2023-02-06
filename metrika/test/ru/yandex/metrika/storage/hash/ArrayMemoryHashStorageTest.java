package ru.yandex.metrika.storage.hash;


import java.io.File;
import java.io.IOException;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

/**
 * @author Arthur Suilin
 */

@SuppressWarnings("deprecation")
public class ArrayMemoryHashStorageTest {

    ArrayMemoryHashStorage hs;

    @Before
    public void setup() throws IOException {

        hs = new ArrayMemoryHashStorage((long) ArrayMemoryHashStorage.CHUNK_SIZE * 2);
    }

    @Test
    public void testNearChunkBounds() {
        hs.putNew(0, new byte[]{0}, 1, new byte[]{1});
        byte[] buf = new byte[1];
        hs.get(1, buf);
        Assert.assertArrayEquals(new byte[]{1}, buf);

        hs.putNew(ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 2, new byte[]{2}, ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1, new byte[]{3});
        hs.get(ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1, buf);
        Assert.assertArrayEquals(new byte[]{3}, buf);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testBadOffset() {
        hs.putNew(ArrayMemoryHashStorage.CHUNK_SIZE * 2, new byte[]{4}, ArrayMemoryHashStorage.CHUNK_SIZE * 2 + 1, new byte[]{5});
    }

    @Test
    public void testChunkCrossing() {
        hs.putNew(ArrayMemoryHashStorage.CHUNK_SIZE - 1, new byte[]{2, 3}, ArrayMemoryHashStorage.CHUNK_SIZE + 1, new byte[]{3, 4});
        byte[] buf = new byte[2];
        hs.get(ArrayMemoryHashStorage.CHUNK_SIZE - 1, buf);
        Assert.assertArrayEquals(new byte[]{2, 3}, buf);
    }

    @Test
    public void testBigData() {
        byte[] bigArray = new byte[ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1];
        for (int i = 0; i < bigArray.length; i++) {
            bigArray[i] = (byte) (i % Byte.MAX_VALUE);
        }
        byte[] bigBuffer = new byte[ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1];
        hs.putNew(0, bigArray, ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1, new byte[]{127});
        hs.get(0, bigBuffer);
        for (int i = 0; i < bigBuffer.length; i++) {
            byte b = bigBuffer[i];
            Assert.assertEquals(i % Byte.MAX_VALUE, b);
        }
    }

    @Test
    public void testCheckpoint() throws IOException {
        File f = File.createTempFile("ArrayMemoryHashStorageTest", "test");
        byte[] bigArray = new byte[ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1];
        for (int i = 0; i < bigArray.length; i++) {
            bigArray[i] = (byte) (i % Byte.MAX_VALUE);
        }
        byte[] bigBuffer = new byte[ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1];
        hs.putNew(0, bigArray, ArrayMemoryHashStorage.CHUNK_SIZE * 2 - 1, new byte[]{127});
        hs.dump(f);
        ArrayMemoryHashStorage hs2 = new ArrayMemoryHashStorage(f, 1024);
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
