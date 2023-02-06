package ru.yandex.metrika.util.collections;

import java.util.Arrays;
import java.util.List;

import com.google.common.collect.Multimap;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class Collectors2Test {
    @Test
    public void testMultimap() throws Exception {
        List<String> food = Arrays.asList("баклажан", "макарон", "овощ", "сгущенка", "тефтель");
        Multimap<Boolean, String> byO = food.stream().collect(Collectors2.toMultimap(x -> x.contains("о")));
        assertEquals(Arrays.asList("макарон", "овощ"), byO.get(true));
        assertEquals(Arrays.asList("баклажан", "сгущенка", "тефтель"), byO.get(false));
    }
}
