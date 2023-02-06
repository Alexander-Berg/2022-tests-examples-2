package ru.yandex.taxi.dmp.flink.test;

import org.apache.flink.table.annotation.DataTypeHint;
import org.apache.flink.table.functions.ScalarFunction;
import org.apache.flink.types.Row;

public class TestMapFunction extends ScalarFunction {
    public @DataTypeHint("ROW<aName STRING, bName STRING>") Row eval(String a) {
        var row = Row.withNames();
        row.setField("bName", a);
        row.setField("aName", "pre-" + a);
        return row;
//        return Row.of(a, "pre-" + a);
    }
}
