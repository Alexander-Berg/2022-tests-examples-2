package ru.yandex.autotests.mainmorda.matchers;

import ch.lambdaj.function.convert.Converter;
import ch.lambdaj.function.matcher.Predicate;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter;
import ru.yandex.autotests.mainmorda.utils.WidgetProperties;

import java.util.Map;

import static ch.lambdaj.Lambda.exists;
import static ch.lambdaj.Lambda.filter;
import static ch.lambdaj.Lambda.map;
import static org.hamcrest.Matchers.not;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 03.07.13
 * Time: 15:59
 */
public class WidgetPatternMatcher extends TypeSafeMatcher<WidgetPattern> {
    private WidgetPattern expectedWidgetPattern;
    private Predicate<Map.Entry<WidgetPatternParameter, String>> matchToExpectedParameters;


    public WidgetPatternMatcher(WidgetPattern pattern, Predicate<Map.Entry<WidgetPatternParameter, String>> matcher) {
        expectedWidgetPattern = pattern;
        this.matchToExpectedParameters = matcher;
    }

    @Factory
    public static WidgetPatternMatcher equalsToPattern(final WidgetPattern pattern) {
        return new WidgetPatternMatcher(pattern, new Predicate<Map.Entry<WidgetPatternParameter, String>>() {
            @Override
            public boolean apply(Map.Entry<WidgetPatternParameter, String> actual) {
                return actual.getValue().equals(pattern.getParameters().get(actual.getKey()));
            }
        });
    }

    @Factory
    public static WidgetPatternMatcher matchesToPattern(final WidgetPattern pattern) {
        return new WidgetPatternMatcher(pattern, new Predicate<Map.Entry<WidgetPatternParameter, String>>() {
            @Override
            public boolean apply(Map.Entry<WidgetPatternParameter, String> actual) {
                return actual.getValue().matches(pattern.getParameters().get(actual.getKey()));
            }
        });
    }

    @Override
    protected boolean matchesSafely(WidgetPattern item) {
        return widgetsMatches(item) && parametersMatches(item);
    }

    private boolean widgetsMatches(WidgetPattern item) {
        Map<String, WidgetProperties> expectedWidgets = expectedWidgetPattern.getWidgets();
        Map<String, WidgetProperties> actualWidgets = item.getWidgets();
        return hasSameItemsAsCollection(expectedWidgets.keySet()).matches(actualWidgets.keySet()) &&
                hasSameItemsAsCollection(expectedWidgets.values()).matches(actualWidgets.values());
    }

    private boolean parametersMatches(WidgetPattern item) {
        Map<WidgetPatternParameter, String> expectedParameters = expectedWidgetPattern.getParameters();
        Map<WidgetPatternParameter, String> actualParameters = item.getParameters();
        return expectedParameters.size() == actualParameters.size() &&
                !exists(actualParameters.entrySet(), not(matchToExpectedParameters));
    }

    @Override
    protected void describeMismatchSafely(WidgetPattern actualWidgetPattern, final Description mismatchDescription) {
        mismatchDescription.appendText("detected: ");
        Map<String, WidgetProperties> expectedWidgets = expectedWidgetPattern.getWidgets();
        Map<String, WidgetProperties> actualWidgets = actualWidgetPattern.getWidgets();
        hasSameItemsAsCollection(expectedWidgets.keySet())
                .describeMismatch(actualWidgets.keySet(), mismatchDescription);
        hasSameItemsAsCollection(expectedWidgets.values())
                .describeMismatch(actualWidgets.values(), mismatchDescription);

        final Map<WidgetPatternParameter, String> expectedParameters = expectedWidgetPattern.getParameters();
        final Map<WidgetPatternParameter, String> actualParameters = actualWidgetPattern.getParameters();

        hasSameItemsAsCollection(expectedParameters.keySet())
                .describeMismatch(actualParameters.keySet(), mismatchDescription);

        map(filter(not(matchToExpectedParameters), actualParameters.entrySet()),
                new Converter<Map.Entry<WidgetPatternParameter, String>, Object>() {
                    @Override
                    public Object convert(Map.Entry<WidgetPatternParameter, String> parameter) {
                        mismatchDescription.appendText("actual (")
                                .appendText(parameter.getKey().toString())
                                .appendText("=").appendText(actualParameters.get(parameter.getKey()))
                                .appendText("): expected (")
                                .appendText(parameter.getKey().toString()).appendText("=")
                                .appendText(expectedParameters.get(parameter.getKey())).appendText("); ");
                        return parameter;
                    }
                });
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Правильный паттерн");
    }
}
