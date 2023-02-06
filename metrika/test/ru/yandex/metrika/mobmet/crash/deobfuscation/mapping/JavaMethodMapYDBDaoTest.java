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
import static ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMapYDBDao.getToKey;
import static ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMapYDBDao.methodInfoKeyYdbOrder;

@RunWith(Parameterized.class)
public class JavaMethodMapYDBDaoTest {

    private static TreeSet<MethodInfoKey> shardBoundaries;

    @Parameter
    public MethodInfoKey fromKey;

    @Parameter(1)
    public MethodInfoKey expectedToKey;

    @BeforeClass
    public static void beforeClass() throws Exception {
        shardBoundaries = Stream.of(
                new MethodInfoKey(10L, 5L, "t", "classC", "methodK"),
                new MethodInfoKey(20L, 5L, "t", "classK", "methodO"),
                new MethodInfoKey(30L, 0L, "t", "", "")
        ).collect(toCollection(() -> new TreeSet<>(methodInfoKeyYdbOrder())));
    }

    @Parameters(name = "From Key: {0}")
    public static Collection<Object[]> init() {
        return List.of(
                new Object[]{
                        new MethodInfoKey(10L, 5L, "t", "", ""),
                        new MethodInfoKey(10L, 5L, "t", "classC", "methodK")},
                new Object[]{
                        new MethodInfoKey(10L, 5L, "t", "classC", "a"),
                        new MethodInfoKey(10L, 5L, "t", "classC", "methodK")},
                new Object[]{
                        new MethodInfoKey(10L, 5L, "t", "classC", "methodK"),
                        new MethodInfoKey(10L, 6L, "t", "", "")},
                new Object[]{
                        new MethodInfoKey(10L, 5L, "t", "classC", "methodT"),
                        new MethodInfoKey(10L, 6L, "t", "", "")},
                new Object[]{
                        new MethodInfoKey(20L, 5L, "t", "classK", "methodT"),
                        new MethodInfoKey(20L, 6L, "t", "", "")}
        );
    }

    @Test
    public void getToKeyTest() {
        MethodInfoKey toKey = getToKey("anyTable", fromKey, shardBoundaries);
        assertEquals(expectedToKey, toKey);
    }
}
