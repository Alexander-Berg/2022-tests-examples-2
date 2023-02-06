package ru.yandex.metrika.segments.core.parser.filter;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import ru.yandex.metrika.segments.clickhouse.g4.AstGeneratorAll;
import ru.yandex.metrika.segments.clickhouse.g4.Grammar;
import ru.yandex.metrika.segments.clickhouse.g4.GrammarBuilder;
import ru.yandex.metrika.segments.clickhouse.g4.GrammarNode;
import ru.yandex.metrika.segments.clickhouse.g4.Rule;
import ru.yandex.metrika.segments.clickhouse.g4.Token;

/**
 * генератор фильтров для отправки их куда следует.
 * Created by orantius on 06.06.16.
 */
public class FiltersGen {

    public static Iterable<String> getFiltersStream() {
        GrammarBuilder gb = new GrammarBuilder("FilterBracesParser.g4", FilterParserBraces2.class);
        //GrammarBuilder gb = new GrammarBuilder("test.g4", AstGeneratorAll.class);
        Grammar grammar = gb.build();
        Rule filter = grammar.getRule("filter");
        Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues = lexerInfo();

        tokenValues.put(new Token("NUMERIC_LITERAL"), k-> Arrays.asList("1","123.123","18446744073709551615","-1"));
        tokenValues.put(new Token("STRING_LITERAL"), k->Arrays.asList("'Yes'","'0'","'abc'"));
        tokenValues.put(new Token("IDENTIFIER"), k->Arrays.asList("ym:s:visits","ym:s:gender"));
        AstGeneratorAll astGeneratorAll = new AstGeneratorAll(grammar, tokenValues);
        Iterable<String> phrases = astGeneratorAll.generate(filter, 2);
        // 2     1164886
        return phrases;
    }

    public static Map<Token, Function<List<GrammarNode>, List<String>>> lexerInfo() {
        Map<Token, Function<List<GrammarNode>, List<String>>> tokenValues = new HashMap<>();
        tokenValues.put(new Token("LPAREN"),  k->Collections.singletonList("("));
        tokenValues.put(new Token("RPAREN"),  k->Collections.singletonList(")"));
        tokenValues.put(new Token("DASH"),  k->Collections.singletonList("-"));
        tokenValues.put(new Token("PLUS"),  k->Collections.singletonList("+"));
        tokenValues.put(new Token("MUL"),  k->Collections.singletonList("*"));
        tokenValues.put(new Token("DIV"),  k->Collections.singletonList("/"));
        tokenValues.put(new Token("EQ"),  k->Collections.singletonList("=="));
        tokenValues.put(new Token("NE"),  k->Collections.singletonList("!="));
        tokenValues.put(new Token("GE"),  k->Collections.singletonList(">="));
        tokenValues.put(new Token("GT"),  k->Collections.singletonList(">"));
        tokenValues.put(new Token("LE"),  k->Collections.singletonList("<="));
        tokenValues.put(new Token("LT"),  k->Collections.singletonList("<"));
        tokenValues.put(new Token("SUB"),  k->Collections.singletonList("=@"));
        tokenValues.put(new Token("NSUB"),  k->Collections.singletonList("!@"));
        tokenValues.put(new Token("RE"),  k->Collections.singletonList("=~"));
        tokenValues.put(new Token("NRE"),  k->Collections.singletonList("!~"));
        tokenValues.put(new Token("LIKE"),  k->Collections.singletonList("=*"));
        tokenValues.put(new Token("NLIKE"),  k->Collections.singletonList("!*"));
        tokenValues.put(new Token("IS_NOT_NULL"),  k->Collections.singletonList("=n"));
        tokenValues.put(new Token("IS_NULL"),  k->Collections.singletonList("!n"));
        tokenValues.put(new Token("IN"),  k->Collections.singletonList("=."));
        tokenValues.put(new Token("NOT_IN"),  k->Collections.singletonList("!."));

        tokenValues.put(new Token("K_EQUALS"),  k->Collections.singletonList("EQUALS"));
        tokenValues.put(new Token("K_CONTAINS"),  k->Collections.singletonList("CONTAINS"));
        tokenValues.put(new Token("K_INCLUDES"),  k->Collections.singletonList("INCLUDES"));
        tokenValues.put(new Token("K_REGEXP"),  k->Collections.singletonList("REGEXP"));
        tokenValues.put(new Token("K_MATCHES"),  k->Collections.singletonList("MATCHES"));
        tokenValues.put(new Token("K_LIKE"),  k->Collections.singletonList("LIKE"));
        tokenValues.put(new Token("K_IN"),  k->Collections.singletonList("IN"));
        tokenValues.put(new Token("K_DEFINED"),  k->Collections.singletonList("DEFINED"));
        tokenValues.put(new Token("K_UNDEFINED"),  k->Collections.singletonList("UNDEFINED"));
        tokenValues.put(new Token("OK"),  k->Collections.singletonList("Λ"));
        tokenValues.put(new Token("FAIL"),  k->Collections.singletonList("Ω"));
        tokenValues.put(new Token("COMMA"),  k->Collections.singletonList(","));
        tokenValues.put(new Token("K_NOT"),  k->Collections.singletonList("not"));
        tokenValues.put(new Token("K_AND"),  k->Collections.singletonList("and"));
        tokenValues.put(new Token("K_OR"),  k->Collections.singletonList("or"));
        tokenValues.put(new Token("K_WITH"),  k->Collections.singletonList("with"));
        tokenValues.put(new Token("K_EXISTS"),  k->Collections.singletonList("exists"));
        tokenValues.put(new Token("K_ALL"),  k->Collections.singletonList("all"));
        tokenValues.put(new Token("K_NONE"),  k->Collections.singletonList("none"));
        tokenValues.put(new Token("K_USER_PATTERN"),  k->Collections.singletonList("user_pattern"));
        tokenValues.put(new Token("K_COND"),  k->Collections.singletonList("COND"));
        tokenValues.put(new Token("K_ANY"),  k->Collections.singletonList("ANY"));
        tokenValues.put(new Token("K_NEXT"),  k->Collections.singletonList("NEXT"));
        tokenValues.put(new Token("K_TIME"),  k->Collections.singletonList("time"));

        tokenValues.put(new Token("SQRT"),  k->Collections.singletonList("sqrt"));
        tokenValues.put(new Token("LOG"),  k->Collections.singletonList("log"));
        tokenValues.put(new Token("K_NULL"),  k->Collections.singletonList("null"));

        tokenValues.put(new Token("DATE"),  k->Collections.singletonList("2016-01-01"));

        tokenValues.put(new Token("K_DAYSAGO"),  k->Collections.singletonList("daysago"));
        tokenValues.put(new Token("K_TODAY"),  k->Collections.singletonList("today"));
        tokenValues.put(new Token("K_YESTERDAY"),  k->Collections.singletonList("YESTERDAY"));
        return tokenValues;
    }


}
