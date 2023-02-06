package ru.yandex.metrika.storage.bloom;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;


/** @author Artur Suilin */
@Ignore //тяжелый
public class RamBitStoreTest {


    @Test
    public void test() {
        long bits = Integer.MAX_VALUE * 2L;
        RamBitStore st = new RamBitStore(bits);
        for (long i = 0; i < bits; i++) {
            if (i % 2 == 0) {
              st.setBit(i);
            }
        }
        for (long i = 0; i < bits; i++) {
            boolean bit = st.getBit(i);
            Assert.assertEquals(bit, i % 2 == 0);
        }



    }

}
