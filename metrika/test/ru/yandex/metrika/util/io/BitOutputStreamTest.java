package ru.yandex.metrika.util.io;

import java.io.IOException;
import java.io.InputStream;

import org.junit.Assert;
import org.junit.Test;

/** @author Arthur Suilin */
public class BitOutputStreamTest {

    @Test
    public void test() throws IOException {
        FastByteArrayOutputStream buf = new FastByteArrayOutputStream();
        BitOutputStream bos = new BitOutputStream(buf);
        boolean[] data = new boolean[1000];
        for (int i = 0; i < 1000; i++) {
            boolean v = Math.random() > 0.5;
            data[i] = v;
            bos.writeBit(v);
        }
        bos.close();
        Assert.assertEquals(1000, bos.getSize());
        InputStream is = buf.convertToInputStream();
        BitInputStream bis = new BitInputStream(is);
        for (int i = 0; i < 1000; i++) {
            boolean v = bis.readBit();
            Assert.assertEquals(data[i], v);

        }


    }
}
