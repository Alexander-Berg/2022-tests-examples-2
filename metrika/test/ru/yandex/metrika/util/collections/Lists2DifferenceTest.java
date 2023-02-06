package ru.yandex.metrika.util.collections;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static com.google.common.collect.Lists.newArrayList;
import static junit.framework.Assert.assertEquals;

@RunWith(Parameterized.class)
public class Lists2DifferenceTest {

    @Parameterized.Parameter
    public List<String> minuend;

    @Parameterized.Parameter(1)
    public List<String> subtrahend;

    @Parameterized.Parameter(2)
    public List<String> result;

    @Test
    public void testDifference() throws Exception {
        assertEquals(result, Lists2.difference(minuend, subtrahend));
    }

    @Parameterized.Parameters
    public static Collection<Object[]> initParams() {
        return ImmutableList.<Object[]>builder()
                .add(params(newArrayList("a", "b", "c"), newArrayList("a"), newArrayList("b", "c")))
                .add(params(newArrayList("a", "b", "c"), newArrayList("b", "a"), newArrayList("c")))
                .add(params(newArrayList("a", "b", "c"), newArrayList("d"), newArrayList("a", "b", "c")))
                .add(params(newArrayList("a", "b", "c"), newArrayList("a", "b", "c", "d"), newArrayList()))
                .build();
    }

    private static Object[] params(Object... params) {
        return params;
    }
}
