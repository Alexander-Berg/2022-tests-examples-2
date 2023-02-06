package ru.yandex.metrika.util.collections;

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertSame;

/**
 * @author jkee
 */

public class WeakHashSetTest {

    WeakHashSet<String> set;

    @Before
    public void setUp() throws Exception {
        set = new WeakHashSet<>();
    }

    @Test
    public void testName() throws Exception {

        ololo ololo = new ololo();

        ololo.assertAddition(set);



    }

    @Test
    public void testExpire() throws Exception {
        final List<String> memory = new ArrayList<>();

        while(set.getCount() == c) {
            //NO INLINING RRRRRRRRR
            Thread thread = new Thread(new Runnable() {
                @Override
                public void run() {
                    StringAdder adder = null;

                    for (int i = 0; i < 1; i++) {
                        if (i % 3 == 0) adder = new StringAdder1();
                        if (i % 3 == 1) adder = new StringAdder2();
                        if (i % 3 == 2) adder = new StringAdder() {
                            public void addString(List<String> memory) {
                                memory.add(set.intern(Long.toString(c++)));
                            }
                        };
                        adder.addString(memory);
                        memory.remove(memory.size() - 1);
                    }
                }
            });
            thread.start();
            thread.join();

            System.gc();
            set.expire();

            System.out.println(set.getCount());
            System.out.println(memory.size());
        }

        System.out.println(set.getCount());
        System.out.println(memory.size());

    }

    private interface StringAdder {
        void addString(List<String> memory);
    }

    private long c = 0;

    private class StringAdder1 implements StringAdder {
        public void addString(List<String> memory) {
            memory.add(set.intern(Long.toString(c++)));
        }
    }

    private class StringAdder2 implements StringAdder {
        public void addString(List<String> memory) {
            memory.add(set.intern(Long.toString(c++)));
        }
    }

    private static class ololo {
        private void assertAddition(WeakHashSet<String> set) {


            String _one2 = "one2";
            String _one3 = "one3";

            String[] strings = getStrings();
            for (String s: strings) {
                assertEquals(s, set.intern(s));
            }
            assertSame(strings[1], set.intern(_one2));
            assertSame(strings[2], set.intern(_one3));
            assertEquals(6, set.getCount());
        }

        private String[] getStrings() {
            String one = "one";
            String one2 = "one2";
            String one3 = "one3";
            String one4 = "one4";
            String one5 = "one5";
            String one6 = "one6";
            String[] strings = {one, one2, one3, one4, one5, one6};
            return strings;
        }
    }


}
