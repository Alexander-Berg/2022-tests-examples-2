package ru.yandex.autotests.widgets.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.WebElement;

import static org.hamcrest.Matchers.is;

/**
 * User: ivannik
 * Date: 02.08.13
 * Time: 19:08
 * <p/>
 * This class is bounded version of {@link ru.yandex.qatools.htmlelements.matchers.common.HasTextMatcher}
 */
public class HasTextMatcher<T extends WebElement> extends TypeSafeMatcher<T> {
    private final Matcher<String> textMatcher;

    HasTextMatcher(Matcher<String> textMatcher) {
        this.textMatcher = textMatcher;
    }

    @Override
    public boolean matchesSafely(T item) {
        return textMatcher.matches(item.getText());
    }

    public void describeTo(Description description) {
        description.appendText("element text ").appendDescriptionOf(textMatcher);
    }

    @Override
    protected void describeMismatchSafely(T item, Description mismatchDescription) {
        mismatchDescription.
                appendText("text of element ").
                appendValue(item).
                appendText(" was ").
                appendValue(item.getText());
    }

    @Factory
    public static <T extends WebElement> Matcher<T> hasText(final Matcher<String> textMatcher) {
        return new HasTextMatcher<T>(textMatcher);
    }

    @Factory
    public static <T extends WebElement> Matcher<T> hasText(final String text) {
        return new HasTextMatcher<T>(is(text));
    }
}
