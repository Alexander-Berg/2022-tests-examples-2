package ru.yandex.autotests.metrika.filters.user;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.metrika.filters.Expression;

/**
 * Created by konkov on 19.06.2015.
 */
public class Condition implements ConditionSequence {
    private final Condition prevCondition;
    private final SequenceRelation sequenceRelation;
    private final String namespace;
    private final Expression filter;

    public class SequenceRelationHolder {

        private final SequenceRelation sequenceRelation;
        private final Condition prevCondition;

        public SequenceRelationHolder(Condition prevCondition, SequenceRelation sequenceRelation) {
            this.prevCondition = prevCondition;
            this.sequenceRelation = sequenceRelation;
        }

        public Condition cond(String namespace, Expression filter) {
            return new Condition(prevCondition, sequenceRelation, namespace, filter);
        }
    }

    public Condition(String namespace, Expression filter) {
        this.prevCondition = null;
        this.sequenceRelation = null;
        this.namespace = namespace;
        this.filter = filter;
    }

    private Condition(Condition prevCondition, SequenceRelation sequenceRelation, String namespace, Expression filter) {
        this.prevCondition = prevCondition;
        this.sequenceRelation = sequenceRelation;
        this.namespace = namespace;
        this.filter = filter;
    }

    public Condition cond(String namespace, Expression filter) {
        return new Condition(this, SimpleSequenceRelation.empty(), namespace, filter);
    }

    public SequenceRelationHolder any() {
        return new SequenceRelationHolder(this, SimpleSequenceRelation.any());
    }

    public SequenceRelationHolder next() {
        return new SequenceRelationHolder(this, SimpleSequenceRelation.next());
    }

    public SequenceRelationHolder time(SequenceRelation sequenceRelation) {
        return new SequenceRelationHolder(this, sequenceRelation);
    }

    @Override
    public String build() {
        return String.format("%sCOND(%s, %s)",
                prevCondition != null
                        ? String.format("%s %s", prevCondition.build(), sequenceRelation.build())
                        : StringUtils.EMPTY,
                namespace, filter.build());
    }
}
