package ru.yandex.autotests.morda.exports.tests.checks;

import org.hamcrest.Matcher;

import java.util.function.Function;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;


/**
 * User: asamar
 * Date: 17.08.2015.
 */
public class TextLengthCheck<T> extends ExportCheck<T> {

    private TextLengthCheck(String name,
                            Function<T, String> textProvider,
                            Function<T, Matcher<Integer>> textLengthMatcherProvider) {
        super(
                format("\"%s\" length", name),
                e -> checkTextLength(textProvider.apply(e), textLengthMatcherProvider.apply(e))
        );
    }

    public static <T> TextLengthCheck<T> textLength(String name,
                                                    Function<T, String> textProvider,
                                                    Function<T, Matcher<Integer>> textLengthMatcherProvider) {
        return new TextLengthCheck<>(name, textProvider, textLengthMatcherProvider);
    }

    public static void checkTextLength(String text, Matcher<Integer> textLengthMatcher) {
        assertThat("Длина текста \"" + text + "\" неверная", text.length(), textLengthMatcher);
    }
}
