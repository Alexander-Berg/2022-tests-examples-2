package ru.yandex.metrika.storage.hash;

import java.io.File;
import java.io.IOException;

import com.google.common.io.Files;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.storage.fileset.FileSetParameters;
import ru.yandex.metrika.storage.fileset.GenerationalFileSet;
import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.io.pool.RandomAccessFilePool;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author Arthur Suilin
 */
@Ignore
public class ExternalValueHashTableTest {

    private ExternalValueHashTable table;
    private File directory;
    private PersistentHashTable delegate;
    private RandomAccessFilePool pool;
    private GenerationalFileSet fileset;

    private ExternalValueHashTable createTable() {
        FileSetParameters fileSetParameters = new FileSetParameters();
        fileSetParameters.setBufferRoot(directory);
        fileSetParameters.setBufferSize(16);
        fileSetParameters.setMaxFileSize(64);
        fileSetParameters.setPool(pool);
        fileSetParameters.setUseWriteJournal(true);
        fileset = new GenerationalFileSet();
        fileset.setParams(fileSetParameters);
        try {
            fileset.afterPropertiesSet();
        } catch (Exception e) {
            e.printStackTrace();
        }
        ExternalValueHashTableParameters p = new ExternalValueHashTableParameters();
        p.setDelegate(delegate);
        p.setFileSet(fileset);
        p.setPayloadExtractor(new ExternalValueHashTable.PayloadExtractor(){
            @Override
            public byte[] extractPayload(byte[] value) {
                byte[] result = new byte[2];
                short v = (short)PrimitiveBytes.getInt(value);
                PrimitiveBytes.putShort(result, 0, v);
                return result;
            }
        });

        return new ExternalValueHashTable(p);
    }

    @Before
    public void setup() {
        pool = new RandomAccessFilePool(1);
        delegate = new PersistentHashTable(4, ExternalValueHashTable.POINTER_SIZE + 2, new HeapMemoryHashStorage(4 + ExternalValueHashTable.POINTER_SIZE + 2),
                new ExpansionFilter() {
                    @Override
                    public void onStartExpansion() {

                    }

                    @Override
                    public boolean isGoodEntity(byte[] key, byte[] value) {
                        short payload = PrimitiveBytes.getShort(value, ExternalValueHashTable.POINTER_SIZE);
                        return payload % 2 == 0;
                    }
                });
        Log4jSetup.basicSetup(Level.DEBUG);
        directory = Files.createTempDir();
        table = createTable();
    }

    @After
    public void teardown() throws Exception {
        fileset.destroy();
        pool.destroy();
        ru.yandex.metrika.util.io.Files.deleteRecursively(directory);
    }

    @Test
    public void testSingleValue() throws IOException {
        table.put(PrimitiveBytes.wrap(1), PrimitiveBytes.wrap(1));
        byte[] data = table.get(PrimitiveBytes.wrap(1));
        Assert.assertArrayEquals(PrimitiveBytes.wrap(1), data);
        table.gc();
        fileset.close();
        table = createTable();
        byte[] data2 = table.get(PrimitiveBytes.wrap(1));
        Assert.assertArrayEquals(PrimitiveBytes.wrap(1), data2);
    }

    @Test
    public void testManyValues() throws IOException {
        for (int i = 1; i <= 1000; i++) {
            table.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i));
        }
        for (int i = 1; i <= 1000; i++) {
            if (i % 2 == 0) {
                byte[] data = table.get(PrimitiveBytes.wrap(i));
                Assert.assertArrayEquals(PrimitiveBytes.wrap(i), data);
            }
        }
        for (int i = 1; i <= 1000; i++) {
            table.put(PrimitiveBytes.wrap(i), PrimitiveBytes.wrap(i*2));
        }
        for (int i = 1; i <= 1000; i++) {
            byte[] data = table.get(PrimitiveBytes.wrap(i));
            Assert.assertArrayEquals(PrimitiveBytes.wrap(i*2), data);
        }

        table.gc();
        fileset.close();
        table = createTable();
        for (int i = 1; i <= 1000; i++) {
            byte[] data = table.get(PrimitiveBytes.wrap(i));
            Assert.assertArrayEquals(PrimitiveBytes.wrap(i*2), data);
        }

        TestCallback callback = new TestCallback();
        table.iterate(callback);
        Assert.assertEquals(1000, callback.count);

    }

    private static class TestCallback implements ByteArrayHashTable.IteratorCallback {
        public int count;

        @Override
        public void onItem(byte[] key, byte[] value) {
            int iKey = PrimitiveBytes.getInt(key);
            int iValue = PrimitiveBytes.getInt(value);
            Assert.assertEquals(iKey, iValue / 2);
            ++count;
        }
    }



}
