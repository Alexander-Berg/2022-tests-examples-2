package ru.yandex.metrika.segments.clickhouse.g4;

/**
 * Created by orantius on 11/20/15.
 */
public enum Operator {
    QUESTION("?"),
    STAR("*"),
    PLUS("+");

    String val;

    Operator(String val) {
        this.val = val;
    }

    @Override
    public String toString() {
        return val;
    }
}
