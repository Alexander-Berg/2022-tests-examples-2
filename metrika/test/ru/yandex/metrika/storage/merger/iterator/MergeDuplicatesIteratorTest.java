package ru.yandex.metrika.storage.merger.iterator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

import com.google.common.primitives.Ints;
import junit.framework.Assert;
import org.junit.Test;

import ru.yandex.metrika.storage.merger.FoldingFunction;

/** @author Arthur Suilin */
public class MergeDuplicatesIteratorTest {

    @Test
    public void test() {
        List<Integer> vals = new ArrayList(Arrays.asList(1, 1, 3, 4, 4, 4));
        MergeDuplicatesIterator<Integer> it = new MergeDuplicatesIterator<>(vals.iterator(), new FoldingFunction<Integer>() {
            @Override
            public Integer fold(Integer accumulator, Integer value) {
                return accumulator + value;
            }
        },
                new Comparator<Integer>() {
            @Override
            public int compare(Integer o1, Integer o2) {
                return Ints.compare(o1, o2);
            }
        });
        Assert.assertEquals(Integer.valueOf(2), it.next());
        Assert.assertEquals(Integer.valueOf(3), it.next());
        Assert.assertTrue(it.hasNext());
        Assert.assertEquals(Integer.valueOf(12), it.next());
        Assert.assertFalse(it.hasNext());

    }

}
