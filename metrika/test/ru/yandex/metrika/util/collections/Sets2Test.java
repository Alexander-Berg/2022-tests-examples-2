package ru.yandex.metrika.util.collections;

import java.util.List;

import gnu.trove.map.hash.TIntObjectHashMap;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * @author jkee
 */

public class Sets2Test {
    @Test
    public void testGrouped() throws Exception {
        TIntObjectHashMap<String> source = new TIntObjectHashMap<>();
        source.put(1, "ololo");
        source.put(2, "ololo");
        source.put(3, "ololo");
        List<TIntObjectHashMap<String>> grouped = Sets2.grouped(source, 1);
        assertEquals(3, grouped.size());
        assertTrue(source.containsKey(grouped.get(0).keys()[0]));
        assertTrue(source.containsKey(grouped.get(1).keys()[0]));
        assertTrue(source.containsKey(grouped.get(2).keys()[0]));

        List<TIntObjectHashMap<String>> grouped2 = Sets2.grouped(source, 2);
        assertEquals(2, grouped2.size());
        assertTrue(source.containsKey(grouped2.get(0).keys()[0]));
        assertTrue(source.containsKey(grouped2.get(0).keys()[1]));
        assertTrue(source.containsKey(grouped2.get(1).keys()[0]));

    }
}
