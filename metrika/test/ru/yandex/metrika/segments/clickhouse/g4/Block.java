package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.List;
import java.util.stream.Collectors;

/**
 * вложенный в плавило список альтернатив
 * Created by orantius on 11/20/15.
 */
public class Block implements Element {
    private final List<Alternative> alternatives;

    public Block(List<Alternative> alternatives) {
        this.alternatives = alternatives;
    }

    @Override
    public String toString() {
        return "( "+alternatives.stream().map(Alternative::toString).collect(Collectors.joining("\n        | "))+" )";
    }

    @Override
    public List<AtomNode> getFirstElements() {
        return alternatives.stream().flatMap(a->a.getFirstElements().stream()).collect(Collectors.toList());
    }

    @Override
    public List<AtomNode> getLastElements() {
        return alternatives.stream().flatMap(a->a.getLastElements().stream()).collect(Collectors.toList());
    }

    @Override
    public <T> T visit(GrammarNodeVisitor<T> visitor) {
        return visitor.visit(this);
    }

    public List<Alternative> getAlternatives() {
        return alternatives;
    }
}
