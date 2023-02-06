package ru.yandex.metrika.segments.clickhouse.xgb;

/**
 * Created by orantius on 14.04.17.
 */
public class Leaf implements Node {
    private final double value;

    public Leaf(double value) {
        this.value = value;
    }

    public double getValue() {
        return value;
    }

    @Override
    public String toString() {
        return ""+value;
    }
}
