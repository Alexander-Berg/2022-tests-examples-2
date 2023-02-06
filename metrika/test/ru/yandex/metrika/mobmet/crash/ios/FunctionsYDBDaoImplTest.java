package ru.yandex.metrika.mobmet.crash.ios;

import java.util.Collection;
import java.util.List;
import java.util.TreeSet;
import java.util.stream.Stream;

import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import static java.util.stream.Collectors.toCollection;
import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.mobmet.crash.ios.FunctionsYDBDaoImpl.functionKeyYdbOrder;
import static ru.yandex.metrika.mobmet.crash.ios.FunctionsYDBDaoImpl.getToKey;

@RunWith(Parameterized.class)
public class FunctionsYDBDaoImplTest {

    private static TreeSet<YdbFunctionKey> shardBoundaries;

    @Parameter
    public YdbFunctionKey fromKey;

    @Parameter(1)
    public YdbFunctionKey expectedToKey;

    @BeforeClass
    public static void beforeClass() throws Exception {
        shardBoundaries = Stream.of(
                new YdbFunctionKey(10, 5, 100),
                new YdbFunctionKey(20, 5, 100),
                new YdbFunctionKey(30, 0, 0)
        ).collect(toCollection(() -> new TreeSet<>(functionKeyYdbOrder())));
    }

    @Parameters(name = "From Key: {0}")
    public static Collection<Object[]> init() {
        return List.of(
                new Object[]{new YdbFunctionKey(10L, 5L, 0), new YdbFunctionKey(10L, 5L, 100)},
                new Object[]{new YdbFunctionKey(10L, 5L, 50), new YdbFunctionKey(10L, 5L, 100)},
                new Object[]{new YdbFunctionKey(10L, 5L, 100), new YdbFunctionKey(10L, 6L, 0)},
                new Object[]{new YdbFunctionKey(10L, 5L, 150), new YdbFunctionKey(10L, 6L, 0)},
                new Object[]{new YdbFunctionKey(20L, 5L, 150), new YdbFunctionKey(20L, 6L, 0)}
        );
    }

    @Test
    public void getToKeyTest() {
        YdbFunctionKey toKey = getToKey(fromKey, shardBoundaries);
        assertEquals(expectedToKey, toKey);
    }
}
