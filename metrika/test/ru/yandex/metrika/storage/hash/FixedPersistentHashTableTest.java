package ru.yandex.metrika.storage.hash;

import java.io.File;
import java.io.IOException;

import junit.framework.Assert;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author serebrserg
 * @since 07.08.15
 */
@Ignore
public class FixedPersistentHashTableTest {
    private static final int COUNT = 10000;
    @Test
    public void testHashSet() throws Exception {
        Log4jSetup.basicSetup();
        MemoryHashStorage hs = new OffHeapHashStorage(4*15000);
        PersistentHashTable t = new FixedPersistentHashTable(4,0,hs);
        for (int i = 1; i < COUNT; i++) {
            t.put(PrimitiveBytes.wrap(i * 10), new byte[0]);
        }
        for (int i = 1; i < COUNT; i++) {
            byte[] bytes = t.get(PrimitiveBytes.wrap(i * 10));
            System.out.println(bytes.length);
        }
    }

    @Test
    public void testRehash() throws IOException {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();

        LogFileHashStorage storage = new LogFileHashStorage(journalFile, checkpointFile);
        PersistentHashTable t = new PersistentHashTable(4,4,storage);

        for (int i = 1; i < COUNT; i++) {
            t.put(PrimitiveBytes.wrap(i * 10), PrimitiveBytes.wrap(i * 10));
        }

        storage.checkpoint();
        storage.close();


        LogFileHashStorage storage2 = new LogFileHashStorage(new OffHeapHashStorage(checkpointFile, 8*1024*1024*100, true), journalFile, checkpointFile);
        PersistentHashTable t2 = new FixedPersistentHashTable(4, 4, storage2);
        for (int i = 1; i < COUNT; i++){
            byte[] res = t2.get(PrimitiveBytes.wrap(i*10));
            Assert.assertNotNull(res);
            int val = PrimitiveBytes.getInt(res);
            Assert.assertEquals(i*10, val);
        }
        t2.expandStorage();
        storage2.checkpoint();
        storage2.close();

        LogFileHashStorage storage3 = new LogFileHashStorage(new OffHeapHashStorage(checkpointFile, 8*1024*1024*100, true), journalFile, checkpointFile);
        PersistentHashTable t3 = new FixedPersistentHashTable(4, 4, storage3);
        for (int i = 1; i < COUNT; i++){
            byte[] res = t3.get(PrimitiveBytes.wrap(i*10));
            Assert.assertNotNull(res);
            int val = PrimitiveBytes.getInt(res);
            Assert.assertEquals(i * 10, val);
        }
        storage3.close();

        Assert.assertEquals(COUNT - 1, t3.getSize());

        journalFile.delete();
        checkpointFile.delete();
    }

    @Test
    public void testExpire() throws IOException {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage storage = new LogFileHashStorage(new OffHeapHashStorage(checkpointFile, 8*1024*12, true), journalFile, checkpointFile);
        PersistentHashTable t = new FixedPersistentHashTable(4, 4, storage, new ExpansionFilter() {
            @Override
            public void onStartExpansion() {
            }

            @Override
            public boolean isGoodEntity(byte[] key, byte[] value) {
                return PrimitiveBytes.getInt(key)%2 == 0;
            }
        });

        for (int i = 1; i < COUNT; i++){
            t.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }

        for (int i = 1; i < COUNT; i++){
            byte[] res = t.get(PrimitiveBytes.wrap(i));
            if (i <= 8601) { // size * loadfactor
                if (i % 2 == 0) {
                    Assert.assertNotNull(res);
                } else {
                    Assert.assertNull(res);
                }
            } else {
                Assert.assertNotNull(res);
            }
        }

        Assert.assertEquals(5698, t.getSize());

        journalFile.delete();
        checkpointFile.delete();
    }
}
