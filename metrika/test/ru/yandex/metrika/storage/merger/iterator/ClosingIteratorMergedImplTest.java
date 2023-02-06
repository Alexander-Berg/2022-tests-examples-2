package ru.yandex.metrika.storage.merger.iterator;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

/**
 * Created: 3/6/12
 *
 * @author jkee
 */

public class ClosingIteratorMergedImplTest {

/*
    public static void main(String[] args) throws Exception {
        ClosingIteratorMergedImplTest t = new ClosingIteratorMergedImplTest();
        t.testClose();
        t.testRemove();
        t.testHasNext();
    }
*/
    @Before
    public void setUp() throws Exception {
        ClosingIteratorTest.count.set(0);
    }

    ClosingIteratorMergedImpl<String> createInstance() {
        ArrayList<String> list1 = new ArrayList<>();
        list1.add("1");
        list1.add("2");
        ArrayList<String> list2 = new ArrayList<>();
        list2.add("3");
        list2.add("4");

        Iterator<String> iter1 = new ClosingIteratorTest(list1);
        Iterator<String> iter2 = new ClosingIteratorTest(list2);
        Iterator [] array = {iter1, iter2};
        return new ClosingIteratorMergedImpl<String>(array);
    }


    @Test
    public void testClose() throws Exception {
        ClosingIteratorMergedImpl impl = createInstance();
        impl.close();
        assertEquals(0, ClosingIteratorTest.count.get());
    }

    @Test
    public void testHasNext() throws Exception {
        ClosingIteratorMergedImpl<String> impl = createInstance();
        while(impl.hasNext()) {
            String str;
            assertNotNull(str = impl.next());
            System.out.println(str);
        }
        assertEquals(0, ClosingIteratorTest.count.get());
        assertFalse(impl.hasNext());
        try {
            String str = impl.next();

            fail();
        } catch (Exception e) {
            assertTrue(true);
        }
    }

    @Test
    public void testRemove() throws Exception {
        ClosingIteratorMergedImpl impl = createInstance();
        try {
            impl.remove();
        } catch (Exception e) {
            assertTrue(true);
        }
    }

    private static class ClosingIteratorTest implements ClosingIterator<String> {

        private static AtomicInteger count = new AtomicInteger();

        private Iterator<String> iterator;
        private boolean closed;

        ClosingIteratorTest (List<String> array) {
            iterator = array.iterator();
            count.incrementAndGet();
        }

        @Override
        public void close() throws IOException {
            if(!closed) {
                closed = true;
                count.decrementAndGet();
            }
        }

        @Override
        public boolean hasNext() {
            return iterator.hasNext();
        }

        @Override
        public String next() {
            return iterator.next();
        }

        @Override
        public void remove() {
            iterator.remove();
        }
    }

}
