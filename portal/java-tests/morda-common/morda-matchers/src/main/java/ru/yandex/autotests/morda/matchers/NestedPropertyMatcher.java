package ru.yandex.autotests.morda.matchers;

import ch.lambdaj.function.argument.ArgumentConversionException;
import ch.lambdaj.function.matcher.HasNestedPropertyWithValue;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;

import static ch.lambdaj.function.argument.ArgumentsFactory.actualArgument;
import static ch.lambdaj.util.IntrospectionUtil.getPropertyValue;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 30/01/15
 */
public class NestedPropertyMatcher<T> extends HasNestedPropertyWithValue<T> {
    private String propertyName;
    private Matcher<?> matcher;
    /**
     * Creates a matcher that returns true if the value af the named property regex the given matcher
     *
     * @param propertyName The name of the property
     * @param value        The value to be mathced
     */
    public NestedPropertyMatcher(String propertyName, Matcher<?> value) {
        super(propertyName, value);
        this.propertyName = propertyName;
        this.matcher = value;
    }

    @Override
    public void describeMismatch(Object item, Description description) {
        matcher.describeMismatch(
                getPropertyValue(item, propertyName),
                description.appendText("property ").appendValue(propertyName).appendText(":    ")
        );
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("property ");
        description.appendValue(propertyName);
        description.appendText(":    ");
        description.appendDescriptionOf(matcher);
    }

    @Factory
    public static <T, E> Matcher<T> hasPropertyWithValue(E argumentOrPropertyName, Matcher<?> value) {
        try {
            return new NestedPropertyMatcher<T>(actualArgument(argumentOrPropertyName).getInkvokedPropertyName(), value);
        } catch (ArgumentConversionException e) {
            if (argumentOrPropertyName instanceof String) {
                return Matchers.hasProperty((String) argumentOrPropertyName, value);
            }
            throw new IllegalArgumentException("Illegal argumentOrPropertyName type. Expected Argument or String");
        }
    }
}
