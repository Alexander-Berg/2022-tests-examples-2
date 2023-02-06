package ru.yandex.autotests.morda.utils.cookie;

import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/12/14
 */
public class WebDriverCookieUtils extends MordaCookieUtils<Cookie> {

    private WebDriver driver;

    public WebDriverCookieUtils(WebDriver driver) {
        this.driver = driver;
    }

    @Override
    public Cookie getCookieNamed(String name, String domain) {
        Optional<Cookie> result = getCookies().stream().filter(
                (cookie) -> cookie.getName().equals(name) && cookie.getDomain().equals(domain)
        ).findFirst();

        return result.isPresent()
                ? result.get()
                : null;
    }

    @Override
    public List<Cookie> getCookies() {
        return new ArrayList<>(driver.manage().getCookies());
    }

    @Override
    public void addCookie(String name, String value, String domain) {
        addCookie(new Cookie(name, value, domain, null, null));
    }

    @Override
    public void addCookie(Cookie cookie) {
        driver.manage().addCookie(cookie);
    }

    @Override
    public void deleteCookieNamed(String name) {
        driver.manage().deleteCookieNamed(name);
    }

    @Override
    public void deleteCookie(Cookie cookie) {
        driver.manage().deleteCookie(cookie);
    }

    @Override
    public void deleteAllCookies() {
        driver.manage().deleteAllCookies();
    }

    @Override
    public String getCookieValue(Cookie cookie) {
        return cookie != null ? cookie.getValue() : null;
    }
}
