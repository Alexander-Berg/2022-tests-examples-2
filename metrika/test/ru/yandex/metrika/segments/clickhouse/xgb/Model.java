package ru.yandex.metrika.segments.clickhouse.xgb;

import java.util.ArrayList;
import java.util.List;

import ru.yandex.metrika.util.collections.F;

/**
 * Created by orantius on 14.04.17.
 */
public class Model {
    List<Node> trees = new ArrayList<>();

    public void addTree(Node node) {
        trees.add(node);
    }

    @Override
    public String toString() {
        return "arrayReduce('sum',[" +F.join(trees,",")+"])";
    }
}
