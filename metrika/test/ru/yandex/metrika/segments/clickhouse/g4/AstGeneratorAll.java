package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.google.common.collect.Iterables;
import com.google.common.collect.Iterators;
import com.google.common.collect.PeekingIterator;

import ru.yandex.metrika.util.collections.F;

/**
 * генератор строк, которые парсятся в деревья ограниченной сложности по грамматике и примерам токенов.
 * недостатки
 * - размер ответа растет экспоненциально от требуемой сложности структур
 * - присутствуют только "положительные" примеры, для которых ожидается успешный результат
 * - игнорирование какой-либо семантики
 * Created by orantius on 1/24/16.
 */
public class AstGeneratorAll {

    public static final List<String> EPSILON = Collections.singletonList("");

    private final Grammar grammar;
    private final Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues;

    public AstGeneratorAll(Grammar grammar, Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues) {
        this.grammar = grammar;
        this.tokenValues = tokenValues;
    }

    public Iterable<String> generate(Rule rule, int maxDepth) {
        return withNode(rule, new LinkedList<>(), stack->generate(rule, maxDepth, stack));
    }

    private static <R> R withNode(GrammarNode elem, LinkedList<GrammarNode> stack, Function<LinkedList<GrammarNode>, R> cont) {
        stack.push(elem);
        R res = cont.apply(stack);
        stack.pop();
        return res;
    }

    private Iterable<String> generate(Rule rule, int maxDepth, LinkedList<GrammarNode> stack) {
        // склеиваем потоки вариантов, полученные из альтернатив
        return plus(F.map(rule.getAlternatives(), a->withNode(a, stack, ss->generate(a, maxDepth, ss))));
    }

    private Iterable<String> generate(Alternative seq, int maxDepth, LinkedList<GrammarNode> stack) {
        List<Iterable<String>> map = F.map(seq.getElements(), e -> applySuffix(withNode(e.getElement(), stack, ss->generate(e.getElement(), maxDepth, ss)), e.getSuffix(), maxDepth));
        return product(map);
    }

    private static Iterable<String> applySuffix(Iterable<String> arg, Operator suffix, int maxDepth) {
        if(suffix == null) {
            return arg;
        } else if(suffix == Operator.QUESTION) {
            return plus(EPSILON, arg);
        } else if(suffix == Operator.PLUS || suffix == Operator.STAR) {
            List<Iterable<String>> res = new ArrayList<>();
            if(suffix == Operator.STAR) {
                res.add(EPSILON);
            }
            for (int i = 1; i < maxDepth; i++) {
                List<Iterable<String>> repeated = repeat(arg, i);
                res.add(product(repeated));
            }
            return plus(res);
        }
        throw new IllegalArgumentException("unsupported type of suffix "+suffix);
    }

    private static List<Iterable<String>> repeat(Iterable<String> arg, int size) {
        ArrayList<Iterable<String>> res = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            res.add(arg);
        }
        return res;
    }

    private Iterable<String> generate(Element elem, int maxDepth, LinkedList<GrammarNode> stack) {
        if(elem instanceof Token) {
            List<String> strings = tokenValues.get(elem).apply(stack);
            if(strings==null || strings.isEmpty()) {
                throw new IllegalStateException("no representation for token " +elem);
            }
            return strings;
        }
        if(elem instanceof RuleRef) {
            if(maxDepth > 0) {
                Rule rule = grammar.getRule(((RuleRef) elem).getName());
                return withNode(rule, stack, ss->generate(rule, maxDepth-1, ss));
            } else {
                return Collections.emptyList();
            }
        }
        if(elem instanceof Block) {
            Block block = (Block)elem;
            return plus(F.map(block.getAlternatives(), a-> withNode(a, stack, ss->generate(a, maxDepth, ss)))); // возможно, тут тоже надо уменьшить maxDepth
        }
        throw new IllegalArgumentException(" unsupported type of elem "+elem);
    }

    ////////////////////////////// iterables arithmetic

    private static Iterable<String> plus(Iterable<String> arg, Iterable<String> arg2) {
        return Iterables.concat(arg, arg2);
    }

    private static Iterable<String> plus(List<Iterable<String>> list) {
        return Iterables.concat(list);
    }

    private static Iterable<String> product(List<Iterable<String>> arg) {
        // если умножаем на ноль, то возвращаем сразу ноль.
        if(arg.isEmpty() || arg.stream().filter(f->!f.iterator().hasNext()).findAny().isPresent()) {
            return Collections.emptyList();
        }
        // иначе предполагаем что имеется непустое множество непустых итераторов.
        return () -> new Iterator<String>() {
            List<PeekingIterator<String>> its = F.map(arg, i-> Iterators.peekingIterator(i.iterator()));
             boolean stop;
            @Override
            public boolean hasNext() {
                return !stop && its.stream().allMatch(i->i.hasNext());
            }

            @Override
            public String next() {
                String current = its.stream().map(i->i.peek()).collect(Collectors.joining(" "));
                moveIterators(0);
                return current;
            }

            private void moveIterators(int index) {
                if(its.size() == index) {
                    stop = true;
                    return;
                }
                its.get(index).next();
                if(!its.get(index).hasNext()) { // если закончился,
                    its.set(index, Iterators.peekingIterator(arg.get(index).iterator()));
                    moveIterators(index+1);
                }
            }
        };
    }



}
