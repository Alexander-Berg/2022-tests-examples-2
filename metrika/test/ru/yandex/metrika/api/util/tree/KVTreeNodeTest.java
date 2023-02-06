package ru.yandex.metrika.api.util.tree;

import java.util.Comparator;
import java.util.LinkedHashMap;

import org.junit.Test;

import ru.yandex.metrika.util.tree.KVTreeNode;

import static org.junit.Assert.assertEquals;


public class KVTreeNodeTest {

    @Test
    public void sort() {
        KVTreeNode<Integer, Integer> actual = node(null, node(3, node(1), node(2)), node(1, node(5), node(3)));
        actual.sortByValues(Comparator.naturalOrder());

        KVTreeNode<Integer, Integer> expected = node(null, node(1, node(3), node(5)), node(3, node(1), node(2)));
        assertEquals(expected, actual);
    }

    @Test
    public void mapContent() {
        KVTreeNode<Integer, Integer> root = node2(null, node2(3, node2(1), node2(2)), node2(1, node2(5), node2(3)));
        KVTreeNode<Integer, Integer> actual = root.mapContent(i -> i == null ? null : i * 2);

        KVTreeNode<Integer, Integer> expected = node2(null, node2(6, node2(2), node2(4)), node2(2, node2(10), node2(6)));
        assertEquals(expected, actual);
    }

    @Test
    public void merge() {
        KVTreeNode<Integer, Integer> actual = node(null, node(3, node(1), node(2)), node(1, node(5), node(3)));
        KVTreeNode<Integer, Integer> addition = node(null, node(3, node(4), node(2)), node(6, node(5), node(3)));
        actual.merge(addition);

        KVTreeNode<Integer, Integer> expected = node(null, node(3, node(1), node(2), node(4)), node(1, node(5), node(3)), node(6, node(5), node(3)));
        assertEquals(expected, actual);
    }

    @Test
    public void mapNodeType() {
        KVTreeNode<Integer, Integer> root = node(0, node(3, node(1), node(2)), node(1, node(5), node(3)));
        KVTreeNode<String, String> actual = root.mapNodeType((v, nodes) -> {
            LinkedHashMap<String, KVTreeNode<String, String>> newNodes = new LinkedHashMap<>();
            nodes.forEach((k, v2) -> newNodes.put(k.toString(), v2));
            return new KVTreeNode<>(v.toString(), newNodes);
        });

        KVTreeNode<String, String> expected = node("0", node("3", node("1"), node("2")), node("1", node("5"), node("3")));
        assertEquals(expected, actual);
    }

    /**
     * Ключ в дереве это сам элемент
     */
    @SafeVarargs
    private static <T> KVTreeNode<T, T> node(T key, KVTreeNode<T, T>... nodes) {
        LinkedHashMap<T, KVTreeNode<T, T>> children = new LinkedHashMap<>();
        for (KVTreeNode<T, T> node : nodes) {
            children.put(node.getContent(), node);
        }
        return new KVTreeNode<>(key, children);
    }

    /**
     * Ключ в дереве это порядок элемента при добавлении
     */
    @SafeVarargs
    private static KVTreeNode<Integer, Integer> node2(Integer key, KVTreeNode<Integer, Integer>... nodes) {
        LinkedHashMap<Integer, KVTreeNode<Integer, Integer>> children = new LinkedHashMap<>();
        int i = 0;
        for (KVTreeNode<Integer, Integer> node : nodes) {
            children.put(i++, node);
        }
        return new KVTreeNode<>(key, children);
    }

}
