package ru.yandex.metrika.storage.hash;

import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;

import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.concurrent.Pools;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;

/**
 * @author Arthur Suilin
 */
public class PersistentHashTableTest {

    private static final int COUNT2 = 1000000;

    @Test
    public void testOffheapMultithreading() throws Exception {
        Log4jSetup.basicSetup();
        DumpableHashStorage.DumpableHashStorageFactory factory = new ThreadSafeOffHeapHashStorage.ThreadSafeOffHeapHashStorageFactory();
        DumpableHashStorage hs = factory.makeStorage(null, 20);
        final PersistentHashTable t = new PersistentHashTable(4,4,hs);
        for (int i = 1; i < COUNT2; i++) {
            t.put(PrimitiveBytes.wrap(i*10), PrimitiveBytes.wrap(i*10));
        }
        ThreadPoolExecutor executor = Pools.newNamedFixedThreadPool(2, "");
        class TaskGood implements Callable<Integer> {
            @Override
            public Integer call() throws Exception {
                int s = 0;
                for (int i = 1; i < COUNT2; i++) {
                    byte[] bytes = t.get(PrimitiveBytes.wrap(i * 10));
                    s += bytes == null ? 1 : 0;
                }
                return s;
            }
        }
        class TaskBad implements Callable<Integer> {
            @Override
            public Integer call() throws Exception {
                int s = 0;
                for (int i = COUNT2 * 3; i < COUNT2 * 4; i++) {
                    s += t.get(PrimitiveBytes.wrap(i*10)) == null ? 1 : 0;
                }
                return s;
            }
        }
        TaskGood taskGood = new TaskGood();
        TaskBad taskBad = new TaskBad();
        Future<Integer> good = executor.submit(taskGood);
        Future<Integer> bad = executor.submit(taskBad);
        assertEquals(0, good.get().intValue());
        assertEquals(COUNT2, bad.get().intValue());
    }
}
