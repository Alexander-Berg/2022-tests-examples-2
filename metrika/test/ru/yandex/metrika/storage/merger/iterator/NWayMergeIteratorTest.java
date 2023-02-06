package ru.yandex.metrika.storage.merger.iterator;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Iterator;

import com.google.common.collect.Iterators;
import com.google.common.collect.Lists;
import com.google.common.primitives.Ints;
import org.junit.Assert;
import org.junit.Test;

/** @author Arthur Suilin */
public class NWayMergeIteratorTest {

    @Test
    public void test() {
        Iterator<Integer> i1 = Arrays.asList(1, 3, 3, 10).iterator();
        Iterator<Integer> i2 = Arrays.asList(2, 8, 16 ).iterator();
        NWayMergeIterator<Integer> it = new NWayMergeIterator<>(Arrays.asList(i1, i2), new Comparator<Integer>() {
            @Override
            public int compare(Integer o1, Integer o2) {
                return Ints.compare(o1, o2);
            }
        });
        int[] result = Ints.toArray(Arrays.asList(Iterators.toArray(it, Integer.class)));
        Assert.assertArrayEquals(new int[]{1, 2, 3, 3, 8, 10, 16}, result);
        Assert.assertFalse(it.hasNext());

    }

    @Test
    public void testNoIterator() {
        NWayMergeIterator<Integer> it = new NWayMergeIterator<>(Lists.<Iterator<Integer>>newArrayList(), new Comparator<Integer>() {
            @Override
            public int compare(Integer o1, Integer o2) {
                return Ints.compare(o1, o2);
            }
        });
        Assert.assertFalse(it.hasNext());

    }
}
