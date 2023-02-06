package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.Collections;
import java.util.List;

/**
 * какой-то конкртеный набор букв, который должен стоять в этом месте по синтаксису: ключевое слово, пунктуация, или литерал известной структуры
 * Created by orantius on 11/20/15.
 */
public class Token implements AtomNode {

    private final String name;

    public Token(String name) {
        this.name = name;
    }

    @Override
    public String getName() {
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

    @Override
    public String toString() {
        return name;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Token token = (Token) o;

        return name.equals(token.name);

    }

    @Override
    public int hashCode() {
        return name.hashCode();
    }
}
