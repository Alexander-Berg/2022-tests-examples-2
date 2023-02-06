package ru.yandex.metrika.util.io;

import java.io.DataInputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.util.Random;

import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.io.bufferedfile.ThreadSafeBufferedFile;
import ru.yandex.metrika.util.io.pool.RandomAccessFilePool;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/** @author Arthur Suilin
 * Это плохой тест, переделанный из теста для другого класса
 * */
@Ignore("METRIQA-936")
public class ThreadSafeBufferedFileTest {
    RandomAccessFilePool pool;
    File f;
    ThreadSafeBufferedFile bf;

    @Before
    public void setup() throws IOException {
        f = File.createTempFile("BufferedFileTest", "test");
        Log4jSetup.basicSetup(Level.DEBUG);
        pool = new RandomAccessFilePool(100);
        bf = new ThreadSafeBufferedFile(f, pool, 3, null);
    }

    @After
    public void tearDown() throws Exception {
        bf.close();
        pool.destroy();
        assertTrue(f.delete());
    }

    @Test
    public void testRead() throws IOException {
        //assertEquals(0, bf.getSize());
        assertEquals(-1, bf.getInput(0).read());
        assertEquals(-1, bf.getInput(1000).read());

        OutputStream os = bf.getOutput();
        os.write(1);

        assertEquals(0, f.length()); //Flush еще не происходил
        InputStream is = bf.getInput(0);
        assertEquals(1, is.read()); // Прочитали то что записалось
        assertEquals(-1, is.read());
        os.flush();
        assertEquals(1, f.length());

        os.write(2);
        byte[] buffer = new byte[2];
        DataInputStream dis = new DataInputStream(bf.getInput(0));
        //assertEquals(2, new DataInputStream(bf.getInput(0)).readFully(buffer));
        dis.readFully(buffer);
        assertArrayEquals(new byte[]{1, 2}, buffer);
    }

    @Test
    public void testSingleWrite() throws IOException {
        OutputStream os = bf.getOutput();
        os.write(1);
        os.write(2);
        os.write(3);
        bf.close();
        assertEquals(3, f.length());
        assertEquals(3, bf.getInput(2).read());
        assertEquals(1, bf.getInput(0).read());
    }


    @Test
    public void testIncompleteFile() throws IOException {
        OutputStream os = bf.getOutput();
        os.write(1);
        os.write(2);
        os.write(3);
        //os.write(4);
        bf.close();
        // Отрезаем последний байт у файла
        RandomAccessFile rf = new RandomAccessFile(f, "rw");
        rf.setLength(f.length() - 1);
        rf.close();
        assertEquals(2, f.length());

        bf = new ThreadSafeBufferedFile(f, pool, 2, null);
        //bf.getOutput().write(4);

        assertEquals(-1, bf.getInput(2).read());
        assertEquals(1, bf.getInput(0).read());
        OutputStream os2 = bf.getOutput();
        //bf.getSize();
        os2.write(4);
        assertEquals(4, bf.getInput(2).read());

    }


    @Test
    public void testBigArrayWrite() throws IOException {
        OutputStream os = bf.getOutput();
        os.write(new byte[]{1, 2, 3});
        bf.close();
        assertEquals(3, f.length());
        assertEquals(3, bf.getInput(2).read());
        assertEquals(1, bf.getInput(0).read());
    }

    @Test
    public void testSmallArrayWriteSingleRead() throws IOException {
        OutputStream os = bf.getOutput();
        os.write(new byte[]{1, 2});
        assertEquals(0, f.length());
        assertEquals(1, bf.getInput(0).read());
        os.write(new byte[]{3});
        InputStream is = bf.getInput(2);
        assertEquals(3, is.read());
        assertEquals(-1, is.read());

    }

    @Test
    public void testSmallArrayWriteArrayRead() throws IOException {
        byte[] readBuffer = new byte[1];
        OutputStream os = bf.getOutput();
        os.write(new byte[]{1, 2});
        assertEquals(0, f.length());
        assertEquals(1, bf.getInput(0).read(readBuffer));
        assertArrayEquals(new byte[]{1}, readBuffer);
        os.write(new byte[]{3});
        InputStream is = bf.getInput(2);
        byte[] readBuffer2 = new byte[2];
        assertEquals(1, is.read(readBuffer2));
         assertArrayEquals(new byte[]{3, 0}, readBuffer2);
        assertEquals(-1, is.read(readBuffer2));

    }

    private int doRead(int readPosition, int written, byte[] data, Random r, InputStream reader) throws IOException {
            // Пробуем сделать случайное чтение из диапазона 0..written-1
            int toRead = r.nextInt(written - readPosition);
        //System.out.println("read");
            byte[] readBuffer = new byte[toRead];
            int wasRead = reader.read(readBuffer);
            Assert.assertEquals(toRead, wasRead);
            for (int i = 0; i < readBuffer.length; i++) {
                byte b = readBuffer[i];
                Assert.assertEquals(b, data[readPosition + i]);
            }
            return wasRead;
    }

    @Test
    public void testRandomReadWrite() throws IOException {
        int dataSize = 1024 * 1024 * 8;
        byte[] data = new byte[dataSize];
        for (int i = 0; i < data.length; i++) {
            data[i] = (byte) i;
        }
        OutputStream os = bf.getOutput();
        int written = 0;
        Random r = new Random(42);
        while (written < data.length) {
            int toWrite = r.nextInt(dataSize / 8);
            if (toWrite > data.length - written) {
                toWrite = data.length - written;
            }
            os.write(data, written, toWrite);
            written += toWrite;
            int readPosition = r.nextInt(written - 1);
            InputStream reader = bf.getInput(readPosition);
            while (readPosition < written -1) {
                readPosition += doRead(readPosition, written, data, r, reader);

            }
            reader.close();

        }


    }


}
