package ru.yandex.autotests.morda.exports.tests.checks;

import org.hamcrest.Matcher;

import java.util.function.Function;
import java.util.function.Predicate;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;

/**
 * User: asamar
 * Date: 14.08.2015.
 */
public class UrlPatternCheck<T> extends ExportCheck<T> {

    private UrlPatternCheck(String name,
                            Function<T, String> urlProvider,
                            Function<T, Matcher<String>> matcherProvider,
                            Predicate<T> condition) {
        super(
                format("\"%s\" pattern check", name),
                e -> checkUrl(urlProvider.apply(e), matcherProvider.apply(e)),
                condition
        );
    }

    public static <T> UrlPatternCheck<T> urlPattern(String name,
                                                    Function<T, String> urlProvider,
                                                    Function<T, Matcher<String>> matcherProvider) {
        return urlPattern(name, urlProvider, matcherProvider, e -> true);
    }

    public static <T> UrlPatternCheck<T> urlPattern(String name,
                                                    Function<T, String> urlProvider,
                                                    Function<T, Matcher<String>> matcherProvider,
                                                    Predicate<T> condition) {
        return new UrlPatternCheck<>(name, urlProvider, matcherProvider, condition);
    }

    public static void checkUrl(String url, Matcher<String> urlMatcher) {
        assertThat("Некорректный URL: ", url, urlMatcher);
    }
}
