package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.List;
import java.util.stream.Collectors;

/**
 * правило - имя и список топовых альтернатив.
 * Created by orantius on 11/20/15.
 */
public class Rule implements GrammarNode {

    private final String name;
    private final List<Alternative> alternatives;

    public Rule(String name, List<Alternative> alternatives) {
        this.name = name;
        this.alternatives = alternatives;
    }

    @Override
    public String toString() {
        return name + " : " +alternatives.stream().map(Alternative::toString).collect(Collectors.joining("\n    | "))+"\n    ;";
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

    public String getName() {
        return name;
    }
}

