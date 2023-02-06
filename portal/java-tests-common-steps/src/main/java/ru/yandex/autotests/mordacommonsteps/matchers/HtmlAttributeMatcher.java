package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.nullValue;

/**
 * User: eoff
 * Date: 08.02.13
 */
public class HtmlAttributeMatcher extends TypeSafeMatcher<HtmlElement> {
    private HtmlAttribute attribute;
    private Matcher<String> matcher;

    public HtmlAttributeMatcher(HtmlAttribute attribute, Matcher<String> matcher) {
        this.attribute = attribute;
        this.matcher = matcher;
    }

    @Override
    protected boolean matchesSafely(HtmlElement item) {
        return matcher.matches(item.getAttribute(attribute.getValue()));
    }

    @Override
    public void describeTo(Description description) {
        description.appendText(attribute.getValue()).appendText(": ").appendDescriptionOf(matcher);
    }

    @Override
    protected void describeMismatchSafely(HtmlElement item, Description mismatchDescription) {
        if (nullValue().matches(item.getAttribute(attribute.getValue()))) {
            mismatchDescription.appendText("Аттрибут ").appendValue(attribute).appendText(" отсутствует!");
        } else {
            mismatchDescription.appendText(attribute.getValue()).appendText(": \"")
                    .appendText(item.getAttribute(attribute.toString())).appendText("\"");
        }
    }

    public static HtmlAttributeMatcher hasAttribute(HtmlAttribute attribute, Matcher<String> matcher) {
        return new HtmlAttributeMatcher(attribute, matcher);
    }
}
