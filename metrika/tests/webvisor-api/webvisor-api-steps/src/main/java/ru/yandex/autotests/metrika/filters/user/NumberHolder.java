package ru.yandex.autotests.metrika.filters.user;

/**
 * Created by konkov on 19.06.2015.
 */
public class NumberHolder {
    private final String relation;
    private final int num;

    NumberHolder(String relation, int num) {
        this.relation = relation;
        this.num = num;
    }

    public SequenceRelation sec() {
        return new TimeSequenceRelation(relation, num, "sec");
    }

    public SequenceRelation min() {
        return new TimeSequenceRelation(relation, num, "min");
    }

    public SequenceRelation hour() {
        return new TimeSequenceRelation(relation, num, "hour");
    }

    public SequenceRelation day() {
        return new TimeSequenceRelation(relation, num, "day");
    }
}
