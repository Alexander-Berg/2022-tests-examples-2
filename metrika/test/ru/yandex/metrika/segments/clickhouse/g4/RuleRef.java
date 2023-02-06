package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.Collections;
import java.util.List;

/**
 * остылка к другому правилу
 * Created by orantius on 11/20/15.
 */
public class RuleRef implements AtomNode {

    private final String name;

    public RuleRef(String name) {
        this.name = name;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public String toString() {
        return name;
    }

    @Override
    public List<AtomNode> getFirstElements() {
        return Collections.singletonList(this);
    }

    @Override
    public List<AtomNode> getLastElements() {
        return Collections.singletonList(this);
    }

    @Override
    public <T> T visit(GrammarNodeVisitor<T> visitor) {
        return visitor.visit(this);
    }

}
