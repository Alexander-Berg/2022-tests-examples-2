package ru.yandex.metrika.storage.bloom;


import java.io.File;
import java.io.IOException;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;

/**
 * @author asuilin
 * @version $Id$
 * @since 21.01.11
 */
public class ExpirableBloomFilterTest {
    private BloomFilter f;
    private static final int capacity =100;

    @Before
    public void setup() throws IOException {
        File tempFile = File.createTempFile("bloom", ".test");
        tempFile.delete();
        float targetProbability = 0.01f;


        f = new BloomFilter<>(capacity, targetProbability, BitStoreFactory.DEFAULT_FACTORY, tempFile, new ExtraSerializer.IntSerializer(),
                time -> time % 2 == 0);


        for (int i = 0; i < capacity; i++) {
            f.add(PrimitiveBytes.wrap(i), i);
        }
    }

    @After
    public void tearDown() {
        if (f.getBackingStorage().exists()) {
            f.delete();
        }
    }


    private void testValidPositives(BloomFilter filter) {
        int validPositives = 0;
        for (int i = 0; i < capacity; i++) {
            if (filter.contains(PrimitiveBytes.wrap(i))) {
                ++validPositives;
            }
        }
        Assert.assertTrue(validPositives == capacity / 2);
    }

    @Test
    public void testExpand() throws Exception {
        f.add(PrimitiveBytes.wrap(101), 101);
        Assert.assertFalse(f.hasAvailableSpace());
        BloomFilter f2 = f.expand(x -> 1);
        testValidPositives(f2);
    }






}
