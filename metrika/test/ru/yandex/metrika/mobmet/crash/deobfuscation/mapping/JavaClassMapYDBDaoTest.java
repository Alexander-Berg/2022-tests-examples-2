package ru.yandex.metrika.mobmet.crash.deobfuscation.mapping;

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
import static ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMapYDBDao.classNameKeyYdbOrder;
import static ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMapYDBDao.getToKey;

@RunWith(Parameterized.class)
public class JavaClassMapYDBDaoTest {

    private static TreeSet<ClassNameKey> shardBoundaries;

    @Parameter
    public ClassNameKey fromKey;

    @Parameter(1)
    public ClassNameKey expectedToKey;

    @BeforeClass
    public static void beforeClass() throws Exception {
        shardBoundaries = Stream.of(
                new ClassNameKey(10, 5, "anyTable", "c"),
                new ClassNameKey(20, 5, "anyTable", "k"),
                new ClassNameKey(30, 0, "anyTable", "")
        ).collect(toCollection(() -> new TreeSet<>(classNameKeyYdbOrder())));
    }

    @Parameters(name = "From Key: {0}")
    public static Collection<Object[]> init() {
        return List.of(
                new Object[]{new ClassNameKey(10, 5, "anyTable", ""), new ClassNameKey(10, 5, "anyTable", "c")},
                new Object[]{new ClassNameKey(10, 5, "anyTable", "a"), new ClassNameKey(10, 5, "anyTable", "c")},
                new Object[]{new ClassNameKey(10, 5, "anyTable", "c"), new ClassNameKey(10, 6, "anyTable", "")},
                new Object[]{new ClassNameKey(10, 5, "anyTable", "d"), new ClassNameKey(10, 6, "anyTable", "")},
                new Object[]{new ClassNameKey(20, 5, "anyTable", "p"), new ClassNameKey(20, 6, "anyTable", "")}
        );
    }

    @Test
    public void getToKeyTest() {
        ClassNameKey toKey = getToKey("anyTable", fromKey, shardBoundaries);
        assertEquals(expectedToKey, toKey);
    }
}
