package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.WebDriver;

/**
 * User: eoff
 * Date: 11.02.13
 */
public class AlertAcceptedMatcher extends TypeSafeMatcher<WebDriver> {
    @Override
    protected boolean matchesSafely(WebDriver item) {
        try {
            item.switchTo().alert().accept();
            return true;
        } catch (NoAlertPresentException ignored) {
            return false;
        }
    }

    @Override
    public void describeTo(Description description) {
        description.appendValue("Сообщение принято");
    }

    @Override
    protected void describeMismatchSafely(WebDriver item, Description mismatchDescription) {
        mismatchDescription.appendValue("Сообщение не принято");
    }

    public static AlertAcceptedMatcher isAlertAccepted() {
        return new AlertAcceptedMatcher();
    }
}
