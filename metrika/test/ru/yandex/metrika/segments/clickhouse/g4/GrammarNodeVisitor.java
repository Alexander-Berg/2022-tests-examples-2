package ru.yandex.metrika.segments.clickhouse.g4;

/**
 * Created by orantius on 11/20/15.
 */
public interface GrammarNodeVisitor<T> {
    T visit(RuleRef node);
    T visit(Block node);
    T visit(Token node);
    T visit(Rule node);
    T visit(Alternative node);
}
