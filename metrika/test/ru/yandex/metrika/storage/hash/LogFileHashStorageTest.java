package ru.yandex.metrika.storage.hash;

import java.io.Closeable;
import java.io.File;
import java.io.IOException;

import org.apache.logging.log4j.Level;
import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.log.Log4jSetup;

/** @author Arthur Suilin */
@Ignore
public class LogFileHashStorageTest {
    @Test
    public void test() throws IOException {
        Log4jSetup.basicSetup(Level.DEBUG);
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        LogFileHashStorage sts = new LogFileHashStorage(new HeapMemoryHashStorage(10), journalFile, checkpointFile);
        PersistentHashTable pts = new PersistentHashTable(4,4, sts);
        sts.replayJournalTo(pts);
        for (int i = 1; i < 10000; i++) {
              pts.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        //sts.checkpoint();
        ((Closeable)pts.getStorage()).close();

        sts = new LogFileHashStorage(journalFile, checkpointFile);
        pts = new PersistentHashTable(4,4, sts);
        sts.replayJournalTo(pts);
        for (int i = 1; i < 10000; i++) {
            //if (i > 9000) System.out.println(i);
            byte[] test = PrimitiveBytes.wrap(i);
            byte[] value = pts.get(test);
            Assert.assertArrayEquals(test, value);
        }
        sts.close();
        journalFile.delete();
        checkpointFile.delete();


    }

    @Test
    public void test2() throws IOException {
        Log4jSetup.basicSetup(Level.DEBUG);
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        LogFileHashStorage sts = new LogFileHashStorage(ThreadSafeOffHeapHashStorage.FACTORY.makeStorage(null, 10), journalFile, checkpointFile);
        PersistentHashTable pts = new PersistentHashTable(4,4, sts);
        sts.replayJournalTo(pts);
        for (int i = 1; i < 10000; i++) {
            pts.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        //sts.checkpoint();
        ((Closeable)pts.getStorage()).close();

        sts = new LogFileHashStorage(journalFile, checkpointFile);
        pts = new PersistentHashTable(4,4, sts);
        sts.replayJournalTo(pts);
        for (int i = 1; i < 10000; i++) {
            //if (i > 9000) System.out.println(i);
            byte[] test = PrimitiveBytes.wrap(i);
            byte[] value = pts.get(test);
            Assert.assertArrayEquals(test, value);
        }
        sts.close();
        journalFile.delete();
        checkpointFile.delete();


    }

    @Test
    public void testExpansion() throws IOException {
        Log4jSetup.basicSetup(Level.DEBUG);
        File journalFile = File.createTempFile("journal", "test");
        File checkpointFile = File.createTempFile("checkpoint", "test");
        checkpointFile.delete();
        LogFileHashStorage sts = new LogFileHashStorage(journalFile, checkpointFile);
        PersistentHashTable pts = new PersistentHashTable(8,8, sts);
        sts.replayJournalTo(pts);
        pts.put(PrimitiveBytes.wrap(1L), PrimitiveBytes.wrap(123L));
        for (long i = 1; i < 10000000; i++) {
            pts.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        //sts.checkpoint();
        ((Closeable)pts.getStorage()).close();

        journalFile.delete();
        checkpointFile.delete();
    }

}
