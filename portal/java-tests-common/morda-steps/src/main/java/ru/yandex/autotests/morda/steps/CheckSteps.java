package ru.yandex.autotests.morda.steps;

import org.hamcrest.Matcher;
import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;
import static ru.yandex.qatools.htmlelements.matchers.decorators.MatcherDecoratorsBuilder.should;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 07/04/15
 */
public class CheckSteps {

    @Step("Element \"{0}\" should exist")
    public static Runnable shouldExistElement(WrapsElement element) {
        return () -> {
            assertThat(element.toString(), element,
                    should(exists()).whileWaitingUntil(timeoutHasExpired(5000L)));
        };
    }

    @Step("Should see element \"{0}\"")
    public static Runnable shouldSeeElement(WrapsElement element) {
        return () -> {
            assertThat(element.toString(), element,
                    should(exists()).whileWaitingUntil(timeoutHasExpired(5000L)));
            assertThat(element.toString(), element,
                    should(isDisplayed()).whileWaitingUntil(timeoutHasExpired(5000L)));
        };
    }

    @Step("Should not see element \"{0}\"")
    public static Runnable shouldNotSeeElement(WrapsElement element) {
        return () -> {
            if (exists().matches(element)) {
                assertThat(element.toString(), element,
                        should(not(isDisplayed())).whileWaitingUntil(timeoutHasExpired(5000L)));
            }
        };
    }

    @Step("Element \"{0}\": {1}")
    public static <T> Runnable shouldSeeElementMatchingTo(T element, Matcher<? super T> matcher) {
        return () -> {
            assertThat(element.toString(), element,
                    should(matcher).whileWaitingUntil(timeoutHasExpired(5000L)));
        };
    }

    @Step("Should see cookie \"{1}\"")
    public static Runnable shouldSeeCookie(Client client, String cookieName, String cookieDomain) {
        return () -> assertThat(cookieUtils(client).getCookieNamed(cookieName, cookieDomain), notNullValue());
    }

    public static String url(String url, String scheme) {
        if (url.startsWith("//")) {
            return scheme + ":" + url;
        }
        return url;
    }

}
