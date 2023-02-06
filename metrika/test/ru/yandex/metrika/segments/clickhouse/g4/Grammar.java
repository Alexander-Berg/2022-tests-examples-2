package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Created by orantius on 11/20/15.
 */
public class Grammar implements GrammarNode {
    private final String name;
    private final List<Rule> rules;

    public Grammar(String name, List<Rule> rules) {
        this.name = name;
        this.rules = rules;
    }

    @Override
    public String toString() {
        return "grammar " + name +";\n" +
                rules.stream().map(Rule::toString).collect(Collectors.joining("\n\n"));
    }

    @Override
    public List<AtomNode> getFirstElements() {
        return Collections.emptyList();
    }

    @Override
    public List<AtomNode> getLastElements() {
        return Collections.emptyList();
    }

    @Override
    public <T> T visit(GrammarNodeVisitor<T> visitor) {
        List<T> ts = rules.stream().map(r -> r.visit(visitor)).collect(Collectors.toList());
        return null; // todo ?
    }

    public List<Rule> getRules() {
        return rules;
    }

    public Rule getRule(String name) {
        return rules.stream().filter(r->r.getName().equals(name)).findFirst().orElseThrow(()->new IllegalArgumentException("no rule with name "+name));
    }
}
