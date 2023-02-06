package ru.yandex.metrika.segments.clickhouse.g4;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayDeque;
import java.util.Collection;
import java.util.Deque;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.jetbrains.annotations.NotNull;

import ru.yandex.metrika.segments.clickhouse.parse.ClickHouseParser;

/**
 * graphviz version of grammar
 * dot -v -o/home/orantius/dev/projects/metrika/metrika-api/segments/src/java/ru/yandex/metrika/segments/clickhouse/fluent2/ch.png -Tpng /home/orantius/dev/ch.dot
 * Created by orantius on 11/20/15.
 */
public class PrintDot {

    public static void main(String[] args) throws Exception {

        GrammarBuilder gb = new GrammarBuilder("ClickHouseParser.g4",ClickHouseParser.class);
        //GrammarBuilder gb = new GrammarBuilder("test.g4");
        Grammar grammar = gb.build();
        GrammarGraph graph = new GrammarGraph(grammar);
        String dot = print(graph);
        try(BufferedWriter bw = new BufferedWriter(new FileWriter(new File("/home/orantius/dev/ch.dot")))){
            bw.write(dot);
        }
        System.out.println(dot);
    }

    public static String print(GrammarGraph graph) {
        // map node->name
        Map<AtomNode, String> names = giveNames(graph);
        StringBuilder sb = new StringBuilder("digraph sql {\n");
        sb.append("    rankdir=LR;\n");
        for (Map.Entry<AtomNode, Set<AtomNode>> ee : graph.getNext().entrySet()) {
            for (AtomNode next : ee.getValue()) {
                sb.append("    "+names.get(ee.getKey())+" -> "+names.get(next)+";\n");
            }
        }
        sb.append("}");
        return sb.toString();

    }

    @NotNull
    private static Map<AtomNode, String> giveNames(GrammarGraph graph) {
        Map<AtomNode, String> names = new IdentityHashMap<>();

        GrammarNodeVisitor<Void> namer = new GrammarNodeVisitor<Void>() {
            private String rule;
            private final Deque<Integer> index = new ArrayDeque<>();

            private String buildName(String rule, Collection<Integer> index, AtomNode node) {
                return node.getName()+"_"+Math.abs((index.stream().map(k -> "" + k).collect(Collectors.joining())+rule).hashCode());
            }

            @Override
            public Void visit(RuleRef node) {
                names.put(node, buildName(rule, index, node));
                return null;
            }

            @Override
            public Void visit(Block node) {
                for (int i = 0; i < node.getAlternatives().size(); i++) {
                    index.push(i);
                    node.getAlternatives().get(i).visit(this);
                    index.pop();
                }
                return null;
            }

            @Override
            public Void visit(Token node) {
                names.put(node, buildName(rule, index, node));
                return null;
            }

            @Override
            public Void visit(Rule node) {
                rule = node.getName();
                names.put(graph.getRuleStart().get(node), node.getName());
                names.put(graph.getRuleEnd().get(node), node.getName()+"_END");
                for (int i = 0; i < node.getAlternatives().size(); i++) {
                    index.push(i);
                    node.getAlternatives().get(i).visit(this);
                    index.pop();
                }
                return null;
            }

            @Override
            public Void visit(Alternative node) {
                for (int i = 0; i < node.getElements().size(); i++) {
                    index.push(i);
                    node.getElements().get(i).getElement().visit(this);
                    index.pop();
                }
                return null;
            }
        };
        graph.getGrammar().visit(namer);
        return names;
    }


}
