package ru.yandex.autotests.mainmorda.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.JavascriptExecutor;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: ivannik
 * Date: 18.06.2014
 */
public class ElementHrefMatcher extends TypeSafeMatcher<HtmlElement> {

    private Matcher<String> hrefMatcher;
    private JavascriptExecutor driver;

    public ElementHrefMatcher(Matcher<String> hrefMatcher, JavascriptExecutor driver) {
        this.hrefMatcher = hrefMatcher;
        this.driver = driver;
    }

    public static ElementHrefMatcher hasHref(Matcher<String> hrefMatcher, JavascriptExecutor driver) {
        return new ElementHrefMatcher(hrefMatcher, driver);
    }

    @Override
    protected boolean matchesSafely(HtmlElement item) {
        return hrefMatcher.matches(
                driver.executeScript("return arguments[0].attributes[arguments[1]].value", item, "href"));
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("href: ").appendDescriptionOf(hrefMatcher);
    }

    @Override
    protected void describeMismatchSafely(HtmlElement item, Description mismatchDescription) {
        Object atr = driver.executeScript("return arguments[0].attributes[arguments[1]].value", item, "href");
        if (atr instanceof String) {
            mismatchDescription.appendText("Аттрибут <href>:'").appendText((String) atr).appendText("' неверный!");
        } else {
            mismatchDescription.appendText("Аттрибут <href> отсутствует!");
        }
    }
}
