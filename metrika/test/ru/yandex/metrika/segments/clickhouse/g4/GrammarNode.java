package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.List;

/**
 * Created by orantius on 11/20/15.
 */
public interface GrammarNode {

    List<AtomNode> getFirstElements();
    List<AtomNode> getLastElements();

    <T> T visit(GrammarNodeVisitor<T> visitor);
}
