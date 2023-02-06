package ru.yandex.metrika.storage.merger.index;

import java.io.File;
import java.util.Random;
import java.util.function.Predicate;

import com.google.common.io.Files;
import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Test;
import org.springframework.util.FileSystemUtils;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.log.Log4jSetup;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertFalse;
import static junit.framework.Assert.assertTrue;

/**
 * @author jkee
 */

public class SparseIndexTest {

    private static class Entity {
        private Entity(int key, String value) {
            this.key = key;
            this.value = value;
        }
        int key;
        String value;
    }

    private SparseIndex<Entity, Integer> index;

    @Before
    public void setUp() throws Exception {
        index = new SparseIndex<Entity, Integer>(4, "index", 100) {
            @Override
            public byte[] keyToByteArray(Integer key) {
                return PrimitiveBytes.wrap(key);
            }

            @Override
            public Integer keyFromByteArray(byte[] key) {
                return PrimitiveBytes.getInt(key);
            }

            @Override
            public Integer keyOf(Entity value) {
                return value.key;
            }
        };
    }

    @Test
    public void testIndex() throws Exception {
        Log4jSetup.basicSetup(Level.ERROR);
        File tmp = Files.createTempDir();
        Indexer<Entity> indexer = index.createIndexer(tmp);
        Random rand = new Random(1001);
        for (int i = 0; i < 10000; i++) {
            long offset = i * 10;
            Entity entity1 = new Entity(i, StringUtil.generateRandomString(10, rand));
            Entity entity2 = new Entity(i, StringUtil.generateRandomString(10, rand));
            indexer.onItem(entity1, offset);
            indexer.onItem(entity2, offset + 5);
        }
        indexer.finish();
        /*куски по 100 записей
        * в куске 50 индексов
        */
        for (int i = 0; i < 200; i++) {
            for (int j = 0; j < 50; j++) {
                int key = i * 50 + j + 1;
                if (key < 10000) assertEquals("id: " + key, i * 500, index.getFileOffset(tmp, key));
            }
        }
        assertEquals("id: " + 0, 0, index.getFileOffset(tmp, 0));
        FileSystemUtils.deleteRecursively(tmp);
    }

    @Test
    public void testIndexSerAlone() throws Exception {
        Log4jSetup.basicSetup(Level.ERROR);
        File tmp = Files.createTempDir();
        Indexer<Entity> indexer = index.createIndexer(tmp);
        Random rand = new Random(1001);
            long offset = 10;
            Entity entity1 = new Entity(1, StringUtil.generateRandomString(10, rand));
            Entity entity2 = new Entity(1, StringUtil.generateRandomString(10, rand));
            indexer.onItem(entity1, offset);
            indexer.onItem(entity2, offset + 5);
        indexer.finish();
        /*куски по 100 записей
        * в куске 50 индексов
        */
        MemoryIndex<Entity, Integer> mIndex = index.indexFromFile(tmp);
        assertEquals("id: " + 0, 10, mIndex.getFileOffset(1));

        FileSystemUtils.deleteRecursively(tmp);
    }

    @Test
    public void testMemoryIndex() throws Exception {
        Log4jSetup.basicSetup();
        File tmp = Files.createTempDir();
        Indexer<Entity> indexer = index.createIndexer(tmp);
        Random rand = new Random(1001);
        for (int i = 0; i < 10000; i++) {
            long offset = i * 10;
            Entity entity1 = new Entity(i, StringUtil.generateRandomString(10, rand));
            Entity entity2 = new Entity(i, StringUtil.generateRandomString(10, rand));
            indexer.onItem(entity1, offset);
            indexer.onItem(entity2, offset + 5);
        }
        MemoryIndex<Entity, Integer> mi = (MemoryIndex<Entity, Integer>) indexer.finish();


        /*куски по 100 записей
        * в куске 50 индексов
        */
        for (int i = 0; i < 200; i++) {
            for (int j = 0; j < 50; j++) {
                int key = i * 50 + j + 1;
                if (key < 10000) assertEquals("id: " + key, i * 500, mi.getFileOffset(key));
            }
        }
        assertEquals("id: " + 0, 0, mi.getFileOffset(0));

        mi = index.indexFromFile(tmp);

        for (int i = 0; i < 200; i++) {
            for (int j = 0; j < 50; j++) {
                int key = i * 50 + j + 1;
                if (key < 10000) assertEquals("id: " + key, i * 500, mi.getFileOffset(key));
            }
        }
        assertEquals("id: " + 0, 0, mi.getFileOffset(0));

        FileSystemUtils.deleteRecursively(tmp);
    }

    @Test
    public void testBigGap() throws Exception {
        Log4jSetup.basicSetup(Level.ERROR);
        File tmp = Files.createTempDir();
        Indexer<Entity> indexer = index.createIndexer(tmp);
        Random rand = new Random(1001);
        for (int i = 0; i < 10; i++) {
            for (int j = 0; j < 1000; j++) {
                long offset = i * 10000 + j * 10;
                Entity entity = new Entity(i, StringUtil.generateRandomString(10, rand));
                indexer.onItem(entity, offset);
            }
        }
        MemoryIndex<Entity, Integer> mi = (MemoryIndex<Entity, Integer>) indexer.finish();
        for (int i = 1; i < 10; i++) {
            assertEquals("id: " + i, i * 10000 - 1000, index.getFileOffset(tmp, i));
            assertEquals("id: " + i, i * 10000 - 1000, mi.getFileOffset(i));
        }
        assertEquals("id: " + 0, 0, index.getFileOffset(tmp, 0));
        assertEquals("id: " + 0, 0, mi.getFileOffset(0));

        FileSystemUtils.deleteRecursively(tmp);
    }

    @Test
    public void testPredicate() throws Exception {
        Log4jSetup.basicSetup();
        File tmp = Files.createTempDir();
        Indexer<Entity> indexer = index.createIndexer(tmp);
        Random rand = new Random(1001);
        for (int i = 0; i < 10000; i++) {
            long offset = i * 10;
            Entity entity = new Entity(i, StringUtil.generateRandomString(10, rand));
            indexer.onItem(entity, offset);
        }
        indexer.finish();
        for (int i = 0; i < 100; i++) {
            for (int j = 0; j < 100; j++) {
                int key = i * 100 + j;
                Predicate<Entity> indexPredicate = index.getKeyPredicate(key);
                assertTrue(indexPredicate.test(new Entity(key, "")));
                assertFalse(indexPredicate.test(new Entity(key - 1, "")));
                assertFalse(indexPredicate.test(new Entity(key + 1, "")));
                Predicate<Entity> continuePredicate = index.getContinuePredicate(key);
                assertTrue(continuePredicate.test(new Entity(key, "")));
                assertTrue(continuePredicate.test(new Entity(key - 1, "")));
                assertFalse(continuePredicate.test(new Entity(key + 1, "")));
            }
        }
        FileSystemUtils.deleteRecursively(tmp);
    }
}
