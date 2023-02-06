package ru.yandex.metrika.util.io;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;

import com.google.common.io.Files;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.io.pool.HandleContainer;
import ru.yandex.metrika.util.io.pool.HandlePoolImpl;
import ru.yandex.metrika.util.io.pool.RandomAccessFilePool;
import ru.yandex.metrika.util.log.Log4jSetup;

/** @author Arthur Suilin */
public class FilePoolTest {
    HandlePoolImpl<File, RandomAccessFile> pool;
    File[] files;

    @Before
    public void setup() throws IOException {
        Log4jSetup.basicSetup(Level.DEBUG);
        files = new File[3];
        for (int i = 0; i < files.length; i++) {
            files[i] = File.createTempFile("fpt", "FilePoolTest");
            Files.touch(files[i]);
        }
        pool = new RandomAccessFilePool(2);
    }

    @After
    public void teardown() throws Exception {
        pool.destroy();
        for (File file : files) {
            file.delete();
        }
    }

    @Test
    public void test() throws Exception {
        HandleContainer<RandomAccessFile> h0 = pool.get(files[0]);
        //noinspection unchecked
        HandleContainer<RandomAccessFile> h00 = pool.get(files[0]);
        Assert.assertNotSame(h0, h00);
        Assert.assertEquals(2, pool.getUsedCount());
        Assert.assertEquals(2, pool.getMisses());
        Assert.assertEquals(0, pool.getHits());
        Assert.assertEquals(2, pool.getOpens());

        pool.returnToPool(h00);
        Assert.assertEquals(1, pool.getUsedCount());
        Assert.assertEquals(0, pool.getCloses());

        // Должен вернуться тот же самый handle
        HandleContainer<RandomAccessFile> h00_2 = pool.get(files[0]);
        Assert.assertSame(h00, h00_2);
        Assert.assertEquals(2, pool.getMisses());
        Assert.assertEquals(1, pool.getHits());

        pool.returnToPool(h00_2);
        pool.returnToPool(h0);
        Assert.assertEquals(0, pool.getUsedCount());

        // Должен вернуться последний положенный в пул handle
        HandleContainer<RandomAccessFile> h_0x = pool.get(files[0]);
        Assert.assertSame(h_0x, h0);

        // Должен закрыться один из предыдущих хэндлов
        HandleContainer h1 = pool.get(files[1]);
        Assert.assertEquals(1, pool.getCloses());

        pool.delete(files[0]);
        // Файл не должен удалиться, т.к. он еще не освобождён
        Assert.assertTrue(files[0].exists());
        pool.returnToPool(h_0x);
        // А теперь должен
        Assert.assertFalse(files[0].exists());
        Assert.assertEquals(1, pool.getUsedCount());



//        for (int i = 0; i < 16; i++) {
//            for (int j = i; j < 16; j++) {
//                HandleContainer h = pool.get(files[j]);
//                pool.returnToPool(h);
//            }
//        }
//        Assert.assertEquals(0, pool.getUsedCount());
        //Assert.assertEquals(8, pool.getHits());
        // Теперь, если возьмем файл из начала списка


    }
}
