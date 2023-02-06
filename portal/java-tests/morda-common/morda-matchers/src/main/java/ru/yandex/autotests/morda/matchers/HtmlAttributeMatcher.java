package ru.yandex.autotests.morda.matchers;

import io.qameta.htmlelements.element.HtmlElement;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

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

    public enum HtmlAttribute {
        HREF("href"),
        SRC("src"),
        TITLE("title"),
        ALT("alt"),
        VALUE("value"),
        SELECTED("selected"),
        STYLE("style"),
        CONTENT("content"),
        DATA_TYPE("data-type"),
        DATA_RELATIONSHIP("data-relationship"),
        CLASS("class"),
        WIDTH("width"),
        HEIGHT("height"),
        ID("id"),
        DATA_LOGIN("data-login"),
        ACTION("action"),
        PLACEHOLDER("placeholder"),
        DATA_ID("data-id"),
        DATA_KEY("data-key"),
        DATA_STAT_SELECT("data-stat-select"),
        DATA_STATLOG("data-statlog"),
        DATA_RUBR("data-rubr"),
        DATA_IMAGE("data-image"),
        DATA_LOGO_URL("data-logo-url"),
        CHECKED("checked"),
        ARIA_LABEL("aria-label");

        private String value;

        private HtmlAttribute(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }

        @Override
        public String toString() {
            return value;
        }
    }
}
