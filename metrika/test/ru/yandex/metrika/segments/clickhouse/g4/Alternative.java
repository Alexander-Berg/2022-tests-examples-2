package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.List;
import java.util.stream.Collectors;

import org.jetbrains.annotations.Nullable;

/**
 * элемент грамматики, содержащий ПОСЛЕДОВАТЕЛЬНО идущие элементы.
 * Created by orantius on 11/20/15.
 */
public class Alternative implements GrammarNode {

    @Nullable
    private final String label;
    private final List<ElementWithSuffix> elements;

    public Alternative(String label, List<ElementWithSuffix> elements) {
        this.label = label;
        this.elements = elements;
    }

    public Alternative(List<ElementWithSuffix> elements) {
        this(null, elements);
    }

    @Nullable
    public String getLabel() {
        return label;
    }

    public List<ElementWithSuffix> getElements() {
        return elements;
    }

    @Override
    public String toString() {
        return elements.stream().map(e->e.toString()).collect(Collectors.joining(" "))+ (label!=null?" #"+label:"");
    }

    @Override
    public List<AtomNode> getFirstElements() {
        return elements.get(0).getElement().getFirstElements();
    }

    @Override
    public List<AtomNode> getLastElements() {
        return elements.get(elements.size()-1).getElement().getLastElements();
    }

    @Override
    public <T> T visit(GrammarNodeVisitor<T> visitor) {
        return visitor.visit(this);
    }
}
