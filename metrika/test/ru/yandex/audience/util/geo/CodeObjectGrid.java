package ru.yandex.audience.util.geo;

import java.util.Arrays;

public class CodeObjectGrid extends CodeObjectExpr {

    CodeObjectExpr[] children;

    @Override
    public void refresh() {
        for (CodeObjectExpr child : children) {
            child.refresh();
        }

        errorRate = Arrays.stream(children).mapToDouble(c -> c.errorRate).average().orElse(0);
        complexity = 1 + Arrays.stream(children).mapToDouble(c -> c.complexity).average().orElse(0);

        for (CodeObjectExpr child : children) {
            this.context.putAll(child.context);
        }

    }

    public String getText() {
        // тут все будет интересней.
        return text;
    }

}
