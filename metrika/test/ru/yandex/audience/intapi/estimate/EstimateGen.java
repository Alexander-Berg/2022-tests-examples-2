package ru.yandex.audience.intapi.estimate;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import ru.yandex.audience.estimate.EstimateRequestParser;
import ru.yandex.metrika.segments.clickhouse.g4.AstGeneratorAll;
import ru.yandex.metrika.segments.clickhouse.g4.Grammar;
import ru.yandex.metrika.segments.clickhouse.g4.GrammarBuilder;
import ru.yandex.metrika.segments.clickhouse.g4.GrammarNode;
import ru.yandex.metrika.segments.clickhouse.g4.Rule;
import ru.yandex.metrika.segments.clickhouse.g4.Token;

/**
 * Created by orantius on 20.07.16.
 */
public class EstimateGen {


    public static Iterable<String> getFiltersStream() {
        GrammarBuilder gb = new GrammarBuilder("AudienceFilter.g4", EstimateRequestParser.class);

        Grammar grammar = gb.build();
        Rule filter = grammar.getRule("filter");
        Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues = lexerInfo();

        tokenValues.put(new Token("NUMERIC_LITERAL"), k->Arrays.asList("1985713","4000000042","1000255890","2000004255","3"));
        AstGeneratorAll astGeneratorAll = new AstGeneratorAll(grammar, tokenValues);
        Iterable<String> phrases = astGeneratorAll.generate(filter, 2);
        // 2     1164886
        return phrases;
    }

    public static Map<Token, Function<List<GrammarNode>, List<String>>> lexerInfo() {
        Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues = new HashMap<>();
        tokenValues.put(new Token("LPAREN"), k->Collections.singletonList("("));
        tokenValues.put(new Token("RPAREN"), k->Collections.singletonList(")"));
        tokenValues.put(new Token("EQUALS"), k->Collections.singletonList("=="));
        tokenValues.put(new Token("K_AND"), k->Collections.singletonList("and"));
        tokenValues.put(new Token("K_OR"), k->Collections.singletonList("or"));
        tokenValues.put(new Token("K_NOT"), k->Collections.singletonList("not"));
        tokenValues.put(new Token("K_ID"), k->Collections.singletonList("id"));
        tokenValues.put(new Token("K_DAYS"), k->Collections.singletonList("days"));
        tokenValues.put(new Token("K_INTERVAL"), k->Collections.singletonList("interval"));
        return tokenValues;
    }

}
