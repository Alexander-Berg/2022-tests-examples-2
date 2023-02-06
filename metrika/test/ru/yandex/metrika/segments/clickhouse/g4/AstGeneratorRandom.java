package ru.yandex.metrika.segments.clickhouse.g4;

import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

import com.google.common.collect.Lists;

import ru.yandex.metrika.util.collections.F;

/**
 * генерит последовательность случайных деревьев для данной грамматики.
 * в отличие от AstGeneratorAll позволяет работать с деревьями глубокой структуры без полного перебора всех деревьев,
 * что позволяет с одной стороны избежать комбинаторного взрыва, с другой - погонять систему на различных входах.
 *
 * как это работает:
 * для правила или блока случайным образом выбирается альтернатива
 * для токена случаным образом выбирается физическое воплощение
 * когда глубина стека правил становится больше depth, для раскрытия правила запускается генератор деревьев маленькой глубины, сейчас это 1, и берется случайное дерево, если такое есть.
 * Created by orantius on 06.06.16.
 */
public class AstGeneratorRandom {

    private static final String EPSILON = "";

    private final Grammar grammar;
    private final Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues;
    private final Random r;

    private final AstGeneratorAll leafGen;
    private final int leafDepth = 1; // размер деревьев которые надо генерить для

    public AstGeneratorRandom(Grammar grammar, Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues, long seed) {
        this.grammar = grammar;
        this.tokenValues = tokenValues;
        r = new Random(seed);
        leafGen = new AstGeneratorAll(grammar, tokenValues);
    }

    /**
     * @param rule аксиома, которую будем разворачивать
     * @param maxDepth глубина рекурсии по правилам
     * @param minLength минимальная длина получающейся строки. нужно чтобы убрать короткие строки, которых будет большинство. т.к. в них проще свернуть в рандоме
     * @param amount размер итерабла
     */
    public Iterable<String> generate(Rule rule, int maxDepth, int minLength, int amount) {
        return StreamSupport.stream(repeat(() -> getRandomValue(rule, maxDepth)).spliterator(), false)
                .filter(i -> i.isPresent() && i.get().length() > minLength).map(Optional::get).limit(amount).collect(Collectors.toList());
    }

    private Optional<String> getRandomValue(Rule rule, int maxDepth) {
        return getRandomValue(chooseRandom(rule.getAlternatives()), maxDepth);
    }

    private Optional<String> getRandomValue(Alternative seq, int maxDepth) {
        List<Optional<String>> map = F.map(seq.getElements(), a -> applyRandomSuffix(()->generate(a.getElement(), maxDepth), a.getSuffix(), maxDepth));
        return product2(map);
    }

    private Optional<String> generate(Element elem, int maxDepth) {
        if(elem instanceof Token) {
            List<String> strings = tokenValues.get(elem).apply(Collections.emptyList()); // TODO
            if(strings==null || strings.isEmpty()) {
                throw new IllegalStateException("no representation for token " +elem);
            }
            return Optional.of(chooseRandom(strings));
        }
        if(elem instanceof RuleRef) {
            if(maxDepth > 0) {
                return getRandomValue(grammar.getRule(((RuleRef)elem).getName()), maxDepth-1);
            } else {
                List<String> strings = Lists.newArrayList(leafGen.generate(grammar.getRule(((RuleRef) elem).getName()), leafDepth));
                if(strings.isEmpty()) {
                    return Optional.empty();
                } else {
                    return Optional.of(chooseRandom(strings));
                }
            }
        }
        if(elem instanceof Block) {
            Block block = (Block)elem;
            return chooseRandom(F.map(block.getAlternatives(), a->getRandomValue(a, maxDepth))); // возможно, тут тоже надо уменьшить maxDepth
        }
        throw new IllegalArgumentException(" unsupported type of elem "+elem);
    }

    private Optional<String> applyRandomSuffix(Supplier<Optional<String>> arg, Operator suffix, int maxDepth) {
        if(suffix == null) {
            return arg.get();
        } else if(suffix == Operator.QUESTION) {
            return chooseRandom(Optional.of(EPSILON), arg.get());
        } else if(suffix == Operator.PLUS || suffix == Operator.STAR) {
            if(maxDepth == 0) {
                return Optional.of(EPSILON);
            }
            int randomDepth = suffix == Operator.STAR?r.nextInt(maxDepth):(1+r.nextInt(maxDepth));
            if(randomDepth == 0) {
                return Optional.of(EPSILON);
            }
            List<Optional<String>> repeated = Stream.generate(arg).limit(randomDepth).collect(Collectors.toList());
            return product2(repeated);
        }
        throw new IllegalArgumentException("unsupported type of suffix "+suffix);
    }



    private Optional<String> product2(List<Optional<String>> map) {
        if(map.stream().allMatch(Optional::isPresent)) { // возвращаем что-то если ВСЕ повторы что-то вернули, без переспрашиваний
            return Optional.of(map.stream().map(Optional::get).collect(Collectors.joining(" ")));
        }
        return Optional.empty();
    }


    private <T> T chooseRandom(List<T> arg) {
        return arg.get(r.nextInt(arg.size()));
    }

    private <T> T chooseRandom(T arg, T arg2) {
        return r.nextBoolean()?arg:arg2;
    }

    private <T> Optional<T> chooseRandom2(List<Optional<T>> arg) {
        int present = 0;
        for (Optional<T> t : arg) {
            if(t.isPresent()) present++;
        }
        if(present == 0) {
            return Optional.empty();
        }
        int rand = r.nextInt(present);
        int present2 = 0;
        for (Optional<T> t : arg) {
            if(t.isPresent()) {
                if(present2 == rand) {
                    return t;
                }
                present2++;
            }
        }
        throw new IllegalArgumentException("impossible");
    }

    private <T> T chooseRandom2(T arg, T arg2) {
        return r.nextBoolean()?arg:arg2;
    }

    public <T> Iterable<T> repeat(Supplier<T> arg) {
        return new Iterable<T>() {
            @Override
            public Iterator<T> iterator() {
                return new Iterator<T>() {
                    @Override
                    public boolean hasNext() {
                        return true;
                    }

                    @Override
                    public T next() {
                        return arg.get();
                    }
                };
            }
        };

    }

}
