package ru.yandex.metrika.storage.merger.iterator;

import java.io.Closeable;
import java.io.IOException;
import java.util.Iterator;
import java.util.NoSuchElementException;

import junit.framework.Assert;
import org.junit.Test;

/** @author Arthur Suilin */
public class ClosingIteratorTest {


    class IntIterator implements Iterator<Integer>, Closeable {
        int position;
        final int[] array;
        boolean closed;

        IntIterator(int[] array) {
            this.array = array;
        }

        @Override
        public boolean hasNext() {
            return position < array.length;
        }

        @Override
        public Integer next() {
            if (position >= array.length)
                throw new NoSuchElementException();
            return array[position++];
        }

        @Override
        public void remove() {
            //To change body of implemented methods use File | Settings | File Templates.
        }

        @Override
        public void close() throws IOException {
            closed = true;
        }
    }

    @Test
    public void testHasNext() {
        IntIterator src = new IntIterator(new int[]{1, 2});
        ClosingIterator<Integer> it = new ClosingIteratorImpl<>(src);
        Assert.assertTrue(it.hasNext());
        Assert.assertEquals(Integer.valueOf(1), it.next());
        Assert.assertTrue(it.hasNext());
        Assert.assertFalse(src.closed);
        Assert.assertEquals(Integer.valueOf(2), it.next());
        Assert.assertFalse(it.hasNext());
        Assert.assertTrue(src.closed);
    }

}
