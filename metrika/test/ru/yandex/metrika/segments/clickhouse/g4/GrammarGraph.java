package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Created by orantius on 11/24/15.
 */
public class GrammarGraph {

    private final Grammar grammar;
    // index
    //private final Map<AtomNode,Rule> toRule = new HashMap<>();

    private final Map<AtomNode,Set<AtomNode>> nextSet = new IdentityHashMap<>();
    private final Map<AtomNode,Set<AtomNode>> prevSet = new IdentityHashMap<>();

    private final Map<Rule, AtomNode> ruleStart = new HashMap<>();
    private final Map<Rule, AtomNode> ruleEnd = new HashMap<>();

    public GrammarGraph(Grammar grammar) {
        this.grammar = grammar;
        buildSimple();
        iterateOperators();
    }

    private void iterateOperators() {
        boolean modified = true;
        while(modified) {
            modified = false;

            GrammarNodeVisitor<Boolean> visitor = new GrammarNodeVisitor<Boolean>() {
                @Override
                public Boolean visit(RuleRef node) {
                    return false;
                }

                @Override
                public Boolean visit(Block node) {
                    return node.getAlternatives().stream().map(a->a.visit(this)).collect(Collectors.reducing(false,Boolean::logicalOr));
                }

                @Override
                public Boolean visit(Token node) {
                    return false;
                }

                @Override
                public Boolean visit(Rule node) {
                    return node.getAlternatives().stream().map(a->a.visit(this)).collect(Collectors.reducing(false,Boolean::logicalOr));
                }

                @Override
                public Boolean visit(Alternative node) {
                    return
                        node.getElements().stream().filter(e->e.getSuffix()!=null)
                            .map(e->processSuffix(e.getElement(), e.getSuffix())).collect(Collectors.reducing(false, Boolean::logicalOr))
                            |
                        node.getElements().stream().map(a->a.getElement().visit(this)).collect(Collectors.reducing(false,Boolean::logicalOr));

                }

                private boolean processSuffix(Element elem, Operator suffix) {
                    // множество атомов, которые могут идти сразу после конца текущего элемента.
                    Set<AtomNode> following = elem.getLastElements().stream().flatMap(e->nextSet.getOrDefault(e,Collections.emptySet()).stream()).collect(Collectors.toSet());
                    // множество атомов, которые могут идти сразу перед началом текущего элемента.
                    Set<AtomNode> preceding = elem.getFirstElements().stream().flatMap(e->prevSet.getOrDefault(e,Collections.emptySet()).stream()).collect(Collectors.toSet());
                    switch (suffix) {
                        case PLUS: return processPlus(elem);
                        case QUESTION: return processQ(elem, following, preceding);
                        case STAR: return processPlus(elem) | processQ(elem, following, preceding);
                    }
                    return false;
                }

                private boolean processQ(Element elem, Set<AtomNode> following, Set<AtomNode> preceding) {
                    Boolean mod = preceding.stream().map(p -> nextSet.get(p).addAll(following)).reduce(false, Boolean::logicalOr);
                    following.stream().map(f->prevSet.get(f).addAll(preceding)).reduce(false, Boolean::logicalOr);
                    return mod;
                }

                private boolean processPlus(Element elem) {
                    List<AtomNode> first = elem.getFirstElements();
                    List<AtomNode> last = elem.getLastElements();
                    Boolean mod = last.stream().map(node->
                            nextSet.computeIfAbsent(node, k->new HashSet<>()).addAll(first)).reduce(false, Boolean::logicalOr);
                    first.stream().map(node-> prevSet.computeIfAbsent(node, k->new HashSet<>()).addAll(last)).reduce(false, Boolean::logicalOr);
                    return mod;
                }
            };

            modified = grammar.getRules().stream().map(visitor::visit).reduce(false, Boolean::logicalOr);
        }
    }

    private void buildSimple() {
        for (Rule rule : grammar.getRules()) {
            ruleStart.put(rule, new RuleRef(rule.getName()));
            ruleEnd.put(rule, new RuleRef(rule.getName()+"_END"));
        }

        GrammarNodeVisitor<Void> simpleConnect = new GrammarNodeVisitor<Void>() {
            Rule currentRule;
            @Override
            public Void visit(RuleRef node) {
                //toRule.put(node, currentRule);
                return null;
            }

            @Override
            public Void visit(Block node) {
                node.getAlternatives().forEach(a->a.visit(this));
                return null;
            }

            @Override
            public Void visit(Token node) {
                //toRule.put(node, currentRule);
                return null;
            }

            @Override
            public Void visit(Rule node) {
                currentRule = node;
                for (AtomNode atom : node.getFirstElements()) {
                    nextSet.computeIfAbsent(ruleStart.get(node),k->new HashSet<>()).add(atom);
                    prevSet.computeIfAbsent(atom,k->new HashSet<>()).add(ruleStart.get(node));
                }
                node.getAlternatives().forEach(a->a.visit(this));
                for (AtomNode atom : node.getLastElements()) {
                    nextSet.computeIfAbsent(atom,k->new HashSet<>()).add(ruleEnd.get(node));
                    prevSet.computeIfAbsent(ruleEnd.get(node),k->new HashSet<>()).add(atom);
                }
                currentRule = null;
                return null;
            }

            @Override
            public Void visit(Alternative node) {
                List<ElementWithSuffix> es = node.getElements();
                for (int i = 0; i < es.size(); i++) {
                    Element e = es.get(i).getElement();
                    if (i < es.size() - 1) {
                        Element eNext = es.get(i + 1).getElement();
                        for (AtomNode ePrevLast : e.getLastElements()) {
                            for (AtomNode eNextFirst : eNext.getFirstElements()) {
                                nextSet.computeIfAbsent(ePrevLast,k->new HashSet<>()).add(eNextFirst);
                                prevSet.computeIfAbsent(eNextFirst,k->new HashSet<>()).add(ePrevLast);
                            }
                        }
                    }
                    e.visit(this);
                }
                return null;
            }
        };
        grammar.visit(simpleConnect);
    }

    public Grammar getGrammar() {
        return grammar;
    }

    public Map<AtomNode, Set<AtomNode>> getNext() {
        return nextSet;
    }

    public Map<Rule, AtomNode> getRuleStart() {
        return ruleStart;
    }

    public Map<Rule, AtomNode> getRuleEnd() {
        return ruleEnd;
    }
}
