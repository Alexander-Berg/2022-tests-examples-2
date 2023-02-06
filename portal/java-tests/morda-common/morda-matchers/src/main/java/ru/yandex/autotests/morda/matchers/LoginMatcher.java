package ru.yandex.autotests.morda.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;

import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;

/**
 * User: eoff
 * Date: 14.02.13
 */
public class LoginMatcher extends TypeSafeMatcher<WebDriver> {

    @Override
    protected boolean matchesSafely(WebDriver item) {
        Cookie sessionId = cookieUtils(item).getCookies().stream()
                .filter(e -> "Session_id".equals(e.getName()) && item.getCurrentUrl().contains(e.getDomain()))
                .findFirst()
                .orElseGet(() -> new Cookie("Session_id",""));

        return !sessionId.getValue().startsWith("noauth");
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Авторизованный режим");
    }

    @Override
    protected void describeMismatchSafely(WebDriver item, Description mismatchDescription) {
        Cookie sessionId = cookieUtils(item).getCookies().stream()
                .filter(e -> "Session_id".equals(e.getName()) && item.getCurrentUrl().contains(e.getDomain()))
                .findFirst()
                .orElseGet(() -> new Cookie("Session_id",""));
        mismatchDescription.appendText("Неавторизованный режим. Session_id = ").appendValue(sessionId.getValue());
    }

    public static LoginMatcher isLogged() {
        return new LoginMatcher();
    }
}
