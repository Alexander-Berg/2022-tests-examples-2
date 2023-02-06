package ru.yandex.metrika.api.util.tree;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import ru.yandex.metrika.api.constructor.response.ConstructorResponseStatic;
import ru.yandex.metrika.api.constructor.response.QueryExternal;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.metrika.segments.core.query.parts.AttributeKeys;
import ru.yandex.metrika.util.tree.ConstructorServiceToTreeUtils;
import ru.yandex.metrika.util.tree.DimensionTreeData;
import ru.yandex.metrika.util.tree.KVTreeNode;

import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;


public class ConstructorServiceToTreeUtilsTest {

    @Test
    public void buildTree() {
        ConstructorResponseStatic response = new ConstructorResponseStatic();
        response.setQuery(new QueryExternal());
        response.getQuery().setMetrics(singletonList("ym:c:clicks"));

        List<StaticRow> rows = new ArrayList<>();
        rows.add(staticRow(ImmutableList.of(dim("1", "name1"), dim("2", "name2"), dim("3", "name3")), ImmutableList.of(2d)));
        rows.add(staticRow(ImmutableList.of(dim("1", "name1"), dim("2", "name2"), dim("4", "name4")), ImmutableList.of(3d)));
        rows.add(staticRow(ImmutableList.of(dim("1", "name1"), dim("5", "name5"), dim("6", "name6")), ImmutableList.of(1d)));
        rows.add(staticRow(ImmutableList.of(dim("7", "name7"), dim("8", "name8"), dim(null, null)), ImmutableList.of(1d)));
        response.setData(rows);

        KVTreeNode<String, DimensionTreeData> expectedRoot = new KVTreeNode<>(null);
        KVTreeNode<String, DimensionTreeData> node1 = new KVTreeNode<>(new DimensionTreeData(dim("1", "name1"), ImmutableList.of(6d)));
        KVTreeNode<String, DimensionTreeData> node2 = new KVTreeNode<>(new DimensionTreeData(dim("2", "name2"), ImmutableList.of(5d)));
        KVTreeNode<String, DimensionTreeData> node3 = new KVTreeNode<>(new DimensionTreeData(dim("3", "name3"), ImmutableList.of(2d)));
        KVTreeNode<String, DimensionTreeData> node4 = new KVTreeNode<>(new DimensionTreeData(dim("4", "name4"), ImmutableList.of(3d)));
        KVTreeNode<String, DimensionTreeData> node5 = new KVTreeNode<>(new DimensionTreeData(dim("5", "name5"), ImmutableList.of(1d)));
        KVTreeNode<String, DimensionTreeData> node6 = new KVTreeNode<>(new DimensionTreeData(dim("6", "name6"), ImmutableList.of(1d)));
        KVTreeNode<String, DimensionTreeData> node7 = new KVTreeNode<>(new DimensionTreeData(dim("7", "name7"), ImmutableList.of(1d)));
        KVTreeNode<String, DimensionTreeData> node8 = new KVTreeNode<>(new DimensionTreeData(dim("8", "name8"), ImmutableList.of(1d)));

        expectedRoot.withChld(asChildren(node1, node7));
        node1.withChld(asChildren(node2, node5));
        node2.withChld(asChildren(node3, node4));
        node5.withChld(asChildren(node6));
        node7.withChld(asChildren(node8));

        KVTreeNode<String, DimensionTreeData> actualRoot = ConstructorServiceToTreeUtils.fromResponseStatic(response);

        assertEquals(expectedRoot, actualRoot);
    }

    private static StaticRow staticRow(List<Map<String, String>> dimensions, List<Double> metrics) {
        StaticRow row = new StaticRow();
        row.setDimensions(dimensions);
        row.setMetrics(metrics.toArray(new Double[0]));
        return row;
    }

    @SafeVarargs
    public static LinkedHashMap<String, KVTreeNode<String, DimensionTreeData>> asChildren(KVTreeNode<String, DimensionTreeData>... nodes) {
        LinkedHashMap<String, KVTreeNode<String, DimensionTreeData>> children = new LinkedHashMap<>();
        for (KVTreeNode<String, DimensionTreeData> node : nodes) {
            children.put(node.getContent().getDimension().get(AttributeKeys.ID), node);
        }
        return children;
    }

    public static Map<String, String> dim(String id, String name) {
        Map<String, String> map = new HashMap<>();
        map.put(AttributeKeys.ID, id);
        map.put(AttributeKeys.NAME, name);
        return map;
    }
}
