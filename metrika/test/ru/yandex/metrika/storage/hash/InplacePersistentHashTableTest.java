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
 * @since 11.08.15
 */
@Ignore
public class InplacePersistentHashTableTest {
    private static final int COUNT = 10000;
    @Test
    public void testHashTable() throws Exception {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage storage = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t = new InlinePersistentHashTable(4,4,storage);
        for (int i = 1; i < COUNT*10; i++) {
            t.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        for (int i = 1; i < COUNT*10; i++) {
            byte[] bytes = t.get(PrimitiveBytes.wrap(i));
            Assert.assertEquals(i, PrimitiveBytes.getInt(bytes));
        }

        journalFile.delete();
        checkpointFile.delete();
    }

    @Test
    public void testHashTableChunkBorders() throws Exception {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage storage = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t = new InlinePersistentHashTable(24,36,storage);
        byte[] key = new byte[24];
        byte[] val = new byte[36];
        for (int i = 1; i < COUNT*10; i++) {
            PrimitiveBytes.putInt(key, i);
            PrimitiveBytes.putInt(val, i);
            t.put(key, val);
        }
        for (int i = 1; i < COUNT*10; i++) {
            PrimitiveBytes.putInt(key, i);
            byte[] bytes = t.get(key);
            Assert.assertEquals(i, PrimitiveBytes.getInt(bytes));
        }

        journalFile.delete();
        checkpointFile.delete();
    }



    @Test
    public void testRehash() throws IOException {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();

        LogFileHashStorage storage = new LogFileHashStorage(journalFile, checkpointFile);
        PersistentHashTable t = new PersistentHashTable(4,4,storage);

        for (int i = 1; i < COUNT*100; i++) {
            t.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }

        t.getStorage().flush();

        LogFileHashStorage storage2 = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t2 = new InlinePersistentHashTable(4, 4, storage2);
        for (int i = 1; i < COUNT*100; i++){
            byte[] res = t2.get(PrimitiveBytes.wrap(i));
            Assert.assertNotNull("i="+i, res);
            int val = PrimitiveBytes.getInt(res);
            Assert.assertEquals(i, val);
        }

        storage2.close();

        Assert.assertEquals(COUNT*100 - 1, t2.getSize());

        journalFile.delete();
        checkpointFile.delete();
    }

    @Test
    public void testExpire() throws IOException {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage storage = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t = new InlinePersistentHashTable(4, 4, storage, new ExpansionFilter() {
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
            if (i <= 7662) { // size * loadfactor
                if (i % 2 == 0) {
                    Assert.assertNotNull(res);
                } else {
                    Assert.assertNull("i="+i, res);
                }
            } else {
                Assert.assertNotNull(res);
            }
        }

        Assert.assertEquals(6168, t.getSize());

        journalFile.delete();
        checkpointFile.delete();
    }

    @Test
    public void testShrink() throws IOException {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage storage = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t = new InlinePersistentHashTable(4, 4, storage);

        for (int i = 1; i < COUNT; i++){
            t.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }

        t.getStorage().flush();

        LogFileHashStorage storage2 = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t2 = new InlinePersistentHashTable(4, 4, storage2, new ExpansionFilter() {
            @Override
            public void onStartExpansion() {
            }

            @Override
            public boolean isGoodEntity(byte[] key, byte[] value) {
                return PrimitiveBytes.getInt(key) < 100;
            }
        });

        t2.expandStorage();

        for (int i = 1; i < COUNT; i++){
            byte[] res = t2.get(PrimitiveBytes.wrap(i));
            if (i < 100) { // size * loadfactor
                Assert.assertNotNull("i="+i, res);
                Assert.assertEquals(i, PrimitiveBytes.getInt(res));
            } else {
                Assert.assertNull(res);
            }
        }

        Assert.assertEquals(99, t2.getSize());

        journalFile.delete();
        checkpointFile.delete();
    }
}
