package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.List;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.literals.CHArray;
import ru.yandex.metrika.segments.clickhouse.types.CHType;
import ru.yandex.metrika.util.collections.Lists2;

public class CHLiteralTestUtils {

    public static <T extends CHType> CHArray<T> emptyArr(T type) {
        return ClickHouse.arr(List.of(), type);
    }

    @SafeVarargs
    public static <T extends CHType> CHArray<T> arr(CHLiteral<T> head, CHLiteral<T>... tail) {
        return ClickHouse.arr(Lists2.concat(head, List.of(tail)), head.getType());
    }
}
