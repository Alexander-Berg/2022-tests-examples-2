package ru.yandex.metrika.segments.core.parser.filter;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import ru.yandex.metrika.segments.clickhouse.g4.AstGeneratorRandom;
import ru.yandex.metrika.segments.clickhouse.g4.Grammar;
import ru.yandex.metrika.segments.clickhouse.g4.GrammarBuilder;
import ru.yandex.metrika.segments.clickhouse.g4.GrammarNode;
import ru.yandex.metrika.segments.clickhouse.g4.Rule;
import ru.yandex.metrika.segments.clickhouse.g4.Token;

/**
 * генерирует случайные жсоны заданного размера в нужном количестве.
 * Created by orantius on 05.06.16.
 */
public class JsonGen {

    public static void main(String[] args) {
        generateTestData();
    }

    private static void generateTestData() {
        Iterable<String> phrases = getJsonStream();
        for (String phrase : phrases) {
            System.out.println("phrase = " + phrase);
        }
    }

    private static Iterable<String> getJsonStream() {
        GrammarBuilder gb = new GrammarBuilder("JSON.g4", JsonGen.class);
        Grammar grammar = gb.build();
        Rule json = grammar.getRule("value");
        Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues = lexerInfo();
        AstGeneratorRandom traceGen = new AstGeneratorRandom(grammar, tokenValues, 42);
        return traceGen.generate(json, 10, 20, 1000);
    }

    private static Map<Token, Function<List<GrammarNode>, List<String>>> lexerInfo() {
        Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues = new HashMap<>();
        tokenValues.put(new Token("STRING"),  k->Stream.of("a","b", "-1","").map(v->"\""+v+"\"").collect(Collectors.toList()));
        tokenValues.put(new Token("NUMBER"),  k->Arrays.asList("1","1.0"));

        tokenValues.put(new Token("TRUE"),  k->Collections.singletonList("true"));
        tokenValues.put(new Token("FALSE"),  k->Collections.singletonList("false"));
        tokenValues.put(new Token("NULL"),  k->Collections.singletonList("null"));

        tokenValues.put(new Token("COMMA"),  k->Collections.singletonList(","));
        tokenValues.put(new Token("COLON"),  k->Collections.singletonList(":"));
        tokenValues.put(new Token("LBRA"),  k->Collections.singletonList("["));
        tokenValues.put(new Token("RBRA"),  k->Collections.singletonList("]"));
        tokenValues.put(new Token("LCUR"),  k->Collections.singletonList("{"));
        tokenValues.put(new Token("RCUR"), k->Collections.singletonList("}"));
        return tokenValues;
    }
}
