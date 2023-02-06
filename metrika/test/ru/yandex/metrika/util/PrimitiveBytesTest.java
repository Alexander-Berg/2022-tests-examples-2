package ru.yandex.metrika.util;

import java.util.Arrays;

import org.junit.Test;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;
import static ru.yandex.metrika.util.PrimitiveBytes.getInt;
import static ru.yandex.metrika.util.PrimitiveBytes.getIntArray;
import static ru.yandex.metrika.util.PrimitiveBytes.modifyIntArray;
import static ru.yandex.metrika.util.PrimitiveBytes.wrapIntArray;

/**
 * @author jkee
 */

public class PrimitiveBytesTest {
    @Test
    public void testIntArray() throws Exception {
        int[] zero = {};
        assertTrue(wrapIntArray(zero).length == 0);

        int[] one = {1};
        assertTrue(wrapIntArray(one).length == 4);
        assertTrue(Arrays.equals(getIntArray(wrapIntArray(one)), one));

        int[] multiple = {1, 2, 12312414, 936547567, -1242353453};
        assertTrue(wrapIntArray(multiple).length == 5 * 4);
        assertTrue(Arrays.equals(getIntArray(wrapIntArray(multiple)), multiple));

        byte[] array = wrapIntArray(multiple);
        modifyIntArray(array, 0, 5);
        multiple[0] += 5;
        assertTrue(Arrays.equals(array, wrapIntArray(multiple)));

        modifyIntArray(array, 0, -2);
        multiple[0] -= 2;
        assertTrue(Arrays.equals(array, wrapIntArray(multiple)));

        modifyIntArray(array, 4, 5);
        multiple[4] += 5;
        assertTrue(Arrays.equals(array, wrapIntArray(multiple)));

        modifyIntArray(array, 3, 5);
        multiple[3] += 5;
        assertTrue(Arrays.equals(array, wrapIntArray(multiple)));

        byte[] filled = new byte[50*4];
        PrimitiveBytes.fillIntArray(filled, Integer.MAX_VALUE);
        for (int i = 0; i < 50; i++) {
            assertEquals(Integer.MAX_VALUE, getInt(filled, i * 4));
        }
    }


}
