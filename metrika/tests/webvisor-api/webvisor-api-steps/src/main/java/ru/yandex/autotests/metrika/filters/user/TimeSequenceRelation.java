package ru.yandex.autotests.metrika.filters.user;

/**
 * Created by konkov on 19.06.2015.
 */
public class TimeSequenceRelation implements SequenceRelation {

    private final String relation;
    private final int num;
    private final String unit;

    TimeSequenceRelation(String relation, int num, String unit) {

        this.relation = relation;
        this.num = num;
        this.unit = unit;
    }

    public static NumberHolder greaterThan(int num) {
        return new NumberHolder(">", num);
    }

    public static NumberHolder lessThan(int num) {
        return new NumberHolder("<", num);
    }

    public static NumberHolder greaterThanOrEqual(int num) {
        return new NumberHolder(">=", num);
    }

    public static NumberHolder lessThanOrEqual(int num) {
        return new NumberHolder("<=", num);
    }

    @Override
    public String build() {
        return String.format("TIME(%s%s %s) ", relation, num, unit);
    }
}
