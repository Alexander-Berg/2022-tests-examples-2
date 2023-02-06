package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04.12.13
 */
public class DocumentLoadedMatcher extends TypeSafeMatcher<WebDriver> {
    @Override
    protected boolean matchesSafely(WebDriver item) {
        JavascriptExecutor js = (JavascriptExecutor) item;
        return (Boolean) js.executeScript(
                "if (window.jQuery) { " +
                        "    return jQuery.active == 0 && document.readyState === 'complete'" +
                        "} else {\n" +
                        "    return document.readyState === 'complete'" +
                        "}"
        );
    }

    @Override
    protected void describeMismatchSafely(WebDriver item, Description mismatchDescription) {
        mismatchDescription.appendText("Content not loaded");
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Content loaded");
    }


    public static DocumentLoadedMatcher contentLoaded() {
        return new DocumentLoadedMatcher();
    }
}
