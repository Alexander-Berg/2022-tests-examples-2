package ru.yandex.autotests.metrika.filters.user;

import org.apache.commons.lang3.StringUtils;

/**
 * Created by konkov on 19.06.2015.
 */
public class SimpleSequenceRelation implements SequenceRelation {

    private final String conditionSequence;

    private SimpleSequenceRelation(String conditionSequence) {
        this.conditionSequence = conditionSequence;
    }

    public static SequenceRelation empty() {
        return new SimpleSequenceRelation(StringUtils.EMPTY);
    }

    public static SequenceRelation any() {
        return new SimpleSequenceRelation("ANY ");
    }

    public static SequenceRelation next() {
        return new SimpleSequenceRelation("NEXT ");
    }

    @Override
    public String build() {
        return conditionSequence;
    }
}
