package ru.yandex.metrika.storage.hash;

import java.io.File;

import junit.framework.Assert;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author serebrserg
 * @since 21.09.15
 */
@Ignore
public class InlinePersistentHashTableCountTest {
    public static final int COUNT = 100000;


    @Test
    public void testReload() throws Exception {
        Log4jSetup.basicSetup();
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage storage = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t = new InlinePersistentHashTable(4, 4, storage);

        for (int i = 1; i < COUNT; i++){
            t.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        ((AutoCloseable)t.getStorage()).close();

        LogFileHashStorage storage2 = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t2 = new InlinePersistentHashTable(4, 4, storage2);

        for (int i = COUNT; i < 2*COUNT; i++){
            t2.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        for (int i = 1; i < 2*COUNT; i++){
            byte[] res = t2.get(PrimitiveBytes.wrap(i));
            Assert.assertNotNull("i=" + i, res);
            Assert.assertEquals(i, PrimitiveBytes.getInt(res));
        }

            t2.expandStorage(new ExpansionFilter() {
                @Override
                public void onStartExpansion() {
                }

                @Override
                public boolean isGoodEntity(byte[] key, byte[] value) {
                    return PrimitiveBytes.getInt(key) % 2 == 0;
                }
            });

        Assert.assertEquals(COUNT - 1, t2.getSize());

        t2.expandStorage(new ExpansionFilter() {
            @Override
            public void onStartExpansion() {
            }

            @Override
            public boolean isGoodEntity(byte[] key, byte[] value) {
                return PrimitiveBytes.getInt(key) % 3 == 0;
            }
        });

        for (int i = 1; i < 2*COUNT; i++) {
            byte[] res = t2.get(PrimitiveBytes.wrap(i));
            if (i%6 == 0 ) {
                Assert.assertNotNull("i=" + i, res);
                Assert.assertEquals(i, PrimitiveBytes.getInt(res));
            } else{
                Assert.assertNull("i=" + i, res);
            }
        }

        Assert.assertEquals(COUNT / 3, t2.getSize());

        ((AutoCloseable)t2.getStorage()).close();

        LogFileHashStorage storage3 = new InplaceLogFileHashStorage(new ExpandableOffHeapHashStorage(checkpointFile, 8*1024), journalFile, checkpointFile);
        PersistentHashTable t3 = new InlinePersistentHashTable(4, 4, storage3);

        for (int i = 1; i < 2*COUNT; i++){
            t3.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }

        for (int i = 1; i < 2*COUNT; i++){
            byte[] res = t3.get(PrimitiveBytes.wrap(i));
            Assert.assertNotNull("i=" + i, res);
            Assert.assertEquals(i, PrimitiveBytes.getInt(res));
        }

        Assert.assertEquals(2 * COUNT - 1, t3.getSize());

        journalFile.delete();
        checkpointFile.delete();
    }
}
