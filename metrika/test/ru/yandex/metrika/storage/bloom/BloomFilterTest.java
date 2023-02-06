package ru.yandex.metrika.storage.bloom;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author asuilin
 * @version $Id$
 * @since 20.12.10
 */
@Ignore
public class BloomFilterTest {
    private BloomFilter<Integer> f;
    private static final int capacity = 1000 * 1 * 200;
    float targetProbability = 0.01f;

    private static byte[] itob(int value) {
        return PrimitiveBytes.wrap(value);
    }

    @Before
    public void setup() throws IOException {
        File tempFile = File.createTempFile("bloom", ".test");
        Log4jSetup.basicSetup(Level.DEBUG);
        f = new BloomFilter<>(1024, targetProbability, BitStoreFactory.DEFAULT_FACTORY, tempFile, new ExtraSerializer.IntSerializer(), null);
        for (int i = 0; i < capacity; i++) {
            if (i % 100000 == 0) {
                System.out.println(i + " elements added");
            }
            if (!f.hasAvailableSpace()) {
                f = f.expand(x -> 1);
            }
            f.add(itob(i), i);
        }
    }

    @After
    public void tearDown() {
        if (f.getBackingStorage().exists()) {
            f.delete();
        }
    }

    @Test
    public void testContainsSimple() throws Exception {

        testValidPositives(f);
    }



    @Test
    public void testExpand() throws Exception {
        f.add(itob(capacity + 1), capacity + 1);
        BloomFilter f2 = f.expand(x -> 1);
        testValidPositives(f2);
    }

    @Test(expected=BloomFilterException.class)
    public void testCapacityLimit() throws Exception {
        for (int i = 0; i < capacity; i++) {
            f.add(itob(i), i);
        }
    }

    @Test
    public void testDelete() throws Exception {
        f.delete();
        assert !f.getBackingStorage().exists();
    }

    /*
    @Test(expected=BloomFilterException.class)
    public void testClose() throws Exception {
        f.close();
        f.add(new IntKey(1000));
    }
    */


    private void testValidPositives(BloomFilter filter) {
        int validPositives = 0;
        for (int i = 0; i < capacity; i++) {
            if (i % 1000000 == 0) {
                System.out.println(i + " elements checked");
            }
            if (filter.contains(itob(i))) {
                ++validPositives;
            }
        }
        Assert.assertEquals(capacity, validPositives);
    }

    @Test
    public void testContains() throws Exception {
        testValidPositives(f);
        int falseProbes = capacity * 100;
        int falsePositives = 0;
        for (int i = capacity; i < falseProbes; i++) {
            if (f.contains(itob(i))) {
                falsePositives++;
            }
        }
        System.out.println(String.format("False positives: %d out of %d, %f ",falsePositives, falseProbes, (float)falsePositives/falseProbes));
        Assert.assertTrue(falsePositives < falseProbes  * targetProbability * 1.1); //
    }


    @Test
    public void testSplit() throws IOException {
        File dest = File.createTempFile("bloom_split", ".test");
        DataOutputStream out = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(dest)));
        long count = f.split(out, integer -> integer < 50);
        out.close();
        Assert.assertEquals(50, count);

        BloomFilter<Integer> result = new BloomFilter<>(targetProbability, BitStoreFactory.DEFAULT_FACTORY, dest, new ExtraSerializer.IntSerializer(), null);
        for (int i = 0; i < 50; i++) {
            Assert.assertTrue(result.contains(itob(i)));
        }
        result.close();
        IOUtils.safeDelete(dest);
    }

    @Test
    public void testMerge() throws IOException {
        File mergeChunk = File.createTempFile("bloom_merge", ".test");
        BloomFilter<Integer> mergeProducer = new BloomFilter<>(targetProbability, BitStoreFactory.DEFAULT_FACTORY, mergeChunk, new ExtraSerializer.IntSerializer(), null);
        for (int i = 100; i < 200; i++) {
            mergeProducer.add(PrimitiveBytes.wrap(i), i);
        }
        mergeProducer.close();
        Assert.assertEquals(100, f.merge(mergeChunk));
        f = f.expand(x -> 1);
        for (int i = 100; i < 200; i++) {
            Assert.assertTrue(f.contains(PrimitiveBytes.wrap(i)));
        }
        IOUtils.safeDelete(mergeChunk);

    }



}
