package ru.yandex.metrika.segments.clickhouse.g4;

/**
 * добавляет элементу КАРДИНАЛЬНОСТЬ
 * Created by orantius on 11/20/15.
 */
public class ElementWithSuffix {
    private final Element element;
    private final Operator suffix;

    public ElementWithSuffix(Element element, Operator suffix) {
        this.element = element;
        this.suffix = suffix;
    }

    @Override
    public String toString() {
        return ""+ element + (suffix!=null?" "+suffix:"");
    }

    public Element getElement() {
        return element;
    }

    public Operator getSuffix() {
        return suffix;
    }
}
